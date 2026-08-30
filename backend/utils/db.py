"""Cliente único de Supabase para toda la app.

Si `SUPABASE_URL`/`SUPABASE_KEY` no están configurados (por ejemplo, en un equipo nuevo
antes de conectar la base de datos), `disponible()` devuelve False y los repositorios
deben manejarlo mostrando un mensaje claro en vez de reventar con una excepción críptica.
"""
from __future__ import annotations

from functools import lru_cache

from backend import config

SQL_CREAR_TABLAS = (
    config.RAIZ / "database" / "migrations" / "001_initial_schema.sql"
).read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def cliente():
    if not disponible():
        return None
    from supabase import create_client

    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


def disponible() -> bool:
    return bool(config.SUPABASE_URL and config.SUPABASE_KEY)


def probar_conexion() -> tuple[bool, str]:
    """Devuelve (ok, mensaje) — usado por Conectar_Supabase.py y por la pantalla
    de diagnóstico del administrador."""
    if not disponible():
        return False, "Faltan supabase_url / supabase_key en secrets.toml o .env"
    try:
        cliente().table("company_settings").select("id").limit(1).execute()
        return True, "Conexión con Supabase establecida correctamente."
    except Exception as exc:  # noqa: BLE001 — mensaje de diagnóstico, no un flujo de negocio
        mensaje = str(exc)
        if "relation" in mensaje and "does not exist" in mensaje:
            return False, (
                "Conexión OK, pero las tablas todavía no existen. "
                "Ejecuta el SQL de database/migrations/001_initial_schema.sql "
                "en el SQL Editor de Supabase."
            )
        return False, f"No se pudo conectar: {mensaje}"
