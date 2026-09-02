"""Correcciones administrativas y justificaciones (Fase 3) — un administrador puede
corregir una hora de entrada/salida mal marcada (ej. el empleado olvidó marcar la
salida, o marcó por error) y debe dejar un motivo. Nunca se pierde el dato original:
`attendance_records.original_check_in_at`/`original_check_out_at` quedan intactos tal
como se guardaron en el momento real del registro — aquí solo se llenan
`modified_check_in_at`/`modified_check_out_at` con el valor corregido, así el
histórico completo (qué marcó vs. qué quedó al final) sigue siendo trazable.
"""
from __future__ import annotations

from datetime import datetime

from backend.models import AttendanceRecord, User
from backend.repositories import attendance_repository, justification_repository
from backend.services.audit import audit_service
from backend.utils.timezone import ahora

TIPOS_JUSTIFICACION = {
    "error_registro": "Error al marcar (registro equivocado)",
    "olvido": "Olvidó marcar",
    "actividad_laboral": "Actividad laboral fuera del sitio habitual",
    "salud": "Cita médica / incapacidad",
    "personal": "Permiso personal",
    "otro": "Otro",
}


class CorrectionError(Exception):
    """Mensaje ya listo para mostrar al administrador."""


def corregir_registro(
    admin: User,
    attendance_id: str,
    *,
    nuevo_check_in: datetime | None,
    nuevo_check_out: datetime | None,
    tipo: str,
    motivo: str,
) -> AttendanceRecord:
    if not motivo or not motivo.strip():
        raise CorrectionError("Debes indicar el motivo de la corrección.")
    if nuevo_check_in is None and nuevo_check_out is None:
        raise CorrectionError("Debes corregir al menos la hora de entrada o la de salida.")
    if tipo not in TIPOS_JUSTIFICACION:
        raise CorrectionError("Tipo de justificación no válido.")

    registro = attendance_repository.obtener_por_id(attendance_id)
    if registro is None:
        raise CorrectionError("El registro ya no existe.")

    check_in_efectivo = nuevo_check_in or registro.check_in_at
    check_out_efectivo = nuevo_check_out or registro.check_out_at
    if check_out_efectivo is not None and check_in_efectivo is None:
        raise CorrectionError("No se puede corregir la salida de un registro sin entrada.")
    if check_in_efectivo and check_out_efectivo and check_out_efectivo <= check_in_efectivo:
        raise CorrectionError("La hora de salida debe ser después de la hora de entrada.")

    estado_anterior = {
        "check_in_at": registro.check_in_at.isoformat() if registro.check_in_at else None,
        "check_in_status": registro.check_in_status,
        "check_out_at": registro.check_out_at.isoformat() if registro.check_out_at else None,
        "worked_minutes": registro.worked_minutes,
        "overtime_minutes": registro.overtime_minutes,
    }

    cambios: dict = {}

    if nuevo_check_in is not None:
        nuevo_estado = registro.check_in_status
        if registro.check_in_expected_at:
            nuevo_estado = "on_time" if nuevo_check_in <= registro.check_in_expected_at else "late"
        cambios.update(
            check_in_at=nuevo_check_in.isoformat(),
            modified_check_in_at=nuevo_check_in.isoformat(),
            check_in_status=nuevo_estado,
        )

    if nuevo_check_out is not None:
        cambios.update(
            check_out_at=nuevo_check_out.isoformat(),
            modified_check_out_at=nuevo_check_out.isoformat(),
            check_out_status="registered",
        )

    if check_in_efectivo and check_out_efectivo:
        minutos_trabajados = int((check_out_efectivo - check_in_efectivo).total_seconds() // 60)
        duracion_esperada = 0
        if registro.check_in_expected_at and registro.check_out_expected_at:
            duracion_esperada = max(
                0, int((registro.check_out_expected_at - registro.check_in_expected_at).total_seconds() // 60)
            )
        cambios["worked_minutes"] = minutos_trabajados
        cambios["overtime_minutes"] = max(0, minutos_trabajados - duracion_esperada)

    cambios["modified_by"] = admin.id
    cambios["modified_at"] = ahora().isoformat()

    justificacion = justification_repository.crear({
        "attendance_record_id": attendance_id,
        "justification_type": tipo,
        "reason": motivo.strip(),
        "original_status": estado_anterior["check_in_status"],
        "new_status": cambios.get("check_in_status", estado_anterior["check_in_status"]),
        "authorized_by": admin.id,
    })
    cambios["justification_id"] = justificacion["id"]

    registro_actualizado = attendance_repository.actualizar(attendance_id, cambios)

    audit_service.registrar(
        admin, "attendance.correction", "attendance_record", attendance_id,
        old_value=estado_anterior, new_value=cambios, reason=motivo.strip(),
    )

    return registro_actualizado
