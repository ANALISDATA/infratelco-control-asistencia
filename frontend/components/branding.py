"""Identidad visual de INFRATELCO. Los colores fueron tomados por muestreo de píxeles
directamente del logo real en assets/logos/infratelco_logo.png (no inventados)."""
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent.parent
LOGO_PATH = RAIZ / "assets" / "logos" / "infratelco_logo.png"
MASCOTA_PATH = RAIZ / "assets" / "images" / "mascota_infratelco.png"

AZUL_OSCURO = "#00226E"
AZUL = "#007CD0"
VERDE = "#92BD29"
DORADO = "#FECF03"
GRIS_OSCURO = "#1A1A1A"
BLANCO = "#FFFFFF"

CSS = f"""
<style>
:root {{
    --infratelco-azul-oscuro: {AZUL_OSCURO};
    --infratelco-azul: {AZUL};
    --infratelco-verde: {VERDE};
    --infratelco-dorado: {DORADO};
}}
.stApp {{
    background-color: #F4F6FA;
}}
[data-testid="stSidebar"] {{
    background-color: {AZUL_OSCURO};
}}
[data-testid="stSidebar"] * {{
    color: {BLANCO} !important;
}}
div.stButton > button, div.stFormSubmitButton > button {{
    background-color: {AZUL_OSCURO};
    color: {BLANCO};
    border: none;
    border-radius: 6px;
    font-weight: 600;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
    background-color: {AZUL};
    color: {BLANCO};
}}
.infratelco-brandbar {{
    border-bottom: 4px solid {DORADO};
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}}
.infratelco-tag {{
    color: {AZUL_OSCURO};
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    font-size: 0.85rem;
}}
</style>
"""


def aplicar_estilo() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(subtitulo: str | None = None) -> None:
    st.markdown('<div class="infratelco-brandbar">', unsafe_allow_html=True)
    columnas = st.columns([1, 4])
    with columnas[0]:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width="stretch")
    with columnas[1]:
        st.markdown(
            '<div class="infratelco-tag">Ingeniería Eléctrica e Infraestructura</div>',
            unsafe_allow_html=True,
        )
        if subtitulo:
            st.subheader(subtitulo)
    st.markdown("</div>", unsafe_allow_html=True)
