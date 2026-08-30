"""Envoltorio sobre st.session_state + una cookie de navegador para la sesión de login.

st.session_state por sí solo vive mientras dura la conexión del navegador con el
servidor Streamlit: si el usuario cierra la pestaña o recarga, se pierde. Para que un
empleado no tenga que iniciar sesión cada día desde el celular en obra, el token de
sesión también se guarda en una cookie del navegador (streamlit_cookies_controller) con
una duración larga para empleados y corta para administradores — ver
backend/config.py (SESSION_TTL_HOURS_EMPLOYEE / _ADMIN).

La cookie por sí sola no basta para entrar: el token todavía se valida contra la tabla
`sessions` en cada carga (auth_service.validar_sesion), así que cerrar sesión desde otro
lado, o que el token expire, la invalida igual aunque la cookie siga en el navegador.
"""
from __future__ import annotations

import streamlit as st
from streamlit_cookies_controller import CookieController

from backend.models import User
from backend.services.auth import auth_service

NOMBRE_COOKIE = "infratelco_session"
_CLAVE_CONTROLADOR = "_cookie_controller"


def _controlador() -> CookieController:
    # CookieController() escribe en st.session_state al crearse (para el widget que lo
    # respalda); crearlo dos veces en el mismo rerun revienta con
    # "cannot be modified after the widget... is instantiated". Se cachea una sola
    # instancia por rerun.
    if _CLAVE_CONTROLADOR not in st.session_state:
        st.session_state[_CLAVE_CONTROLADOR] = CookieController()
    return st.session_state[_CLAVE_CONTROLADOR]


def usuario_actual() -> User | None:
    token = st.session_state.get("session_token")

    if not token:
        # No hay token en esta sesión de navegador todavía: puede que sí exista una
        # cookie de una visita anterior (celular del empleado, por ejemplo).
        token = _controlador().get(NOMBRE_COOKIE)

    if not token:
        return None

    usuario = auth_service.validar_sesion(token)
    if usuario is None:
        # El token de la cookie ya no es válido (expiró o se cerró sesión en otro lado).
        st.session_state.pop("session_token", None)
        _controlador().remove(NOMBRE_COOKIE)
        return None

    # Válido: se deja en session_state para no tener que releer la cookie en cada rerun.
    st.session_state["session_token"] = token
    st.session_state["user_id"] = usuario.id
    return usuario


def iniciar_sesion(resultado: auth_service.ResultadoLogin) -> None:
    st.session_state["session_token"] = resultado.session_token
    st.session_state["user_id"] = resultado.user.id
    _controlador().set(
        NOMBRE_COOKIE,
        resultado.session_token,
        max_age=resultado.session_ttl_hours * 3600,
        same_site="strict",
    )


def cerrar_sesion() -> None:
    token = st.session_state.get("session_token")
    if token:
        auth_service.cerrar_sesion(token)
    for clave in ("session_token", "user_id"):
        st.session_state.pop(clave, None)
    _controlador().remove(NOMBRE_COOKIE)
