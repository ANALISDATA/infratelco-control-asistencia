"""Aviso de llegada tarde al administrador por WhatsApp (Fase 5).

Regla dura: esto NUNCA debe tumbar ni retrasar el registro de ingreso del empleado.
Es un aviso "mejor esfuerzo" — si CallMeBot falla, se guarda el error en `notifications`
para poder revisarlo después, pero el empleado ya quedó registrado igual.
"""
from __future__ import annotations

from backend import config
from backend.models import AttendanceRecord, Employee
from backend.repositories import company_settings_repository, notification_repository
from backend.services.notifications.providers import callmebot_provider
from backend.utils.timezone import ahora

PROVEEDORES_SOPORTADOS = {"callmebot"}


def _mensaje_llegada_tarde(empleado: Employee, registro: AttendanceRecord) -> str:
    hora_llegada = registro.check_in_at.strftime("%I:%M %p").lstrip("0")
    hora_esperada = registro.check_in_expected_at.strftime("%I:%M %p").lstrip("0") if registro.check_in_expected_at else "?"
    return (
        f"⚠️ INFRATELCO — Llegada tarde\n"
        f"{empleado.full_name} marcó ingreso a las {hora_llegada} "
        f"(hora esperada: {hora_esperada})."
    )


def _enviar(numero: str, mensaje: str, *, tipo: str, entidad_id: str | None) -> None:
    """Envía y siempre deja constancia en `notifications`, sin propagar la excepción."""
    try:
        if config.WHATSAPP_PROVIDER not in PROVEEDORES_SOPORTADOS:
            raise callmebot_provider.CallMeBotError(
                f"Proveedor de WhatsApp no configurado (whatsapp_provider='{config.WHATSAPP_PROVIDER}')."
            )
        callmebot_provider.enviar_whatsapp(numero, mensaje, config.WHATSAPP_API_KEY)
    except Exception as error:  # noqa: BLE001 -- mejor esfuerzo, nunca debe romper el flujo del caller
        notification_repository.registrar_envio(
            notification_type=tipo, channel="whatsapp", recipient=numero, body=mensaje,
            status="failed", related_entity_type="attendance_record", related_entity_id=entidad_id,
            error_message=str(error),
        )
        return

    notification_repository.registrar_envio(
        notification_type=tipo, channel="whatsapp", recipient=numero, body=mensaje,
        status="sent", related_entity_type="attendance_record", related_entity_id=entidad_id,
        sent_at=ahora().isoformat(),
    )


def notificar_llegada_tarde(empleado: Employee, registro: AttendanceRecord) -> None:
    """Mejor esfuerzo: si algo falta (número no configurado, aviso desactivado,
    proveedor no conectado) simplemente no hace nada — nunca lanza."""
    try:
        if not notification_repository.late_arrival_habilitado():
            return
    except Exception:  # noqa: BLE001 -- si falla la lectura de settings, no se bloquea el ingreso
        return

    ajustes = company_settings_repository.obtener()
    if not ajustes.whatsapp_admin_number:
        return

    mensaje = _mensaje_llegada_tarde(empleado, registro)
    _enviar(ajustes.whatsapp_admin_number, mensaje, tipo="late_arrival", entidad_id=registro.id)


def enviar_mensaje_prueba(numero: str) -> None:
    """Para el botón 'Enviar mensaje de prueba' en Configuración — a diferencia de
    notificar_llegada_tarde, aquí SÍ se propaga el error para que el admin lo vea."""
    if config.WHATSAPP_PROVIDER not in PROVEEDORES_SOPORTADOS:
        raise callmebot_provider.CallMeBotError(
            "Todavía no hay proveedor de WhatsApp conectado (falta whatsapp_provider/whatsapp_api_key en secrets.toml)."
        )
    mensaje = "✅ INFRATELCO — Este es un mensaje de prueba del Control de Asistencia. Si lo recibiste, quedó bien conectado."
    callmebot_provider.enviar_whatsapp(numero, mensaje, config.WHATSAPP_API_KEY)
    notification_repository.registrar_envio(
        notification_type="test", channel="whatsapp", recipient=numero, body=mensaje,
        status="sent", sent_at=ahora().isoformat(),
    )
