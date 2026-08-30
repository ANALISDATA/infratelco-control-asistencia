"""Envoltorio delgado sobre st.session_state para la sesión de login.

Limitación conocida (documentada en documentation/security.md): st.session_state vive
mientras dura la conexión del navegador con el servidor Streamlit. Si el usuario cierra
la pestaña o recarga con F5, debe iniciar sesión de nuevo — no hay todavía una cookie
persistente. Es una limitación aceptada para la Fase 1, no un descuido.
"""
from __future__ import annotations

import streamlit as st

from backend.models import User
from backend.services.auth import auth_service


def usuario_actual() -> User | None:
    token = st.session_state.get("session_token")
    if not token:
        return None
    usuario = auth_service.validar_sesion(token)
    if usuario is None:
        st.session_state.pop("session_token", None)
    return usuario


def iniciar_sesion(user: User, session_token: str) -> None:
    st.session_state["session_token"] = session_token
    st.session_state["user_id"] = user.id


def cerrar_sesion() -> None:
    token = st.session_state.get("session_token")
    if token:
        auth_service.cerrar_sesion(token)
    for clave in ("session_token", "user_id"):
        st.session_state.pop(clave, None)
