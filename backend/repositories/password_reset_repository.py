from __future__ import annotations

from datetime import datetime

from backend.utils import db


def crear(user_id: str, token_hash: str, expires_at: datetime) -> None:
    db.cliente().table("password_resets").insert(
        {"user_id": user_id, "token_hash": token_hash, "expires_at": expires_at.isoformat()}
    ).execute()


def obtener_valido(token_hash: str, ahora: datetime) -> dict | None:
    respuesta = (
        db.cliente()
        .table("password_resets")
        .select("*")
        .eq("token_hash", token_hash)
        .is_("used_at", "null")
        .gt("expires_at", ahora.isoformat())
        .limit(1)
        .execute()
    )
    return respuesta.data[0] if respuesta.data else None


def marcar_usado(token_hash: str, ahora: datetime) -> None:
    db.cliente().table("password_resets").update({"used_at": ahora.isoformat()}).eq(
        "token_hash", token_hash
    ).execute()
