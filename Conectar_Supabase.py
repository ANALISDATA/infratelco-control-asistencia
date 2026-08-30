"""Comprueba la conexión a Supabase y muestra el SQL necesario si las tablas no existen.

Uso:
    1. Copia ".streamlit/secrets.toml.example" a ".streamlit/secrets.toml" y completa
       supabase_url y supabase_key (Project Settings → API → service_role).
    2. Ejecuta:  python Conectar_Supabase.py
    3. Si dice que faltan las tablas, copia el SQL que imprime, pégalo en
       Supabase → SQL Editor → New query, y dale RUN.
    4. Vuelve a ejecutar este script para confirmar.

No borra ni modifica nada existente.
"""
import sys
from pathlib import Path

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

    if not ok and "tablas todavía no existen" not in mensaje:
        print("Revisa .streamlit/secrets.toml (o .env) con los valores de tu proyecto Supabase.")
        return 1

    if not ok:
        print("-" * 70)
        print(db.SQL_CREAR_TABLAS)
        print("-" * 70)
        return 1

    print("Listo. Ahora puedes crear el primer administrador con:")
    print("    python Crear_Administrador.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
