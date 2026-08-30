import streamlit as st

from backend.models import User
from backend.services.employees import employee_service


def render(admin: User) -> None:
    st.header("Dashboard")

    activos = employee_service.listar_empleados(solo_activos=True, por_pagina=1000)
    todos = employee_service.listar_empleados(solo_activos=False, por_pagina=1000)

    col1, col2, col3 = st.columns(3)
    col1.metric("Empleados activos", len(activos))
    col2.metric("Empleados inactivos", len(todos) - len(activos))
    col3.metric("Total empleados", len(todos))

    st.info(
        "Los indicadores de asistencia del día (ingresos, puntualidad, faltantes de salida) "
        "se habilitan en la Fase 2, cuando se construya el registro de ingreso/salida."
    )
