"""Configuración central de la app: lee credenciales de `st.secrets` cuando corre bajo
Streamlit, y de variables de entorno (`.env`) cuando corre como script suelto (por ejemplo
`Conectar_Supabase.py`). Nunca hay una API key escrita directamente en el código.
"""
from __future__ import annotations

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _cargar_dotenv() -> None:
    ruta = RAIZ / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        os.environ.setdefault(clave.strip(), valor.strip())


_cargar_dotenv()


def leer(clave: str, por_defecto: str | None = None) -> str | None:
    """Lee una credencial: primero intenta `st.secrets`, luego variables de entorno."""
    try:
        import streamlit as st

        valor = st.secrets.get(clave)
        if valor not in (None, ""):
            return valor
    except Exception:
        pass
    return os.environ.get(clave.upper(), por_defecto)


SUPABASE_URL = leer("supabase_url")
SUPABASE_KEY = leer("supabase_key")

APP_SECRET = leer("app_secret", "")
SESSION_SECRET = leer("session_secret", "")

TIMEZONE = leer("timezone", "America/Bogota")

GEOCODING_PROVIDER = leer("geocoding_provider", "nominatim")
GEOCODING_API_KEY = leer("geocoding_api_key", "")

WHATSAPP_PROVIDER = leer("whatsapp_provider", "")
WHATSAPP_API_KEY = leer("whatsapp_api_key", "")
WHATSAPP_PHONE_NUMBER_ID = leer("whatsapp_phone_number_id", "")

EMAIL_PROVIDER = leer("email_provider", "")
EMAIL_API_KEY = leer("email_api_key", "")

# Reglas de sesión y seguridad (no hardcodeadas en la lógica de negocio)
SESSION_TTL_HOURS = 12
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15
PASSWORD_RESET_TTL_MINUTES = 30
MIN_PASSWORD_LENGTH = 8
