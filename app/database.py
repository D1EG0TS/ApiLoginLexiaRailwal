import os
from sqlalchemy import create_engine
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
        # Prioridad 3: variables estándar con prefijo DB_ requeridas por el entorno
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_USER = os.getenv("DB_USER")
        DB_PASS = os.getenv("DB_PASS", "")
        DB_NAME = os.getenv("DB_NAME")

        # Si DB_HOST contiene una URL completa, úsala directamente
        if DB_HOST and (DB_HOST.startswith("mysql://") or DB_HOST.startswith("mysql+pymysql://")):
            DATABASE_URL = _normalize_mysql_url(DB_HOST)
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                future=True,
            )
        elif DB_HOST and DB_USER and DB_NAME:
            DATABASE_URL = (
                f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
            )
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                future=True,
            )
        else:
            MYSQLHOST = os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST")
            MYSQLPORT = os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT") or "3306"
            MYSQLUSER = os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER")
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
                raise RuntimeError("Falta configuración de base de datos: define 'DATABASE_URL', 'MYSQL_URL'/'MYSQL_PUBLIC_URL', variables DB_* o variables MYSQL_*")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()