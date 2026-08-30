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
    padding-top: 0.5rem !important;
}}
[data-testid="stSidebarNavLink"] {{
    border-radius: 10px !important;
    margin: 0.15rem 0.6rem !important;
    padding: 0.6rem 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em;
    background-color: transparent !important;
    transition: background-color 0.15s ease, transform 0.15s ease;
}}
[data-testid="stSidebarNavLink"]:hover {{
    background-color: rgba(255,255,255,0.12) !important;
    transform: translateX(2px);
}}
[data-testid="stSidebarNavLink"][aria-current="page"] {{
    background: linear-gradient(90deg, rgba(254,207,3,0.28) 0%, rgba(254,207,3,0.05) 100%) !important;
    border-left: 3px solid {DORADO} !important;
    padding-left: calc(0.9rem - 3px) !important;
}}
[data-testid="stSidebarNavSeparator"] {{
    border-color: rgba(255,255,255,0.15) !important;
}}

div.stButton > button, div.stFormSubmitButton > button {{
    background-color: {AZUL_OSCURO} !important;
    color: {BLANCO} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
    background-color: {AZUL} !important;
    color: {BLANCO} !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 16px -6px rgba(0,124,208,0.5);
}}
[data-testid="stSidebar"] div.stButton > button {{
    background-color: rgba(255,255,255,0.10) !important;
    border: 1.5px solid rgba(255,255,255,0.35) !important;
    padding: 0.55rem 0 !important;
}}
[data-testid="stSidebar"] div.stButton > button:hover {{
    background-color: rgba(255,255,255,0.22) !important;
    border-color: {DORADO} !important;
}}

/* Tarjeta del logo en la barra lateral -- evita que la imagen quede como un
   rectángulo blanco pegado directo contra el azul. */
[data-testid="stSidebar"] [data-testid="stImage"] {{
    background: {BLANCO};
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin: 1.25rem 0.6rem 0.75rem 0.6rem;
    box-shadow: 0 10px 24px -8px rgba(0,0,0,0.35);
}}

/* Chip de sesión (correo + rol) */
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
    padding: 0 0.6rem;
}}
[data-testid="stSidebar"] div.stButton {{
    padding: 0 0.6rem;
    margin-top: 0.5rem;
}}
/* Tarjetas de métricas (st.metric) -- fondo, sombra y acento de color */
[data-testid="stMetric"] {{
    background: {BLANCO};
    border-radius: 14px;
    padding: 1.1rem 1.25rem 1rem 1.25rem;
    box-shadow: 0 6px 18px -8px rgba(0,34,110,0.18), 0 0 0 1px rgba(0,34,110,0.06);
    border-top: 3px solid {AZUL};
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 12px 24px -8px rgba(0,34,110,0.25), 0 0 0 1px rgba(0,34,110,0.08);
}}
[data-testid="stMetric"] {{
    min-height: 96px;
}}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {{
    color: #6B7280 !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    line-height: 1.25 !important;
}}
[data-testid="stMetricValue"] {{
    color: {AZUL_OSCURO} !important;
    font-weight: 800 !important;
}}

/* Títulos de página (st.header) -- en esta versión de Streamlit renderiza <h2>,
   no <h1> (verificado con Playwright contra el DOM real). Más presencia, con
   acento de marca. */
div[data-testid="stHeading"] h2 {{
    color: {AZUL_OSCURO} !important;
    font-weight: 800 !important;
    letter-spacing: -0.01em;
    padding-bottom: 0.6rem;
    margin-bottom: 0.75rem !important;
    position: relative;
    display: inline-block;
}}
div[data-testid="stHeading"] h2::after {{
    content: "";
    position: absolute;
    left: 0;
    bottom: 0;
    height: 4px;
    width: 64px;
    border-radius: 2px;
    background: linear-gradient(90deg, {AZUL_OSCURO} 0%, {AZUL} 55%, {DORADO} 100%);
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
