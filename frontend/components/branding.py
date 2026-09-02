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
SVG_CIRCUITO_URI = "data:image/svg+xml," + quote(_SVG_CIRCUITO)
FONDO_CIRCUITO_CSS = (
    "background-image: radial-gradient(circle at 15% 0%, rgba(0,124,208,0.35) 0%, transparent 55%), "
    f'url("{SVG_CIRCUITO_URI}"); '
    "background-repeat: no-repeat, repeat; background-size: auto, 140px 140px;"
)

# --- Modo claro/oscuro ---------------------------------------------------
# El sidebar se queda siempre azul oscuro de marca (es identidad, no "modo").
# Lo que cambia es el fondo de la página y las tarjetas/texto del contenido.
# Colores del modo oscuro validados por contraste real contra su propio fondo
# (no elegidos a ojo) -- ver el chequeo hecho con la misma herramienta que
# valida los gráficos: azul claro 6.84:1, verde 8.05:1, dorado 11.94:1,
# texto principal 14.32:1, texto secundario 7.11:1, todos sobre #0F1522.
CLAVE_TEMA = "tema_oscuro"


def es_oscuro() -> bool:
    return bool(st.session_state.get(CLAVE_TEMA, False))


def alternar_tema() -> None:
    st.session_state[CLAVE_TEMA] = not es_oscuro()


def _tokens(oscuro: bool) -> dict:
    if oscuro:
        return dict(
            bg_pagina="#0F1522",
            bg_tarjeta="#1A2236",
            borde_tarjeta="rgba(255,255,255,0.08)",
            texto_principal="#E5E7EB",
            texto_secundario="#9AA5B4",
            acento_titulo="#4FA8E8",
            sombra="rgba(0,0,0,0.45)",
        )
    return dict(
        bg_pagina="#F4F6FA",
        bg_tarjeta=BLANCO,
        borde_tarjeta="rgba(0,34,110,0.06)",
        texto_principal="#14213D",
        texto_secundario="#6B7280",
        acento_titulo=AZUL_OSCURO,
        sombra="rgba(0,34,110,0.18)",
    )


def _css(oscuro: bool) -> str:
    t = _tokens(oscuro)
    return f"""
<style>
:root {{
    --infratelco-azul-oscuro: {AZUL_OSCURO};
    --infratelco-azul: {AZUL};
    --infratelco-verde: {VERDE};
    --infratelco-dorado: {DORADO};
}}
.stApp {{
    background-color: {t['bg_pagina']} !important;
}}
.stApp, .stApp p, .stApp span, .stApp li, .stApp label {{
    color: {t['texto_principal']};
}}
[data-testid="stSidebar"] {{
    background-color: {AZUL_OSCURO};
    {FONDO_CIRCUITO_CSS}
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

/* El texto de los botones va en <p>/<span> anidados dentro del <button>. La regla
   ".stApp p, .stApp span" de arriba les pinta el color de texto normal de la página
   -- y como esa regla apunta directo a esos elementos (no es herencia), gana sobre
   el "color: ... !important" puesto solo en el <button> padre, aunque tenga
   !important (el !important del padre solo protege lo heredado, no una coincidencia
   directa en el hijo). Por eso el texto quedaba invisible sobre el fondo azul oscuro
   -- se soluciona apuntando también a los hijos directamente. Se usa el dorado de
   marca en vez de blanco, por pedido explícito del cliente. */
div.stButton > button, div.stFormSubmitButton > button,
div.stButton > button *, div.stFormSubmitButton > button * {{
    color: {DORADO} !important;
}}
div.stButton > button, div.stFormSubmitButton > button {{
    background-color: {AZUL_OSCURO} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover,
div.stButton > button:hover *, div.stFormSubmitButton > button:hover * {{
    color: {BLANCO} !important;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
    background-color: {AZUL} !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 16px -6px rgba(0,124,208,0.5);
}}
[data-testid="stSidebar"] div.stButton > button {{
    background-color: rgba(255,255,255,0.10) !important;
    border: 1.5px solid rgba(255,255,255,0.35) !important;
    padding: 0.55rem 0 !important;
}}
[data-testid="stSidebar"] div.stButton > button,
[data-testid="stSidebar"] div.stButton > button * {{
    color: {BLANCO} !important;
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
    background: {t['bg_tarjeta']};
    border-radius: 14px;
    padding: 1.1rem 1.25rem 1rem 1.25rem;
    box-shadow: 0 6px 18px -8px {t['sombra']}, 0 0 0 1px {t['borde_tarjeta']};
    border-top: 3px solid {AZUL};
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 12px 24px -8px {t['sombra']}, 0 0 0 1px {t['borde_tarjeta']};
}}
[data-testid="stMetric"] {{
    min-height: 96px;
}}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {{
    color: {t['texto_secundario']} !important;
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
    color: {t['acento_titulo']} !important;
    font-weight: 800 !important;
}}

/* Títulos de página (st.header) -- en esta versión de Streamlit renderiza <h2>,
   no <h1> (verificado con Playwright contra el DOM real). Más presencia, con
   acento de marca. */
div[data-testid="stHeading"] h2 {{
    color: {t['acento_titulo']} !important;
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
    color: {t['acento_titulo']};
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    font-size: 0.85rem;
}}

/* Botón de modo claro/oscuro -- antes usaba un emoji (☀️/🌙), inmune al CSS de color
   por ser un glifo de emoji; ahora es un icono real de Material Symbols, que sí
   respeta "color", así que hace falta forzarlo junto con el fondo o queda blanco
   sobre blanco (bug real, visto con Playwright). */
.st-key-boton_tema button {{
    border-radius: 999px !important;
    width: 2.6rem;
    height: 2.6rem;
    padding: 0 !important;
    font-size: 1.1rem !important;
    background-color: rgba(255,255,255,0.10) !important;
}}
.st-key-boton_tema button,
.st-key-boton_tema button * {{
    color: {BLANCO} !important;
}}

/* Celular: nunca debe aparecer una barra de scroll horizontal ni contenido cortado,
   sea cual sea el tamaño del teléfono -- afecta sobre todo a "Mi cuenta" (marcar
   ingreso/salida), la pantalla que más se usa desde el celular en campo. */
.stApp {{ overflow-x: hidden; }}
img {{ max-width: 100%; height: auto; }}
@media (max-width: 480px) {{
    .block-container {{ padding-left: 0.75rem !important; padding-right: 0.75rem !important; }}
    div[data-testid="stHeading"] h2 {{ font-size: 1.4rem !important; }}
}}
</style>
"""


