"""Hashing de contraseñas y tokens de sesión/recuperación.

Regla dura del proyecto: nunca se guarda ni se muestra una contraseña en texto plano.
Los tokens de sesión y de recuperación tampoco se guardan en claro en la base de datos:
se guarda su hash (SHA-256) y se compara hash contra hash, igual que una contraseña.
Así, si alguien lee la base de datos, no puede reusar un token de sesión activo.
"""
from __future__ import annotations

import hashlib
import re
import secrets

import bcrypt

# bcrypt trunca (y algunas versiones directamente rechazan) contraseñas de más de 72 bytes.
# Se corta explícitamente aquí para que hash y verificación sean siempre consistentes,
# sin depender del comportamiento interno de la librería.
_MAX_BYTES_BCRYPT = 72


def _a_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:_MAX_BYTES_BCRYPT]


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_a_bytes(password), bcrypt.gensalt())
    return hashed.decode("ascii")


def verificar_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(_a_bytes(password), password_hash.encode("ascii"))
    except (ValueError, TypeError):
        return False


def validar_fortaleza(password: str) -> tuple[bool, str]:
    """Política mínima de contraseña segura. Devuelve (ok, motivo_si_falla)."""
    from backend import config

    if len(password) < config.MIN_PASSWORD_LENGTH:
        return False, f"La contraseña debe tener al menos {config.MIN_PASSWORD_LENGTH} caracteres."
    if not re.search(r"[A-Za-z]", password):
        return False, "La contraseña debe incluir al menos una letra."
    if not re.search(r"[0-9]", password):
        return False, "La contraseña debe incluir al menos un número."
    return True, ""


def generar_token() -> tuple[str, str]:
    """Genera un token aleatorio para sesión/recuperación.

    Devuelve (token_para_el_usuario, hash_para_guardar_en_bd).
    """
    token = secrets.token_urlsafe(32)
    return token, hash_token(token)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
