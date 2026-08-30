"""Convierte lo que devuelve el navegador (streamlit_js_eval.get_geolocation()) en
una ubicación utilizable, con dirección legible cuando es posible.

No decide aquí si la precisión es suficiente ni qué hacer si falla — eso depende de
la configuración de la empresa (mínimo de precisión, bloquear/permitir con
advertencia) y vive en backend/services/attendance, que es quien conoce esas reglas
de negocio.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from backend.services.geolocation import reverse_geocoding_service
from backend.utils.timezone import ahora

# Códigos estándar de GeolocationPositionError (spec W3C, iguales en todo navegador).
_MENSAJES_ERROR = {
    1: "No se pudo registrar la asistencia: denegaste el permiso de ubicación. "
       "Actívalo en la configuración del navegador e intenta de nuevo.",
    2: "No se pudo obtener tu ubicación (GPS apagado o sin señal). Verifica que el "
       "GPS esté activado e intenta de nuevo.",
    3: "Se agotó el tiempo esperando tu ubicación. Intenta de nuevo.",
}


class UbicacionError(Exception):
    """Mensaje ya listo para mostrarle al empleado — nunca expone detalles técnicos."""


@dataclass
class Ubicacion:
    latitud: float
    longitud: float
    precision_m: float
    capturada_en: datetime
    direccion: str | None


def procesar_resultado_navegador(resultado: dict) -> Ubicacion:
    """`resultado` es el dict que devuelve streamlit_js_eval.get_geolocation().
    Lanza UbicacionError con un mensaje seguro para mostrar si el navegador no pudo
    dar la ubicación; nunca inventa coordenadas."""
    if "error" in resultado:
        codigo = resultado["error"].get("code")
        raise UbicacionError(
            _MENSAJES_ERROR.get(codigo, "No se pudo obtener tu ubicación. Intenta de nuevo.")
        )

    coords = resultado.get("coords") or {}
    latitud = coords.get("latitude")
    longitud = coords.get("longitude")
    precision = coords.get("accuracy")

    if latitud is None or longitud is None:
        raise UbicacionError("No se pudo leer la ubicación del dispositivo. Intenta de nuevo.")

    direccion = reverse_geocoding_service.obtener_direccion(latitud, longitud)

    return Ubicacion(
        latitud=latitud,
        longitud=longitud,
        precision_m=precision if precision is not None else 0.0,
        capturada_en=ahora(),
        direccion=direccion,
    )
