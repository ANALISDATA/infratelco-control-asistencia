"""Acceso a datos de usuarios (credenciales) y su rol. Sin lógica de autenticación —
eso vive en backend/services/auth."""
from __future__ import annotations

from backend.models import Role, User
from backend.utils import db

_ROLE_CODE_BY_ID = {1: Role.ADMIN, 2: Role.EMPLOYEE}
_ROLE_ID_BY_CODE = {Role.ADMIN: 1, Role.EMPLOYEE: 2}


def _con_rol(fila: dict) -> User:
    return User.from_row(fila, role_code=_ROLE_CODE_BY_ID[fila["role_id"]])


def obtener_por_email(email: str) -> User | None:
    respuesta = db.cliente().table("users").select("*").eq("email", email.lower()).limit(1).execute()
    return _con_rol(respuesta.data[0]) if respuesta.data else None


def obtener_por_documento(document_id: str) -> User | None:
    respuesta = (
        db.cliente()
        .table("users")
        .select("*")
        .eq("login_document_id", document_id)
        .limit(1)
        .execute()
    )
    return _con_rol(respuesta.data[0]) if respuesta.data else None


def obtener_por_id(user_id: str) -> User | None:
    respuesta = db.cliente().table("users").select("*").eq("id", user_id).limit(1).execute()
    return _con_rol(respuesta.data[0]) if respuesta.data else None


def crear(
    *,
    email: str,
    password_hash: str,
    role_code: str,
    employee_id: str | None = None,
    login_document_id: str | None = None,
    must_change_password: bool = True,
) -> User:
    fila = {
        "email": email.lower(),
        "password_hash": password_hash,
        "role_id": _ROLE_ID_BY_CODE[role_code],
        "employee_id": employee_id,
        "login_document_id": login_document_id,
        "must_change_password": must_change_password,
    }
    respuesta = db.cliente().table("users").insert(fila).execute()
    return _con_rol(respuesta.data[0])


def actualizar(user_id: str, cambios: dict) -> None:
    db.cliente().table("users").update(cambios).eq("id", user_id).execute()


def registrar_intento_fallido(user_id: str, intentos: int, bloqueado_hasta=None) -> None:
    cambios = {"failed_login_attempts": intentos}
    if bloqueado_hasta is not None:
        cambios["locked_until"] = bloqueado_hasta.isoformat()
    db.cliente().table("users").update(cambios).eq("id", user_id).execute()


def registrar_login_exitoso(user_id: str, cuando) -> None:
    db.cliente().table("users").update(
        {"failed_login_attempts": 0, "locked_until": None, "last_login_at": cuando.isoformat()}
    ).eq("id", user_id).execute()
