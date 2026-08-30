import streamlit as st

from backend.services.auth import auth_service
from backend.utils import db
from frontend.components import branding
from frontend.components.session_state import iniciar_sesion


def render() -> None:
    branding.aplicar_estilo()

    columnas = st.columns([1, 2, 1])
    with columnas[1]:
        branding.encabezado("Control de Asistencia")

        if branding.MASCOTA_PATH.exists():
            col_mascota = st.columns([1, 1, 1])
            with col_mascota[1]:
                st.image(str(branding.MASCOTA_PATH), width=150)

        if not db.disponible():
            st.error(
                "La aplicación todavía no está conectada a la base de datos. "
                "Un administrador debe completar `.streamlit/secrets.toml` "
                "(ver `.streamlit/secrets.toml.example`) y ejecutar `python Conectar_Supabase.py`."
            )
            return

        with st.form("form_login"):
            identificador = st.text_input("Cédula o correo electrónico")
            password = st.text_input("Contraseña", type="password")
            enviar = st.form_submit_button("Ingresar", width="stretch")

        if enviar:
            if not identificador or not password:
                st.warning("Completa cédula/correo y contraseña.")
                return
            try:
                resultado = auth_service.login(identificador, password)
            except auth_service.AuthError as error:
                st.error(str(error))
                return
            iniciar_sesion(resultado)
            st.rerun()
