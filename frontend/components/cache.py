"""Caché de las consultas que se piden en casi cada pantalla de administrador
(empleados, horarios) -- sin esto, cualquier clic (marcar una casilla, cambiar de
pestaña) le vuelve a pedir la lista completa a Supabase, aunque no haya cambiado nada.
Con poco personal casi no se nota, pero con mala señal (típico en obra) esa espera de
ida y vuelta en cada clic se siente como que "la página no carga".

TTL corto (45s) para que nunca se sienta desactualizado, y además se limpia a mano
justo después de cualquier acción que cree/edite/desactive algo -- para que la propia
pantalla que acaba de hacer el cambio lo muestre al instante, no hasta que expire el
TTL. A propósito NO se cachean los registros de asistencia (attendance_records): eso
es lo que el administrador vigila en tiempo real durante el día.
"""
from __future__ import annotations

import streamlit as st

from backend.services.employees import employee_service
from backend.services.schedules import schedule_service

_TTL_SEGUNDOS = 45


@st.cache_data(ttl=_TTL_SEGUNDOS)
def empleados(solo_activos: bool) -> list:
    return employee_service.listar_empleados(solo_activos=solo_activos, por_pagina=2000)


@st.cache_data(ttl=_TTL_SEGUNDOS)
def empleados_operativos(solo_activos: bool) -> list:
    return employee_service.listar_empleados_operativos(solo_activos=solo_activos, por_pagina=2000)


@st.cache_data(ttl=_TTL_SEGUNDOS)
def horarios() -> list:
    return schedule_service.listar_horarios()


def limpiar_cache_empleados() -> None:
    empleados.clear()
    empleados_operativos.clear()


def limpiar_cache_horarios() -> None:
    horarios.clear()
