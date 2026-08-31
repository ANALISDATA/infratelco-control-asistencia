"""La hora oficial de ingreso/salida SIEMPRE sale de aquí (servidor), nunca del reloj del
teléfono del empleado. Ver documentation/geolocation.md y regla #18 del encargo original.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from backend import config

BOGOTA = ZoneInfo(config.TIMEZONE)


def ahora() -> datetime:
    """Hora oficial actual en America/Bogota, con tzinfo — esta es la que se guarda
    como check_in_at / check_out_at."""
    return datetime.now(BOGOTA)


def hoy():
    return ahora().date()


def a_bogota(dt: datetime) -> datetime:
    """Convierte un datetime (con o sin tzinfo, se asume UTC si no la tiene, que es como
    Postgres/Supabase devuelve los timestamptz) a hora de Bogotá para mostrar en pantalla."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(BOGOTA)


def formato_hora(dt: datetime) -> str:
    return a_bogota(dt).strftime("%H:%M")


def formato_fecha(dt: datetime) -> str:
    return a_bogota(dt).strftime("%d/%m/%Y")


def formato_fecha_hora(dt: datetime) -> str:
    return a_bogota(dt).strftime("%d/%m/%Y %H:%M:%S")


def formato_horas_minutos(minutos: int | None) -> str:
    if minutos is None:
        return "—"
    horas, resto = divmod(minutos, 60)
    return f"{horas}h {resto:02d}m"
