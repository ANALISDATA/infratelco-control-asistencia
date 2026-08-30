from __future__ import annotations

from backend.models import User
from backend.repositories import company_settings_repository
from backend.services.audit import audit_service


def obtener():
    return company_settings_repository.obtener()


def actualizar(admin: User, cambios: dict):
    actualizado = company_settings_repository.actualizar(cambios)
    audit_service.registrar(admin, "company_settings.update", "company_settings", "1", new_value=cambios)
    return actualizado
