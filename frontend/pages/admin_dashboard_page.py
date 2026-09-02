from datetime import timedelta

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from backend.models import User
from backend.repositories import attendance_repository
from backend.utils.timezone import ahora
from frontend.components import branding, cache, charts


def render(admin: User) -> None:
    st.header("Dashboard")

    activos = cache.empleados(solo_activos=True)
    todos = cache.empleados(solo_activos=False)
    inactivos = len(todos) - len(activos)
    # Operativos = activos sin quienes tienen acceso de Administrador (ej. gerencia):
    # a ellos no se les espera que marquen, así que no cuentan como "No han marcado".
    activos_operativos = cache.empleados_operativos(solo_activos=True)

    hoy = ahora().date()
    registros_hoy = attendance_repository.listar_por_fecha(hoy)
    ids_con_registro = {r.employee_id for r in registros_hoy}

    puntuales = sum(1 for r in registros_hoy if r.check_in_status == "on_time")
    tarde = sum(1 for r in registros_hoy if r.check_in_status == "late")
    no_marcaron = sum(1 for e in activos_operativos if e.id not in ids_con_registro)
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
                oscuro=branding.es_oscuro(),
            ),
            width="stretch",
        )

    st.divider()
    st.markdown("##### Tendencia de asistencia (últimos 14 días)")
    dias = [hoy - timedelta(days=i) for i in range(13, -1, -1)]
    registros_rango = attendance_repository.listar_por_rango(dias[0], hoy)
    por_dia = {d: {"puntuales": 0, "tarde": 0} for d in dias}
    for r in registros_rango:
        if r.work_date in por_dia:
            if r.check_in_status == "on_time":
                por_dia[r.work_date]["puntuales"] += 1
            elif r.check_in_status == "late":
                por_dia[r.work_date]["tarde"] += 1
    df_tendencia = pd.DataFrame(
        [
            {"Día": d.strftime("%d/%m"), "Puntuales": v["puntuales"], "Tarde": v["tarde"]}
            for d, v in por_dia.items()
        ]
    )
    altura_tendencia = 300
    chart_tendencia = charts.tendencia_lineas(
        df_tendencia, "Día",
        series=[
            ("Puntuales", charts.VERDE_ESTADO, "Puntuales"),
            ("Tarde", charts.AMBAR_ESTADO, "Tarde"),
        ],
        oscuro=branding.es_oscuro(),
        altura=altura_tendencia,
    )
    # st.altair_chart (el puente Arrow de Streamlit) no calcula bien la escala en este
    # gráfico con varias series superpuestas -- eje vacío / "Infinite extent" en la
    # consola, verificado con Playwright. Se incrusta como HTML/vega-embed directo
    # (el mismo mecanismo ya probado y funcionando) para evitar ese puente por completo.
    components.html(chart_tendencia.to_html(), height=altura_tendencia + 40, scrolling=False)

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
                    oscuro=branding.es_oscuro(),
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
                charts.barras_magnitud(df_area, "Área", "Empleados", oscuro=branding.es_oscuro()),
                width="stretch",
            )
