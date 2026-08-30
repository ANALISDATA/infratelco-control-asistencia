import pandas as pd
import streamlit as st

from backend.models import User
from backend.services.employees import employee_service
from frontend.components import charts


def render(admin: User) -> None:
    st.header("Dashboard")

    activos = employee_service.listar_empleados(solo_activos=True, por_pagina=1000)
    todos = employee_service.listar_empleados(solo_activos=False, por_pagina=1000)
    inactivos = len(todos) - len(activos)

    col1, col2, col3 = st.columns(3)
    col1.metric("Empleados activos", len(activos))
    col2.metric("Empleados inactivos", inactivos)
    col3.metric("Total empleados", len(todos))

    if not todos:
        st.info("Todavía no hay empleados registrados — los gráficos aparecen aquí apenas crees el primero, en la pestaña **Empleados**.")
    else:
        st.divider()
        col_a, col_b = st.columns([1, 1.4])

        with col_a:
            st.markdown("##### Estado del personal")
            df_estado = pd.DataFrame(
                {"Estado": ["Activos", "Inactivos"], "Empleados": [len(activos), inactivos]}
            )
            st.altair_chart(
                charts.barras_estado(
                    df_estado, "Estado", "Empleados",
                    dominio=["Activos", "Inactivos"],
                    rango=[charts.VERDE_ESTADO, charts.GRIS_ESTADO],
                ),
                use_container_width=True,
            )

        with col_b:
            st.markdown("##### Empleados por área")
            df_area = (
                pd.DataFrame([{"Área": e.department or "Sin asignar"} for e in todos])
                .value_counts("Área")
                .reset_index(name="Empleados")
            )
            st.altair_chart(
                charts.barras_magnitud(df_area, "Área", "Empleados"),
                use_container_width=True,
            )

    st.info(
        "Los indicadores de asistencia del día (ingresos, puntualidad, faltantes de salida) "
        "se habilitan en la Fase 2, cuando se construya el registro de ingreso/salida."
    )
