import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Helpers
def _normalize_mysql_url(url: str) -> str:
    """Ensure SQLAlchemy URL uses PyMySQL driver and utf8mb4 charset without exposing secrets."""
    if not url:
        return url
    # Convert scheme to mysql+pymysql
    if url.startswith("mysql://"):
        url = "mysql+pymysql://" + url[len("mysql://"):]
    # Ensure charset param present
    if "charset=utf8mb4" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}charset=utf8mb4"
    return url

# Prioridad 1: usar DATABASE_URL si está definido (ideal para despliegues como Railway)
DATABASE_URL = os.getenv("DATABASE_URL")
ALLOW_DB_CREATE = os.getenv("ALLOW_DB_CREATE", "true").lower() == "true"

if DATABASE_URL:
    DATABASE_URL = _normalize_mysql_url(DATABASE_URL)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        future=True,
    )
else:
    # Prioridad 2: URLs directas de Railway (interno y público)
    MYSQL_URL = os.getenv("MYSQL_URL")  # e.g. mysql://root:pass@mysql.railway.internal:3306/railway
    MYSQL_PUBLIC_URL = os.getenv("MYSQL_PUBLIC_URL")

    if MYSQL_URL or MYSQL_PUBLIC_URL:
        DATABASE_URL = _normalize_mysql_url(MYSQL_URL or MYSQL_PUBLIC_URL)
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            future=True,
        )
    else:
        # Prioridad 3: variables estándar de MySQL (con y sin guión bajo)
        MYSQLHOST = os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST")
        MYSQLPORT = os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT") or "3306"
        MYSQLUSER = os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER")
        # Permite usar MYSQLPASSWORD, MYSQL_PASSWORD o MYSQL_ROOT_PASSWORD
        MYSQLPASSWORD = (
            os.getenv("MYSQLPASSWORD")
            or os.getenv("MYSQL_PASSWORD")
            or os.getenv("MYSQL_ROOT_PASSWORD")
            or ""
        )
        MYSQLDATABASE = os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE")

        if MYSQLHOST and MYSQLUSER and MYSQLDATABASE:
            DATABASE_URL = (
                f"mysql+pymysql://{MYSQLUSER}:{MYSQLPASSWORD}@{MYSQLHOST}:{MYSQLPORT}/{MYSQLDATABASE}?charset=utf8mb4"
            )
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                future=True,
            )
        else:
            # Prioridad 4: entorno local (XAMPP) con creación opcional de base de datos
            DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
            DB_PORT = os.getenv("DB_PORT", "3306")
            DB_USER = os.getenv("DB_USER", "root")  # por defecto en XAMPP
            DB_PASS = os.getenv("DB_PASS", "")       # vacío por defecto en XAMPP
            DB_NAME = os.getenv("DB_NAME", "login_api")

            # Crear base de datos solo si está permitido (evitar en producción como Railway)
            if ALLOW_DB_CREATE:
                SERVER_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/?charset=utf8mb4"
                server_engine = create_engine(
                    SERVER_DATABASE_URL,
                    pool_pre_ping=True,
                    future=True,
                )
                with server_engine.connect() as conn:
                    conn.execute(text(
                        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    ))
                    conn.commit()

            # Conectar a la base ya existente
            DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                future=True,
            )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()