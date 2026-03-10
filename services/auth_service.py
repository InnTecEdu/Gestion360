from __future__ import annotations

from types import SimpleNamespace
from typing import Any


def build_login_user(user_data: dict[str, Any]) -> SimpleNamespace:
    user_id = str(user_data["id"])
    user = SimpleNamespace(
        id=user_id,
        username=user_data["username"],
        rol=user_data["rol"],
        is_active=True,
        is_authenticated=True,
        is_anonymous=False,
    )

    def get_id() -> str:
        return user_id

    user.get_id = get_id
    return user


def is_admin(user: Any) -> bool:
    return bool(getattr(user, "rol", "") == "admin")
