"""Registro de ingreso y salida — el corazón de la Fase 2.

Reglas duras (no negociables, del encargo original):
  - La hora oficial SIEMPRE sale del servidor (`backend.utils.timezone.ahora()`),
    nunca del reloj del celular del empleado.
  - La ubicación se captura ÚNICAMENTE en el momento del ingreso/salida — nunca se
    guarda un "último visto" ni se hace tracking continuo.
  - Un empleado no puede tener dos ingresos ni dos salidas el mismo día, ni una
    salida sin ingreso previo.
  - Si la geolocalización falla, se sigue la configuración de la empresa (bloquear o
    permitir con advertencia) — nunca se inventa una ubicación ni una dirección.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from backend.models import AttendanceRecord, Employee
from backend.repositories import attendance_repository, company_settings_repository, schedule_repository
from backend.services.audit import audit_service
from backend.services.geolocation import location_service
from backend.utils.timezone import BOGOTA, ahora


class AttendanceError(Exception):
    """Mensaje ya listo para mostrar al empleado."""


@dataclass
class ResultadoRegistro:
    registro: AttendanceRecord
    advertencias: list[str]


def _hora_desde_valor(valor) -> time:
    return valor if isinstance(valor, time) else time.fromisoformat(str(valor))


def _hora_y_tolerancia_esperadas(empleado: Employee, fecha) -> tuple[time, int]:
    ajustes = company_settings_repository.obtener()
    hora_esperada = _hora_desde_valor(ajustes.default_check_in_time)
    tolerancia = ajustes.tolerance_minutes

    if empleado.schedule_id:
        horario = schedule_repository.obtener_por_id(empleado.schedule_id)
        if horario:
            tolerancia = horario.tolerance_minutes
            dia = next((d for d in (horario.dias or []) if d.weekday == fecha.isoweekday()), None)
            if dia and dia.is_working_day and dia.start_time:
                hora_esperada = dia.start_time

    return hora_esperada, tolerancia


def _hora_salida_esperada(empleado: Employee, fecha) -> time:
    ajustes = company_settings_repository.obtener()
    hora_esperada = _hora_desde_valor(ajustes.default_check_out_time)

    if empleado.schedule_id:
        horario = schedule_repository.obtener_por_id(empleado.schedule_id)
        if horario:
            dia = next((d for d in (horario.dias or []) if d.weekday == fecha.isoweekday()), None)
            if dia and dia.is_working_day and dia.end_time:
                hora_esperada = dia.end_time

    return hora_esperada


def _resolver_ubicacion(resultado_navegador: dict | None, precision_minima_m: float,
                         requerida: bool, comportamiento_si_falla: str):
    """Devuelve (Ubicacion | None, advertencia | None). Lanza AttendanceError si la
    empresa exige bloquear el registro y no hay ubicación válida."""
    ubicacion = None
    motivo_falla = None

    if resultado_navegador is None:
        motivo_falla = "No se pudo obtener tu ubicación."
    else:
        try:
            ubicacion = location_service.procesar_resultado_navegador(resultado_navegador)
            if precision_minima_m and ubicacion.precision_m > precision_minima_m:
                motivo_falla = (
                    f"La precisión de tu ubicación ({ubicacion.precision_m:.0f} m) es menor "
                    f"a la mínima requerida por la empresa ({precision_minima_m:.0f} m)."
                )
        except location_service.UbicacionError as error:
            motivo_falla = str(error)

    if motivo_falla is None:
        return ubicacion, None

    if requerida and comportamiento_si_falla == "block":
        raise AttendanceError(motivo_falla)

    return ubicacion, motivo_falla


def registrar_ingreso(empleado: Employee, resultado_navegador: dict | None,
                       comentario: str | None = None) -> ResultadoRegistro:
    if not empleado.is_active:
        raise AttendanceError("Tu usuario está desactivado. Contacta al administrador.")

    momento = ahora()
    hoy = momento.date()

    if attendance_repository.obtener_por_empleado_y_fecha(empleado.id, hoy):
        raise AttendanceError("Ya registraste tu ingreso hoy.")

    # Obligatorio (regla del cliente): sin obra/trabajo no hay registro. Se valida aquí
    # -- no solo en la pantalla -- porque nunca se confía únicamente en el frontend.
    if not comentario or not comentario.strip():
        raise AttendanceError("Debes indicar la obra o el trabajo que vas a realizar para registrar el ingreso.")

    ajustes = company_settings_repository.obtener()
    ubicacion, advertencia = _resolver_ubicacion(
        resultado_navegador, ajustes.min_gps_accuracy_m,
        ajustes.require_location_check_in, ajustes.on_location_failure,
    )

    hora_esperada, tolerancia = _hora_y_tolerancia_esperadas(empleado, hoy)
    esperado_dt = datetime.combine(hoy, hora_esperada, tzinfo=BOGOTA)
    estado = "on_time" if momento <= esperado_dt + timedelta(minutes=tolerancia) else "late"

    fila = {
        "employee_id": empleado.id,
        "work_date": hoy.isoformat(),
        "check_in_at": momento.isoformat(),
        "check_in_status": estado,
        "check_in_expected_at": esperado_dt.isoformat(),
        "original_check_in_at": momento.isoformat(),
        "observation": comentario.strip() if comentario and comentario.strip() else None,
    }
    if ubicacion:
        fila.update(
            check_in_latitude=ubicacion.latitud,
            check_in_longitude=ubicacion.longitud,
            check_in_accuracy_m=ubicacion.precision_m,
            check_in_location_at=ubicacion.capturada_en.isoformat(),
            check_in_address=ubicacion.direccion,
        )

    registro = attendance_repository.crear(fila)
    audit_service.registrar(
        None, "attendance.check_in", "attendance_record", registro.id,
        new_value={"employee_id": empleado.id, "check_in_at": momento.isoformat(), "status": estado},
    )

    advertencias = [advertencia] if advertencia else []
    return ResultadoRegistro(registro=registro, advertencias=advertencias)


def registrar_salida(empleado: Employee, resultado_navegador: dict | None) -> ResultadoRegistro:
    if not empleado.is_active:
        raise AttendanceError("Tu usuario está desactivado. Contacta al administrador.")

    momento = ahora()
    hoy = momento.date()

    registro_existente = attendance_repository.obtener_por_empleado_y_fecha(empleado.id, hoy)
    if registro_existente is None:
        raise AttendanceError("Todavía no has registrado tu ingreso hoy.")
    if registro_existente.check_out_at is not None:
        raise AttendanceError("Ya registraste tu salida hoy.")

    ajustes = company_settings_repository.obtener()
    ubicacion, advertencia = _resolver_ubicacion(
        resultado_navegador, ajustes.min_gps_accuracy_m,
        ajustes.require_location_check_out, ajustes.on_location_failure,
    )

    minutos_trabajados = int((momento - registro_existente.check_in_at).total_seconds() // 60)

    # Horas extra: lo que pase de la hora de salida esperada ESE día (horario propio del
    # empleado si tiene uno asignado, si no el predeterminado de la empresa) -- se calcula
    # y se guarda aquí, no se recalcula después, para que quede fijo con la configuración
    # vigente ese día (mismo criterio que ya se usa para check_in_status).
    hora_salida_esperada = _hora_salida_esperada(empleado, hoy)
    esperado_salida_dt = datetime.combine(hoy, hora_salida_esperada, tzinfo=BOGOTA)
    minutos_extra = max(0, int((momento - esperado_salida_dt).total_seconds() // 60))

    cambios = {
        "check_out_at": momento.isoformat(),
        "check_out_status": "registered",
        "check_out_expected_at": esperado_salida_dt.isoformat(),
        "original_check_out_at": momento.isoformat(),
        "worked_minutes": minutos_trabajados,
        "overtime_minutes": minutos_extra,
    }
    if ubicacion:
        cambios.update(
            check_out_latitude=ubicacion.latitud,
            check_out_longitude=ubicacion.longitud,
            check_out_accuracy_m=ubicacion.precision_m,
            check_out_location_at=ubicacion.capturada_en.isoformat(),
            check_out_address=ubicacion.direccion,
        )

    registro = attendance_repository.actualizar(registro_existente.id, cambios)
    audit_service.registrar(
        None, "attendance.check_out", "attendance_record", registro.id,
        new_value={"employee_id": empleado.id, "check_out_at": momento.isoformat()},
    )

    advertencias = [advertencia] if advertencia else []
    return ResultadoRegistro(registro=registro, advertencias=advertencias)
