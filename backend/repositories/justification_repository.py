from __future__ import annotations

from backend.utils import db


def crear(fila: dict) -> dict:
    respuesta = db.cliente().table("justifications").insert(fila).execute()
    return respuesta.data[0]


def listar_por_registro(attendance_record_id: str) -> list[dict]:
    respuesta = (
        db.cliente()
        .table("justifications")
        .select("*")
        .eq("attendance_record_id", attendance_record_id)
        .order("created_at", desc=True)
        .execute()
    )
    return respuesta.data
