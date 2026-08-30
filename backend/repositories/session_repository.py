"""Sesiones de login. El token en claro solo existe en memoria/cookie del navegador;
en la base de datos se guarda su hash (ver backend/utils/security.hash_token)."""
from __future__ import annotations

from datetime import datetime

from backend.utils import db


def crear(user_id: str, token_hash: str, expires_at: datetime, ip_address: str | None = None,
          user_agent: str | None = None) -> str:
    fila = {
        "user_id": user_id,
        "token_hash": token_hash,
        "expires_at": expires_at.isoformat(),
        "ip_address": ip_address,
        "user_agent": user_agent,
    }
    respuesta = db.cliente().table("sessions").insert(fila).execute()
    return respuesta.data[0]["id"]


def obtener_valida(token_hash: str, ahora: datetime) -> dict | None:
    respuesta = (
        db.cliente()
        .table("sessions")
        .select("*")
        .eq("token_hash", token_hash)
        .is_("revoked_at", "null")
        .gt("expires_at", ahora.isoformat())
        .limit(1)
        .execute()
    )
    return respuesta.data[0] if respuesta.data else None


def revocar(token_hash: str, ahora: datetime) -> None:
    db.cliente().table("sessions").update({"revoked_at": ahora.isoformat()}).eq(
        "token_hash", token_hash
    ).execute()
