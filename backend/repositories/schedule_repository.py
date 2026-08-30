from __future__ import annotations

from backend.models import Schedule, ScheduleDay
from backend.utils import db


def listar(solo_activos: bool = True) -> list[Schedule]:
    query = db.cliente().table("schedules").select("*").order("name")
    if solo_activos:
        query = query.eq("is_active", True)
    return [Schedule.from_row(r) for r in query.execute().data]


def obtener_por_id(schedule_id: str) -> Schedule | None:
    respuesta = db.cliente().table("schedules").select("*").eq("id", schedule_id).limit(1).execute()
    if not respuesta.data:
        return None
    horario = Schedule.from_row(respuesta.data[0])
    horario.dias = obtener_dias(schedule_id)
    return horario


def obtener_dias(schedule_id: str) -> list[ScheduleDay]:
    respuesta = (
        db.cliente().table("schedule_days").select("*").eq("schedule_id", schedule_id).order("weekday").execute()
    )
    return [ScheduleDay.from_row(r) for r in respuesta.data]


def crear(nombre: str, tolerancia_minutos: int) -> Schedule:
    respuesta = (
        db.cliente()
        .table("schedules")
        .insert({"name": nombre, "tolerance_minutes": tolerancia_minutos})
        .execute()
    )
    return Schedule.from_row(respuesta.data[0])


def actualizar(schedule_id: str, cambios: dict) -> None:
    db.cliente().table("schedules").update(cambios).eq("id", schedule_id).execute()


def guardar_dia(schedule_id: str, weekday: int, *, is_working_day: bool,
                 start_time: str | None, end_time: str | None) -> None:
    """Crea o reemplaza la configuración de un día de la semana para un horario
    (upsert manual: un schedule_id+weekday es único por esquema)."""
    cliente = db.cliente()
    existente = (
        cliente.table("schedule_days")
        .select("id")
        .eq("schedule_id", schedule_id)
        .eq("weekday", weekday)
        .limit(1)
        .execute()
    )
    fila = {
        "schedule_id": schedule_id,
        "weekday": weekday,
        "is_working_day": is_working_day,
        "start_time": start_time,
        "end_time": end_time,
    }
    if existente.data:
        cliente.table("schedule_days").update(fila).eq("id", existente.data[0]["id"]).execute()
    else:
        cliente.table("schedule_days").insert(fila).execute()
