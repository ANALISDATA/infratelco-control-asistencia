import streamlit as st

from backend.models import User
from backend.services.auth import auth_service
from frontend.components import branding


def render(usuario: User) -> None:
    branding.aplicar_estilo()
    columnas = st.columns([1, 2, 1])
    with columnas[1]:
        branding.encabezado("Cambio de contraseña obligatorio")
        st.info("Es tu primer ingreso (o un administrador restableció tu clave). Debes elegir una contraseña nueva antes de continuar.")

        with st.form("form_primer_acceso"):
            actual = st.text_input("Contraseña actual / temporal", type="password")
            nueva = st.text_input("Nueva contraseña", type="password")
            confirmar = st.text_input("Confirmar nueva contraseña", type="password")
            enviar = st.form_submit_button("Guardar y continuar", width="stretch")

        if enviar:
            if nueva != confirmar:
                st.error("Las contraseñas nuevas no coinciden.")
                return
            try:
                auth_service.cambiar_password(usuario, actual, nueva)
            except auth_service.AuthError as error:
                st.error(str(error))
                return
            st.success("Contraseña actualizada. Ya puedes continuar.")
            st.rerun()
