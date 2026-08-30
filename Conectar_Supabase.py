"""Comprueba la conexión a Supabase y muestra el SQL necesario si las tablas no existen.

Uso:
    1. Copia ".streamlit/secrets.toml.example" a ".streamlit/secrets.toml" y completa
       supabase_url y supabase_key (Project Settings → API → service_role).
    2. Ejecuta:  python Conectar_Supabase.py
    3. Si dice que faltan las tablas, copia el SQL que imprime, pégalo en
       Supabase → SQL Editor → New query, y dale RUN.
    4. Si dice que falta habilitar el esquema "infratelco" en la API, ve a
       Project Settings → API → Data API Settings → Exposed schemas y agrégalo.
    5. Vuelve a ejecutar este script para confirmar.

Este proyecto Supabase puede ser el mismo que ya usan otras apps de ISTHO — las tablas
de INFRATELCO viven en su propio esquema ("infratelco"), así que no tocan ni se mezclan
con las de esas apps. No borra ni modifica nada existente.
"""
import sys
from pathlib import Path

# La consola de Windows en español suele usar cp1252, que no sabe imprimir ✔/✖.
# Se fuerza UTF-8 para que este script funcione igual en cualquier equipo.
sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))

from backend.utils import db  # noqa: E402


def main() -> int:
    print("=" * 70)
    print("  CONECTAR INFRATELCO — CONTROL DE ASISTENCIA CON SUPABASE")
    print("=" * 70)
    print()

    ok, mensaje = db.probar_conexion()
    print(("✔ " if ok else "✖ ") + mensaje)
    print()

    if not ok and "tablas todavía no existen" in mensaje:
        print("-" * 70)
        print(db.SQL_CREAR_TABLAS)
        print("-" * 70)
        return 1

    if not ok and "esquema" in mensaje:
        # El mensaje de db.probar_conexion() ya trae los pasos exactos a seguir.
        return 1

    if not ok:
        print("Revisa .streamlit/secrets.toml (o .env) con los valores de tu proyecto Supabase.")
        return 1

    print("Listo. Ahora puedes crear el primer administrador con:")
    print("    python Crear_Administrador.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
