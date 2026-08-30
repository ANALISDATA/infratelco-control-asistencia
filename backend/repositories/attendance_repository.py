from __future__ import annotations

from datetime import date

from backend.models import AttendanceRecord
from backend.utils import db


def obtener_por_empleado_y_fecha(employee_id: str, work_date: date) -> AttendanceRecord | None:
    respuesta = (
        db.cliente()
        .table("attendance_records")
        .select("*")
        .eq("employee_id", employee_id)
        .eq("work_date", work_date.isoformat())
        .limit(1)
        .execute()
    )
    return AttendanceRecord.from_row(respuesta.data[0]) if respuesta.data else None


def crear(fila: dict) -> AttendanceRecord:
    respuesta = db.cliente().table("attendance_records").insert(fila).execute()
    return AttendanceRecord.from_row(respuesta.data[0])


def actualizar(attendance_id: str, cambios: dict) -> AttendanceRecord:
    respuesta = db.cliente().table("attendance_records").update(cambios).eq("id", attendance_id).execute()
    return AttendanceRecord.from_row(respuesta.data[0])


def listar_por_fecha(work_date: date) -> list[AttendanceRecord]:
    respuesta = (
        db.cliente()
        .table("attendance_records")
        .select("*")
        .eq("work_date", work_date.isoformat())
        .execute()
    )
    return [AttendanceRecord.from_row(r) for r in respuesta.data]


def listar_por_empleado(employee_id: str, pagina: int = 1, por_pagina: int = 30) -> list[AttendanceRecord]:
    desde = (pagina - 1) * por_pagina
    hasta = desde + por_pagina - 1
    respuesta = (
        db.cliente()
        .table("attendance_records")
        .select("*")
        .eq("employee_id", employee_id)
        .order("work_date", desc=True)
        .range(desde, hasta)
        .execute()
    )
    return [AttendanceRecord.from_row(r) for r in respuesta.data]
