"""Crea el primer usuario administrador. Se ejecuta UNA sola vez, antes de usar la app
por primera vez (no puede crearse un admin desde la propia app: nadie habría podido
iniciar sesión todavía).

Uso:
    python Crear_Administrador.py
"""
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.models import Role  # noqa: E402
from backend.repositories import user_repository  # noqa: E402
from backend.utils import db, security  # noqa: E402


def main() -> int:
    print("=" * 70)
    print("  CREAR ADMINISTRADOR — INFRATELCO Control de Asistencia")
    print("=" * 70)
    print()

    ok, mensaje = db.probar_conexion()
    if not ok:
        print(f"✖ {mensaje}")
        print("  Ejecuta primero: python Conectar_Supabase.py")
        return 1

    email = input("Correo del administrador: ").strip().lower()
    if not email or "@" not in email:
        print("✖ Correo inválido.")
        return 1

    if user_repository.obtener_por_email(email):
        print(f"✖ Ya existe un usuario con el correo {email}.")
        return 1

    password = getpass.getpass("Contraseña temporal (mínimo 8 caracteres, letras y números): ")
    ok, motivo = security.validar_fortaleza(password)
    if not ok:
        print(f"✖ {motivo}")
        return 1

    confirmacion = getpass.getpass("Confirma la contraseña: ")
    if password != confirmacion:
        print("✖ Las contraseñas no coinciden.")
        return 1

    user_repository.crear(
        email=email,
        password_hash=security.hash_password(password),
        role_code=Role.ADMIN,
        must_change_password=True,
    )

    print()
    print(f"✔ Administrador creado: {email}")
    print("  Se le pedirá cambiar la contraseña en el primer inicio de sesión.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
