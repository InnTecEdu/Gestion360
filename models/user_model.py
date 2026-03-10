from __future__ import annotations

from typing import Any

from sqlalchemy import select

from infrastructure import db
from models.entities import Usuario


def _user_to_dict(user: Usuario) -> dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "password": user.password,
        "rol": user.rol,
        "foto": user.foto,
        "fecha_creacion": user.fecha_creacion,
    }


def get_user_by_username(username: str) -> dict[str, Any] | None:
    query = select(Usuario).where(Usuario.username == username)
    user = db.session.execute(query).scalar_one_or_none()
    return _user_to_dict(user) if user else None


def get_user_by_id(user_id: int | str) -> dict[str, Any] | None:
    query = select(Usuario).where(Usuario.id == int(user_id))
    user = db.session.execute(query).scalar_one_or_none()
    return _user_to_dict(user) if user else None


def list_users() -> list[dict[str, Any]]:
    query = select(Usuario).order_by(Usuario.id.asc())
    rows = db.session.execute(query).scalars().all()
    return [_user_to_dict(row) for row in rows]


def insert_user(username: str, password_hash: str, rol: str, foto_key: str) -> None:
    user = Usuario()
    user.username = username
    user.password = password_hash
    user.rol = rol
    user.foto = foto_key
    db.session.add(user)
    db.session.commit()


def update_user(user_id: int, username: str, rol: str) -> None:
    user = db.session.get(Usuario, user_id)
    if not user:
        raise ValueError(f"Usuario no existe: {user_id}")

    user.username = username
    user.rol = rol
    db.session.commit()


def delete_user(user_id: int) -> None:
    user = db.session.get(Usuario, user_id)
    if not user:
        return

    db.session.delete(user)
    db.session.commit()
