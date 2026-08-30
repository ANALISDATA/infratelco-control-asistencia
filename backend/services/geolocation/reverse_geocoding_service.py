"""Punto único desde el que el resto de la app pide una dirección a partir de
coordenadas. Cambiar de proveedor es cambiar esta función — nada más se entera."""
from __future__ import annotations

from backend import config


def obtener_direccion(latitud: float, longitud: float) -> str | None:
    proveedor = (config.GEOCODING_PROVIDER or "nominatim").lower()

    if proveedor == "nominatim":
        from backend.services.geolocation.providers import nominatim_provider

        return nominatim_provider.obtener_direccion(latitud, longitud)

    # Proveedor desconocido/no configurado: no se inventa nada, se guardan solo
    # coordenadas (regla del proyecto — ver documentation/geolocation.md).
    return None
