import pandas as pd
import streamlit as st

from backend.models import User
from backend.repositories import attendance_repository
from backend.services.employees import employee_service
from backend.utils.timezone import ahora
from frontend.components import charts


def render(admin: User) -> None:
    st.header("Dashboard")

    activos = employee_service.listar_empleados(solo_activos=True, por_pagina=1000)
    todos = employee_service.listar_empleados(solo_activos=False, por_pagina=1000)
    inactivos = len(todos) - len(activos)

    hoy = ahora().date()
    registros_hoy = attendance_repository.listar_por_fecha(hoy)
    ids_con_registro = {r.employee_id for r in registros_hoy}

    puntuales = sum(1 for r in registros_hoy if r.check_in_status == "on_time")
    tarde = sum(1 for r in registros_hoy if r.check_in_status == "late")
    no_marcaron = sum(1 for e in activos if e.id not in ids_con_registro)
    sin_salida = sum(1 for r in registros_hoy if r.check_in_at and not r.check_out_at)

    st.markdown("##### Asistencia de hoy")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Ingresos registrados", len(registros_hoy))
    col2.metric("Puntuales", puntuales)
    col3.metric("Llegaron tarde", tarde)
    col4.metric("No han marcado", no_marcaron)
    col5.metric("Sin salida", sin_salida)

    if registros_hoy or activos:
        st.altair_chart(
            charts.barras_estado(
                pd.DataFrame({
                    "Estado": ["Puntuales", "Tarde", "No marcaron"],
                    "Empleados": [puntuales, tarde, no_marcaron],
                }),
                "Estado", "Empleados",
                dominio=["Puntuales", "Tarde", "No marcaron"],
                rango=[charts.VERDE_ESTADO, charts.AMBAR_ESTADO, charts.GRIS_ESTADO],
                altura=200,
            ),
            width="stretch",
        )

    st.divider()
    st.markdown("##### Personal")
    col1, col2, col3 = st.columns(3)
    col1.metric("Empleados activos", len(activos))
    col2.metric("Empleados inactivos", inactivos)
    col3.metric("Total empleados", len(todos))

    if not todos:
        st.info("Todavía no hay empleados registrados — los gráficos aparecen aquí apenas crees el primero, en la pestaña **Empleados**.")
    else:
        col_a, col_b = st.columns([1, 1.4])
        with col_a:
            st.markdown("###### Estado del personal")
            df_estado = pd.DataFrame(
                {"Estado": ["Activos", "Inactivos"], "Empleados": [len(activos), inactivos]}
            )
            st.altair_chart(
                charts.barras_estado(
                    df_estado, "Estado", "Empleados",
                    dominio=["Activos", "Inactivos"],
                    rango=[charts.VERDE_ESTADO, charts.GRIS_ESTADO],
                ),
                width="stretch",
            )
        with col_b:
            st.markdown("###### Empleados por área")
            df_area = (
                pd.DataFrame([{"Área": e.department or "Sin asignar"} for e in todos])
                .value_counts("Área")
                .reset_index(name="Empleados")
            )
            st.altair_chart(
                charts.barras_magnitud(df_area, "Área", "Empleados"),
                width="stretch",
            )
