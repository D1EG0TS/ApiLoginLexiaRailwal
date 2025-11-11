from sqlalchemy.orm import Session
from sqlalchemy import select, func
from . import models
from .security import get_password_hash
from typing import Optional


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.execute(select(models.User).where(models.User.email == email)).scalar_one_or_none()


def create_user(db: Session, email: str, full_name: str, password: str, role: models.UserRole = models.UserRole.user) -> models.User:
    user = models.User(
        email=email,
        full_name=full_name,
        password_hash=get_password_hash(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users(
    db: Session,
    q: Optional[str] = None,
    full_name: Optional[str] = None,
    role: Optional[models.UserRole] = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
):
    # Filtros
    stmt = select(models.User)
    if q:
        stmt = stmt.where(models.User.email.like(f"%{q}%"))
    if full_name:
        stmt = stmt.where(models.User.full_name.like(f"%{full_name}%"))
    if role is not None:
        stmt = stmt.where(models.User.role == role)

    # Ordenamiento
    sort_map = {
        "id": models.User.id,
        "email": models.User.email,
        "full_name": models.User.full_name,
        "role": models.User.role,
    }
    sort_key = sort_map.get((sort_by or "id").lower(), models.User.id)
    order_expr = sort_key.asc() if sort_order.lower() == "asc" else sort_key.desc()
    stmt = stmt.order_by(order_expr)

    # Paginación
    stmt = stmt.offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()


def count_users(db: Session, q: Optional[str] = None, full_name: Optional[str] = None, role: Optional[models.UserRole] = None) -> int:
    stmt = select(func.count(models.User.id))
    if q:
        stmt = stmt.where(models.User.email.like(f"%{q}%"))
    if full_name:
        stmt = stmt.where(models.User.full_name.like(f"%{full_name}%"))
    if role is not None:
        stmt = stmt.where(models.User.role == role)
    return db.execute(stmt).scalar_one()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.execute(select(models.User).where(models.User.id == user_id)).scalar_one_or_none()


def update_user(
    db: Session,
    user: models.User,
    *,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    password: Optional[str] = None,
    role: Optional[models.UserRole] = None,
) -> models.User:
    if email and email != user.email:
        # Verificar conflicto de email
        existing = db.execute(select(models.User).where(models.User.email == email)).scalar_one_or_none()
        if existing:
            raise ValueError("El correo ya está registrado")
        user.email = email
    if full_name is not None:
        user.full_name = full_name
    if password:
        user.password_hash = get_password_hash(password)
    if role is not None:
        user.role = role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: models.User) -> None:
    db.delete(user)
    db.commit()