"""Autenticación: login (cédula o correo), bloqueo por intentos fallidos, sesiones con
expiración, cambio de contraseña obligatorio en primer acceso, y reseteo administrativo.

Todas las reglas de seguridad (máximo de intentos, minutos de bloqueo, duración de sesión)
salen de backend/config.py — nunca hay un número mágico aquí.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from backend import config
from backend.models import Role, User
from backend.repositories import session_repository, user_repository
from backend.services.audit import audit_service
from backend.utils import security
from backend.utils.timezone import ahora


class AuthError(Exception):
    """Error de autenticación con mensaje seguro para mostrar al usuario
    (nunca revela si fue la cédula/correo o la contraseña lo que falló)."""


MENSAJE_CREDENCIALES_INVALIDAS = "Cédula/correo o contraseña incorrectos."


@dataclass
class ResultadoLogin:
    user: User
    session_token: str
    session_ttl_hours: int


def _ttl_horas(role_code: str) -> int:
    return config.SESSION_TTL_HOURS_ADMIN if role_code == Role.ADMIN else config.SESSION_TTL_HOURS_EMPLOYEE


def _es_correo(identificador: str) -> bool:
    return "@" in identificador


def _usuario_por_identificador(identificador: str) -> User | None:
    identificador = identificador.strip()
    if _es_correo(identificador):
        return user_repository.obtener_por_email(identificador)
    return user_repository.obtener_por_documento(identificador)


def login(identificador: str, password: str, ip_address: str | None = None,
          user_agent: str | None = None) -> ResultadoLogin:
    usuario = _usuario_por_identificador(identificador)

    # Mismo mensaje de error exista o no el usuario: no se revela cuál dato fue el incorrecto.
    if usuario is None:
        raise AuthError(MENSAJE_CREDENCIALES_INVALIDAS)

    if not usuario.is_active:
        raise AuthError("Tu usuario está desactivado. Contacta al administrador.")

    momento = ahora()
    if usuario.locked_until and usuario.locked_until > momento:
        minutos = max(1, int((usuario.locked_until - momento).total_seconds() // 60) + 1)
        raise AuthError(
            f"Cuenta bloqueada por demasiados intentos fallidos. Intenta de nuevo en {minutos} minuto(s)."
        )

    if not security.verificar_password(password, usuario.password_hash):
        intentos = usuario.failed_login_attempts + 1
        bloqueado_hasta = None
        if intentos >= config.MAX_FAILED_LOGIN_ATTEMPTS:
            bloqueado_hasta = momento + timedelta(minutes=config.LOGIN_LOCKOUT_MINUTES)
        user_repository.registrar_intento_fallido(usuario.id, intentos, bloqueado_hasta)
        audit_service.registrar(
            None, "auth.login_failed", "user", usuario.id,
            reason=f"Intento {intentos}/{config.MAX_FAILED_LOGIN_ATTEMPTS}", ip_address=ip_address,
        )
        raise AuthError(MENSAJE_CREDENCIALES_INVALIDAS)

    user_repository.registrar_login_exitoso(usuario.id, momento)

    token, token_hash = security.generar_token()
    ttl_horas = _ttl_horas(usuario.role_code)
    expira = momento + timedelta(hours=ttl_horas)
    session_repository.crear(usuario.id, token_hash, expira, ip_address, user_agent)

    audit_service.registrar(usuario, "auth.login_success", "user", usuario.id, ip_address=ip_address)

    usuario.failed_login_attempts = 0
    usuario.locked_until = None
    return ResultadoLogin(user=usuario, session_token=token, session_ttl_hours=ttl_horas)


def validar_sesion(session_token: str) -> User | None:
    if not session_token:
        return None
    token_hash = security.hash_token(session_token)
    sesion = session_repository.obtener_valida(token_hash, ahora())
    if not sesion:
        return None
    return user_repository.obtener_por_id(sesion["user_id"])


def cerrar_sesion(session_token: str) -> None:
    if not session_token:
        return
    session_repository.revocar(security.hash_token(session_token), ahora())


def cambiar_password(usuario: User, password_actual: str, password_nueva: str) -> None:
    if not security.verificar_password(password_actual, usuario.password_hash):
        raise AuthError("La contraseña actual no es correcta.")
    _establecer_password(usuario, password_nueva)


def _establecer_password(usuario: User, password_nueva: str) -> None:
    ok, motivo = security.validar_fortaleza(password_nueva)
    if not ok:
        raise AuthError(motivo)
    nuevo_hash = security.hash_password(password_nueva)
    user_repository.actualizar(
        usuario.id, {"password_hash": nuevo_hash, "must_change_password": False}
    )
    audit_service.registrar(usuario, "auth.password_changed", "user", usuario.id)


def restablecer_password_administrador(admin: User, usuario_objetivo: User, password_temporal: str) -> None:
    """Un administrador asigna una contraseña temporal a otro usuario (por ejemplo,
    porque el empleado olvidó la suya y todavía no hay proveedor de email conectado —
    ver documentation/technical-decisions.md, límite de notificaciones).
    Fuerza cambio de contraseña en el siguiente ingreso."""
    ok, motivo = security.validar_fortaleza(password_temporal)
    if not ok:
        raise AuthError(motivo)
    nuevo_hash = security.hash_password(password_temporal)
    user_repository.actualizar(
        usuario_objetivo.id,
        {"password_hash": nuevo_hash, "must_change_password": True, "failed_login_attempts": 0,
         "locked_until": None},
    )
    audit_service.registrar(
        admin, "auth.password_reset_by_admin", "user", usuario_objetivo.id,
        reason=f"Restablecida por {admin.email}",
    )
