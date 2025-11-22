from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models, schemas, crud
from .security import create_access_token, verify_password
from . import security
from .deps import get_current_user, get_current_admin
import os
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import logging

Base.metadata.create_all(bind=engine)

env_value = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("ENV") or os.getenv("ENVIRONMENT")
is_prod = str(env_value).lower() in {"prod", "production"}
enable_docs = os.getenv("ENABLE_DOCS", "false").lower() == "true"
app = FastAPI(
    title="API Login con Roles",
    docs_url="/docs" if (not is_prod or enable_docs) else None,
    redoc_url="/redoc" if (not is_prod or enable_docs) else None,
)
logger = logging.getLogger("uvicorn")

@app.on_event("startup")
def _log_routes():
    try:
        paths = [getattr(r, "path", None) for r in app.routes]
        logger.info({"routes": paths, "pwd_scheme": getattr(security.pwd_context, "default_scheme", lambda: None)()})
    except Exception:
        pass
if is_prod:
    origins_env = os.getenv("CORS_ORIGINS", "")
    if origins_env:
        origins = [o.strip().rstrip("/") for o in origins_env.split(",") if o.strip()]
    else:
        origins = ["https://lexiarailway-production.up.railway.app"]
else:
    origins = [
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://192.168.1.108:8081",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["meta"])
def root():
    return {
        "status": "ok",
        "service": "API Login con Roles",
        "docs": "/docs" if (not is_prod or enable_docs) else None,
    }

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Verificar si existe
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya está registrado")
    role = models.UserRole(user_in.role)
    try:
        user = crud.create_user(db, email=user_in.email, full_name=user_in.full_name, password=user_in.password, role=role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/admin/users", response_model=List[schemas.UserOut])
def admin_list_users(
    q: Optional[str] = None,
    full_name: Optional[str] = None,
    role: Optional[models.UserRole] = None,
    limit: int = 50,
    offset: int = 0,
    sortBy: Optional[str] = None,
    sortOrder: str = "asc",
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    return crud.list_users(db, q=q, full_name=full_name, role=role, limit=limit, offset=offset, sort_by=sortBy, sort_order=sortOrder)

@app.get("/admin/users/paged", response_model=schemas.UsersPaged)
def admin_list_users_paged(
    q: Optional[str] = None,
    full_name: Optional[str] = None,
    role: Optional[models.UserRole] = None,
    limit: int = 50,
    offset: int = 0,
    sortBy: Optional[str] = None,
    sortOrder: str = "asc",
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    items = crud.list_users(db, q=q, full_name=full_name, role=role, limit=limit, offset=offset, sort_by=sortBy, sort_order=sortOrder)
    total = crud.count_users(db, q=q, full_name=full_name, role=role)
    return {"items": items, "total": total}

@app.post("/admin/users", response_model=schemas.UserOut)
def admin_create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db), _: models.User = Depends(get_current_admin)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya está registrado")
    role = models.UserRole(user_in.role)
    user = crud.create_user(db, email=user_in.email, full_name=user_in.full_name, password=user_in.password, role=role)
    return user

@app.get("/admin/users/{user_id}", response_model=schemas.UserOut)
def admin_get_user(user_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_admin)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@app.put("/admin/users/{user_id}", response_model=schemas.UserOut)
def admin_update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    try:
        updated = crud.update_user(
            db,
            user,
            email=user_in.email,
            full_name=user_in.full_name,
            password=user_in.password,
            role=models.UserRole(user_in.role) if user_in.role is not None else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated


@app.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_admin)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    crud.delete_user(db, user)
    return {"detail": "Usuario eliminado"}