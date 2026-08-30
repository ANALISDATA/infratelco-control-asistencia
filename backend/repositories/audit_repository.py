"""La auditoría es de solo-inserción desde la aplicación: no existe un `actualizar`
ni un `eliminar` a propósito (regla #24 del encargo: debe ser inmutable)."""
from __future__ import annotations

from backend.utils import db


def registrar(
    *,
    user_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    reason: str | None = None,
    ip_address: str | None = None,
) -> None:
    fila = {
        "user_id": user_id,
        "action": action,
        "entity_type": entity_type,
        "entity_id": str(entity_id) if entity_id is not None else None,
        "old_value": old_value,
        "new_value": new_value,
        "reason": reason,
        "ip_address": ip_address,
    }
    db.cliente().table("audit_logs").insert(fila).execute()


def listar(pagina: int = 1, por_pagina: int = 50, entity_type: str | None = None) -> list[dict]:
    query = db.cliente().table("audit_logs").select("*").order("created_at", desc=True)
    if entity_type:
        query = query.eq("entity_type", entity_type)
    desde = (pagina - 1) * por_pagina
    hasta = desde + por_pagina - 1
    return query.range(desde, hasta).execute().data
