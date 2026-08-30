"""Prueba de humo: todos los módulos deben poder importarse sin credenciales de Supabase
configuradas (la conexión real es "perezosa": solo se intenta al llamar db.cliente()).
Esto detecta errores de importación circular, typos de nombres, etc. antes de desplegar.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib

MODULOS = [
    "backend.config",
    "backend.utils.db",
    "backend.utils.timezone",
    "backend.utils.security",
    "backend.models",
    "backend.repositories.employee_repository",
    "backend.repositories.user_repository",
    "backend.repositories.session_repository",
    "backend.repositories.audit_repository",
    "backend.repositories.company_settings_repository",
    "backend.repositories.password_reset_repository",
    "backend.services.auth.auth_service",
    "backend.services.audit.audit_service",
    "backend.services.employees.employee_service",
    "backend.services.company.company_settings_service",
    "frontend.components.branding",
    "frontend.components.session_state",
    "frontend.pages.login_page",
    "frontend.pages.first_access_page",
    "frontend.pages.employee_home_page",
    "frontend.pages.admin_dashboard_page",
    "frontend.pages.admin_employees_page",
    "frontend.pages.admin_settings_page",
    "frontend.pages.admin_audit_page",
]


def test_todos_los_modulos_importan():
    errores = []
    for nombre in MODULOS:
        try:
            importlib.import_module(nombre)
        except Exception as exc:  # noqa: BLE001
            errores.append(f"{nombre}: {exc!r}")
    assert not errores, "Fallaron imports:\n" + "\n".join(errores)


def test_db_no_disponible_sin_credenciales(monkeypatch):
    from backend import config
    from backend.utils import db

    monkeypatch.setattr(config, "SUPABASE_URL", None)
    monkeypatch.setattr(config, "SUPABASE_KEY", None)
    assert db.disponible() is False
