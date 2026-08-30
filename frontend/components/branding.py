"""Identidad visual de INFRATELCO. Los colores fueron tomados por muestreo de píxeles
directamente del logo real en assets/logos/infratelco_logo.png (no inventados)."""
from pathlib import Path
from urllib.parse import quote

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

# Patrón de "pistas de circuito" (PCB) muy tenue para el fondo de la barra lateral —
# evoca ingeniería eléctrica sin distraer del contenido. Trazos + pads a bajo alfa.
_SVG_CIRCUITO = """
<svg xmlns="http://www.w3.org/2000/svg" width="140" height="140">
  <g fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="1.5">
    <path d="M0 30 H40 V70 H90 V30 H140" />
    <path d="M20 140 V100 H60 V60" />
    <path d="M140 90 H100 V120 H70" />
  </g>
  <g fill="rgba(255,255,255,0.10)">
    <circle cx="40" cy="30" r="3" />
    <circle cx="90" cy="70" r="3" />
    <circle cx="60" cy="60" r="3" />
    <circle cx="100" cy="90" r="3" />
    <circle cx="70" cy="120" r="3" />
  </g>
</svg>
""".strip()
_SVG_CIRCUITO_URI = "data:image/svg+xml," + quote(_SVG_CIRCUITO)

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
    background-image:
        radial-gradient(circle at 15% 0%, rgba(0,124,208,0.35) 0%, transparent 55%),
        url("{_SVG_CIRCUITO_URI}");
    background-repeat: no-repeat, repeat;
    background-size: auto, 140px 140px;
}}
[data-testid="stSidebar"] * {{
    color: {BLANCO} !important;
}}

/* Menú de navegación (st.navigation) -- botones tipo "pill", más pro */
[data-testid="stSidebarNav"] {{
    padding-top: 0.5rem;
}}
[data-testid="stSidebarNavLink"] {{
    border-radius: 10px;
    margin: 0.15rem 0.4rem;
    padding: 0.55rem 0.85rem !important;
    font-weight: 600;
    letter-spacing: 0.01em;
    transition: background-color 0.15s ease, transform 0.15s ease;
}}
[data-testid="stSidebarNavLink"]:hover {{
    background-color: rgba(255,255,255,0.10);
    transform: translateX(2px);
}}
[data-testid="stSidebarNavLink"][aria-current="page"] {{
    background: linear-gradient(90deg, rgba(254,207,3,0.22) 0%, rgba(254,207,3,0.06) 100%);
    border-left: 3px solid {DORADO};
    padding-left: calc(0.85rem - 3px) !important;
}}
[data-testid="stSidebarNavSeparator"] {{
    border-color: rgba(255,255,255,0.15) !important;
}}

div.stButton > button, div.stFormSubmitButton > button {{
    background-color: {AZUL_OSCURO};
    color: {BLANCO};
    border: none;
    border-radius: 8px;
    font-weight: 700;
    letter-spacing: 0.02em;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
    background-color: {AZUL};
    color: {BLANCO};
    transform: translateY(-1px);
    box-shadow: 0 8px 16px -6px rgba(0,124,208,0.5);
}}
[data-testid="stSidebar"] div.stButton > button {{
    background-color: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.25);
}}
[data-testid="stSidebar"] div.stButton > button:hover {{
    background-color: rgba(255,255,255,0.18);
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
