import streamlit as st

from backend.services.auth import auth_service
from backend.utils import db
from frontend.components import branding
from frontend.components.session_state import iniciar_sesion

_CSS_LOGIN = f"""
<style>
.stApp {{
    background: radial-gradient(circle at 20% 15%, #003C9E 0%, {branding.AZUL_OSCURO} 45%, #00133F 100%) !important;
}}
[data-testid="stHeader"] {{ background: transparent !important; }}

.st-key-login_card {{
    background: #FFFFFF;
    border-radius: 20px;
    padding: 2.75rem 2.5rem 2.25rem 2.5rem;
    box-shadow: 0 25px 60px -12px rgba(0, 10, 40, 0.55), 0 0 0 1px rgba(255,255,255,0.06);
    position: relative;
    overflow: hidden;
}}
.st-key-login_card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 6px;
    background: linear-gradient(90deg, {branding.AZUL_OSCURO} 0%, {branding.AZUL} 45%, {branding.DORADO} 75%, {branding.VERDE} 100%);
}}

.login-marca {{
    text-align: center;
    color: {branding.AZUL_OSCURO};
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-size: 0.8rem;
    margin-top: 0.75rem;
}}
.login-tagline {{
    text-align: center;
    color: #6B7280;
    font-size: 0.78rem;
    letter-spacing: 0.03em;
    margin-bottom: 0.4rem;
}}
.login-titulo {{
    text-align: center;
    color: #14213D;
    font-size: 1.7rem;
    font-weight: 800;
    margin: 0.15rem 0 1.5rem 0;
}}

.st-key-login_card [data-testid="stImage"] img {{
    border-radius: 14px;
    box-shadow: 0 12px 28px -8px rgba(0,34,110,0.35);
}}

.st-key-login_card div[data-testid="stTextInput"] input {{
    border-radius: 10px;
    border: 1.5px solid #E2E5EC;
    padding: 0.65rem 0.9rem;
}}
.st-key-login_card div[data-testid="stTextInput"] input:focus {{
    border-color: {branding.AZUL};
    box-shadow: 0 0 0 3px rgba(0,124,208,0.18);
}}

.st-key-login_card div.stFormSubmitButton > button {{
    background: linear-gradient(90deg, {branding.AZUL_OSCURO} 0%, {branding.AZUL} 100%);
    border-radius: 10px;
    padding: 0.7rem 0;
    font-weight: 700;
    letter-spacing: 0.03em;
    border: none;
    box-shadow: 0 10px 20px -6px rgba(0,124,208,0.5);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.st-key-login_card div.stFormSubmitButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 14px 26px -6px rgba(0,124,208,0.6);
}}

.login-footer {{
    text-align: center;
    color: rgba(255,255,255,0.65);
    font-size: 0.78rem;
    margin-top: 1.5rem;
    letter-spacing: 0.02em;
}}
</style>
"""


def render() -> None:
    st.markdown(_CSS_LOGIN, unsafe_allow_html=True)

    columnas = st.columns([1, 1.3, 1])
    with columnas[1]:
        st.write("")
        with st.container(key="login_card"):
            if branding.MASCOTA_PATH.exists():
                col_m = st.columns([1, 1.3, 1])
                with col_m[1]:
                    st.image(str(branding.MASCOTA_PATH), width=210)

            st.markdown('<div class="login-marca">INFRATELCO</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="login-tagline">Ingeniería Eléctrica e Infraestructura</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="login-titulo">Control de Asistencia</div>', unsafe_allow_html=True)

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

        st.markdown(
            '<div class="login-footer">Sistema interno de control de asistencia — acceso restringido</div>',
            unsafe_allow_html=True,
        )