def aplicar_estilo() -> None:
    st.markdown(_css(es_oscuro()), unsafe_allow_html=True)


def boton_tema() -> None:
    """Botón redondo que alterna el fondo de la app entre claro y oscuro."""
    with st.container(key="boton_tema"):
        icono = ":material/light_mode:" if es_oscuro() else ":material/dark_mode:"
        if st.button("", icon=icono, help="Cambiar a modo claro/oscuro"):
            alternar_tema()
            st.rerun()


# --- Tarjetas con icono (estilo "badge" de color) -------------------------
# Reemplaza st.metric en las pantallas de asistencia/dashboard: Streamlit no deja
# ponerle un icono a st.metric, así que estas se arman con HTML propio. El icono usa
# la misma fuente "Material Symbols Rounded" que Streamlit ya carga para sus propios
# iconos (:material/nombre:), así que no hace falta cargar nada aparte -- basta con
# reusar el mismo nombre de icono como texto dentro de un <span> con esa fuente.
_COLORES_BADGE = {
    "azul": AZUL,
    "verde": VERDE,
    "dorado": "#B8930A",  # el dorado de marca es muy claro para verse como icono/texto
    "rojo": "#DC2626",
    "gris": "#6B7280",
}


def _hex_a_rgb(color_hex: str) -> tuple[int, int, int]:
    color_hex = color_hex.lstrip("#")
    return tuple(int(color_hex[i : i + 2], 16) for i in (0, 2, 4))


def tarjeta_metrica(titulo: str, valor, icono: str, color: str = "azul", ayuda: str | None = None) -> None:
    """`icono`: nombre de un icono de Material Symbols (ej. "check_circle"), sin los
    dos puntos ni el prefijo "material/" que sí lleva `icon=":material/x:"` en los
    widgets nativos de Streamlit. `color`: una clave de _COLORES_BADGE."""
    oscuro = es_oscuro()
    t = _tokens(oscuro)
    r, g, b = _hex_a_rgb(_COLORES_BADGE.get(color, color))
    alfa_fondo = 0.24 if oscuro else 0.12
    ayuda_html = (
        f'<div style="font-size:0.76rem;color:{t["texto_secundario"]};margin-top:0.1rem;">{ayuda}</div>'
        if ayuda else ""
    )
    st.markdown(
        f"""
        <div style="background:{t['bg_tarjeta']}; border-radius:14px; padding:1rem 1.15rem;
                     box-shadow:0 6px 18px -8px {t['sombra']}, 0 0 0 1px {t['borde_tarjeta']};
                     display:flex; flex-direction:column; gap:0.7rem; min-height:112px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:0.5rem;">
                <div style="font-size:0.72rem; font-weight:700; letter-spacing:0.03em;
                             text-transform:uppercase; color:{t['texto_secundario']}; line-height:1.3;">
                    {titulo}
                </div>
                <div style="width:40px; height:40px; min-width:40px; border-radius:11px;
                             background:rgba({r},{g},{b},{alfa_fondo}); display:flex;
                             align-items:center; justify-content:center;">
                    <span style="font-family:'Material Symbols Rounded'; font-size:21px;
                                  color:rgb({r},{g},{b}); line-height:1;">{icono}</span>
                </div>
            </div>
            <div style="font-size:1.65rem; font-weight:800; color:{t['texto_principal']}; line-height:1;">
                {valor}
            </div>
            {ayuda_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


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
