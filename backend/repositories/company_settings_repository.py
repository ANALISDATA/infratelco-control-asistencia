from __future__ import annotations

from backend.models import CompanySettings
from backend.utils import db


def obtener() -> CompanySettings:
    respuesta = db.cliente().table("company_settings").select("*").eq("id", 1).limit(1).execute()
    if not respuesta.data:
        return CompanySettings()
    return CompanySettings.from_row(respuesta.data[0])


def actualizar(cambios: dict) -> CompanySettings:
    respuesta = db.cliente().table("company_settings").update(cambios).eq("id", 1).execute()
    return CompanySettings.from_row(respuesta.data[0])
