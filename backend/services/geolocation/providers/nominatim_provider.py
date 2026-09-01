"""Reverse Geocoding gratuito con Nominatim (OpenStreetMap) — no requiere API key.

Política de uso de Nominatim (importante, es la condición para usarlo gratis):
  - Máximo ~1 solicitud por segundo. Esta app solo geocodifica en el momento exacto
    de un ingreso/salida (nunca tracking continuo), así que nunca se acerca a ese
    límite en uso normal.
  - Hay que identificarse con un User-Agent real (no el genérico de `requests`).
  - Nunca cachear/redistribuir el resultado como si fuera un servicio propio — aquí
    solo se usa para mostrar la dirección de ESE registro de asistencia.

Si Nominatim no responde, tarda demasiado, o no tiene dirección para esas
coordenadas: se devuelve None. Nunca se inventa una dirección (regla del proyecto).
"""
from __future__ import annotations

import time

import requests

_URL = "https://nominatim.openstreetmap.org/reverse"
_TIMEOUT_SEGUNDOS = 4
_REINTENTOS = 2  # 3 intentos en total -- casi toda falla de Nominatim es momentánea
_ESPERA_ENTRE_REINTENTOS_SEGUNDOS = 1
_USER_AGENT = "INFRATELCO-ControlAsistencia/1.0 (uso interno, contacto: isthosas@gmail.com)"


def _construir_direccion(address: dict) -> str | None:
    """Arma una dirección legible tipo "Calle 35A #46A-25, Copacabana, Antioquia,
    Colombia" a partir de los componentes estructurados que devuelve Nominatim.
    Si no hay suficientes componentes, se usa display_name como respaldo (fuera de
    esta función)."""
    via = address.get("road") or address.get("pedestrian")
    numero = address.get("house_number")
    calle = f"{via} #{numero}" if via and numero else via

    localidad = (
        address.get("suburb")
        or address.get("neighbourhood")
        or address.get("city_district")
        or address.get("town")
        or address.get("city")
        or address.get("municipality")
    )
    departamento = address.get("state")
    pais = address.get("country")

    partes = [p for p in (calle, localidad, departamento, pais) if p]
    return ", ".join(partes) if partes else None


def obtener_direccion(latitud: float, longitud: float) -> str | None:
    """Reintenta un par de veces antes de rendirse: un registro real (José Julián,
    01/09/2026) se quedó sin dirección porque Nominatim tardó más de lo esperado en un
    solo intento -- casi siempre es un bache momentáneo, no una caída real."""
    for intento in range(_REINTENTOS + 1):
        try:
            respuesta = requests.get(
                _URL,
                params={
                    "lat": latitud,
                    "lon": longitud,
                    "format": "jsonv2",
                    "addressdetails": 1,
                    "zoom": 18,
                },
                headers={"User-Agent": _USER_AGENT},
                timeout=_TIMEOUT_SEGUNDOS,
            )
            respuesta.raise_for_status()
            datos = respuesta.json()
        except (requests.RequestException, ValueError):
            if intento < _REINTENTOS:
                time.sleep(_ESPERA_ENTRE_REINTENTOS_SEGUNDOS)
                continue
            return None

        if not datos or "address" not in datos:
            return None

        direccion = _construir_direccion(datos["address"])
        return direccion or datos.get("display_name")

    return None
