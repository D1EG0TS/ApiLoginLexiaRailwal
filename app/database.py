import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Prioridad 1: usar DATABASE_URL si está definido (ideal para despliegues como Railway)
DATABASE_URL = os.getenv("DATABASE_URL")
ALLOW_DB_CREATE = os.getenv("ALLOW_DB_CREATE", "true").lower() == "true"

if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        future=True,
    )
else:
    # Prioridad 2: variables estándar de MySQL en Railway
    MYSQLHOST = os.getenv("MYSQLHOST")
    MYSQLPORT = os.getenv("MYSQLPORT", "3306")
    MYSQLUSER = os.getenv("MYSQLUSER")
    MYSQLPASSWORD = os.getenv("MYSQLPASSWORD", "")
    MYSQLDATABASE = os.getenv("MYSQLDATABASE")

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
        # Prioridad 3: entorno local (XAMPP) con creación opcional de base de datos
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