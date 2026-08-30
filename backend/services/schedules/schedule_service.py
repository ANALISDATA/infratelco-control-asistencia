"""Gestión de horarios (sección 22 del encargo): un horario tiene un nombre, una
tolerancia y hasta 7 configuraciones de día (laboral/no laboral + hora de entrada y
salida). Se guarda siempre el horario completo de una vez — no hay edición parcial
de un solo día desde aquí, para no dejar un horario a medio configurar.
"""
from __future__ import annotations

from backend.models import Schedule, User
from backend.repositories import schedule_repository
from backend.services.audit import audit_service

NOMBRES_DIA = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado", 7: "Domingo"}


def listar_horarios(solo_activos: bool = True) -> list[Schedule]:
    return schedule_repository.listar(solo_activos=solo_activos)


def obtener_horario(schedule_id: str) -> Schedule | None:
    return schedule_repository.obtener_por_id(schedule_id)


def crear_horario(admin: User, nombre: str, tolerancia_minutos: int, dias: list[dict]) -> Schedule:
    """`dias`: lista de dicts con weekday, is_working_day, start_time ("HH:MM" o None),
    end_time ("HH:MM" o None) — uno por cada día 1..7."""
    horario = schedule_repository.crear(nombre, tolerancia_minutos)
    for dia in dias:
        schedule_repository.guardar_dia(
            horario.id,
            dia["weekday"],
            is_working_day=dia["is_working_day"],
            start_time=dia.get("start_time"),
            end_time=dia.get("end_time"),
        )
    audit_service.registrar(admin, "schedule.create", "schedule", horario.id, new_value={"name": nombre})
    return schedule_repository.obtener_por_id(horario.id)


def actualizar_horario(admin: User, schedule_id: str, nombre: str, tolerancia_minutos: int,
                        dias: list[dict]) -> Schedule:
    schedule_repository.actualizar(
        schedule_id, {"name": nombre, "tolerance_minutes": tolerancia_minutos}
    )
    for dia in dias:
        schedule_repository.guardar_dia(
            schedule_id,
            dia["weekday"],
            is_working_day=dia["is_working_day"],
            start_time=dia.get("start_time"),
            end_time=dia.get("end_time"),
        )
    audit_service.registrar(admin, "schedule.update", "schedule", schedule_id, new_value={"name": nombre})
    return schedule_repository.obtener_por_id(schedule_id)


def desactivar_horario(admin: User, schedule_id: str) -> None:
    schedule_repository.actualizar(schedule_id, {"is_active": False})
    audit_service.registrar(admin, "schedule.deactivate", "schedule", schedule_id)
