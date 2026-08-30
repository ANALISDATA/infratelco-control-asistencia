"""Interfaz que debe cumplir cualquier proveedor de Reverse Geocoding. Cambiar de
proveedor (Nominatim -> Google/Mapbox/HERE) significa agregar un archivo nuevo aquí
que implemente esta misma función — nada más en la app necesita cambiar.
"""
from __future__ import annotations

from typing import Protocol


class ReverseGeocodingProvider(Protocol):
    def obtener_direccion(self, latitud: float, longitud: float) -> str | None:
        """Devuelve una dirección legible, o None si no se pudo obtener.
        Nunca debe inventar una dirección (regla del proyecto) — None es una
        respuesta válida y esperada cuando el proveedor no tiene información."""
        ...
