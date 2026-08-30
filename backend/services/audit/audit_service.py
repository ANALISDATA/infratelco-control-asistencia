"""Punto único desde el que el resto de la app debe registrar auditoría, para que
ninguna pantalla se le olvide pasar algún campo obligatorio."""
from __future__ import annotations

from backend.models import User
from backend.repositories import audit_repository


def registrar(
    actor: User | None,
    action: str,
    entity_type: str,
    entity_id: str | None,
    *,
    old_value: dict | None = None,
    new_value: dict | None = None,
    reason: str | None = None,
    ip_address: str | None = None,
) -> None:
    audit_repository.registrar(
        user_id=actor.id if actor else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        reason=reason,
        ip_address=ip_address,
    )
