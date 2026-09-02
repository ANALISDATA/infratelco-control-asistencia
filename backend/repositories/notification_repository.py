from __future__ import annotations

from backend.utils import db


def late_arrival_habilitado() -> bool:
    respuesta = (
        db.cliente().table("notification_settings").select("late_arrival_enabled").eq("id", 1).limit(1).execute()
    )
    if not respuesta.data:
        return True
    return respuesta.data[0].get("late_arrival_enabled", True)


def registrar_envio(
    *, notification_type: str, channel: str, recipient: str, body: str,
    status: str, related_entity_type: str | None = None, related_entity_id: str | None = None,
    error_message: str | None = None, sent_at: str | None = None,
) -> None:
    db.cliente().table("notifications").insert({
        "notification_type": notification_type,
        "channel": channel,
        "recipient": recipient,
        "body": body,
        "status": status,
        "related_entity_type": related_entity_type,
        "related_entity_id": related_entity_id,
        "error_message": error_message,
        "sent_at": sent_at,
    }).execute()
