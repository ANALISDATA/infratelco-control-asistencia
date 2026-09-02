"""Indicadores — reemplaza la necesidad de Power BI para el día a día: todo el
análisis de asistencia (puntualidad, horas, ausentismo) queda dentro de la misma app,
con filtros de período y área. Power BI sigue siendo una opción aparte para quien
quiera conectarse directamente a la base de datos (ver powerbi/README.md), pero ya no
es un requisito para ver estos números.
"""
from __future__ import annotations

from datetime import timedelta

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from backend.models import User
from backend.repositories import attendance_repository
from backend.utils.timezone import hoy
from frontend.components import branding, cache, charts

_DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

_PRESETS = ["Este mes", "Mes anterior", "Últimos 30 días", "Últimos 7 días", "Personalizado"]


def _rango_por_preset(preset: str, hoy_actual) -> tuple:
    if preset == "Este mes":
        return hoy_actual.replace(day=1), hoy_actual
    if preset == "Mes anterior":
        fin = hoy_actual.replace(day=1) - timedelta(days=1)
        return fin.replace(day=1), fin
    if preset == "Últimos 30 días":
        return hoy_actual - timedelta(days=29), hoy_actual
    if preset == "Últimos 7 días":
        return hoy_actual - timedelta(days=6), hoy_actual
    return hoy_actual.replace(day=1), hoy_actual  # Personalizado: valor inicial, se ajusta abajo


def render(admin: User) -> None:
    st.header("Indicadores")
    st.caption("Puntualidad, horas trabajadas y ausentismo del período — todo dentro de la app, sin depender de Power BI.")

    todos = cache.empleados(solo_activos=False)
    operativos_activos = cache.empleados_operativos(solo_activos=True)
    if not todos:
        st.info("Todavía no hay empleados registrados — estos indicadores aparecen apenas crees el primero, en la pestaña **Empleados**.")
        return

    departamentos = sorted({e.department or "Sin asignar" for e in todos})
    hoy_actual = hoy()

    col_f1, col_f2, col_f3 = st.columns([1.1, 1.3, 1.4])
    with col_f1:
        preset = st.selectbox("Período", _PRESETS)
    fecha_inicio, fecha_fin = _rango_por_preset(preset, hoy_actual)
    with col_f2:
        if preset == "Personalizado":
            rango = st.date_input("Rango de fechas", value=(fecha_inicio, fecha_fin), max_value=hoy_actual)
            if isinstance(rango, tuple) and len(rango) == 2:
                fecha_inicio, fecha_fin = rango
        else:
            st.text_input("Rango de fechas", value=f"{fecha_inicio.strftime('%d/%m/%Y')} — {fecha_fin.strftime('%d/%m/%Y')}", disabled=True)
    with col_f3:
        deptos_sel = st.multiselect("Área", departamentos, default=departamentos)

    if fecha_inicio > fecha_fin:
        st.warning("La fecha inicial es posterior a la final.")
        return
    if not deptos_sel:
        st.info("Selecciona al menos un área para ver los indicadores.")
        return

    ids_incluidos = {e.id for e in todos if (e.department or "Sin asignar") in deptos_sel}
    empleados_por_id = {e.id: e for e in todos}

    registros = attendance_repository.listar_por_rango(fecha_inicio, fecha_fin)
    registros_f = [r for r in registros if r.employee_id in ids_incluidos]

    if not registros_f:
        st.info("No hay registros de asistencia en el período y área seleccionados.")
        return

    oscuro = branding.es_oscuro()

    total_registros = len(registros_f)
    puntuales = sum(1 for r in registros_f if r.check_in_status == "on_time")
    tarde = sum(1 for r in registros_f if r.check_in_status == "late")
    pct_puntualidad = round(100 * puntuales / total_registros) if total_registros else 0
    horas_trabajadas = sum((r.worked_minutes or 0) for r in registros_f) / 60
    horas_extra = sum((r.overtime_minutes or 0) for r in registros_f) / 60

    operativos_del_area = [e for e in operativos_activos if (e.department or "Sin asignar") in deptos_sel]
    ids_con_registro = {r.employee_id for r in registros_f}
    sin_ningun_registro = [e for e in operativos_del_area if e.id not in ids_con_registro]

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        branding.tarjeta_metrica("Registros", total_registros, "fact_check", "azul")
    with col2:
        branding.tarjeta_metrica("Puntualidad", f"{pct_puntualidad}%", "check_circle", "verde")
    with col3:
        branding.tarjeta_metrica("Llegadas tarde", tarde, "schedule", "dorado")
    with col4:
        branding.tarjeta_metrica("Horas trabajadas", f"{horas_trabajadas:,.0f} h", "timer", "azul")
    with col5:
        branding.tarjeta_metrica("Sin registros", len(sin_ningun_registro), "person_off", "rojo",
                                  ayuda="Activos sin ningún ingreso en el período")

    st.write("")

    por_dia = {}
    dia_actual = fecha_inicio
    while dia_actual <= fecha_fin:
        por_dia[dia_actual] = {"puntuales": 0, "tarde": 0}
        dia_actual += timedelta(days=1)
    for r in registros_f:
        if r.work_date in por_dia:
            if r.check_in_status == "on_time":
                por_dia[r.work_date]["puntuales"] += 1
            elif r.check_in_status == "late":
                por_dia[r.work_date]["tarde"] += 1
    df_tendencia = pd.DataFrame(
        [{"Día": d.strftime("%d/%m"), "Puntuales": v["puntuales"], "Tarde": v["tarde"]} for d, v in por_dia.items()]
    )
    altura_tendencia = 280
    chart_tendencia = charts.tendencia_lineas(
        df_tendencia, "Día",
        series=[("Puntuales", charts.VERDE_ESTADO, "Puntuales"), ("Tarde", charts.AMBAR_ESTADO, "Tarde")],
        oscuro=oscuro, altura=altura_tendencia,
    )
    with st.container(key="tarjeta_grafico_indic_tendencia"):
        st.markdown("###### Tendencia diaria")
        components.html(chart_tendencia.to_html(), height=altura_tendencia + 40, scrolling=False)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(key="tarjeta_grafico_indic_tarde"):
            st.markdown("###### Llegadas tarde por empleado")
            conteo_tarde: dict[str, int] = {}
            for r in registros_f:
                if r.check_in_status == "late":
                    conteo_tarde[r.employee_id] = conteo_tarde.get(r.employee_id, 0) + 1
            if conteo_tarde:
                df_tarde = pd.DataFrame(
                    [{"Empleado": empleados_por_id[eid].full_name, "Llegadas tarde": c}
                     for eid, c in conteo_tarde.items() if eid in empleados_por_id]
                ).sort_values("Llegadas tarde", ascending=False).head(10)
                st.altair_chart(
                    charts.barras_magnitud(df_tarde, "Empleado", "Llegadas tarde",
                                            color=charts.AMBAR_ESTADO, altura=260, oscuro=oscuro),
                    width="stretch",
                )
            else:
                st.caption("Nadie llegó tarde en este período. 🎉")
    with col_b:
        with st.container(key="tarjeta_grafico_indic_horas"):
            st.markdown("###### Horas trabajadas por empleado")
            horas_por_empleado: dict[str, float] = {}
            for r in registros_f:
                if r.worked_minutes:
                    horas_por_empleado[r.employee_id] = horas_por_empleado.get(r.employee_id, 0) + r.worked_minutes / 60
            if horas_por_empleado:
                df_horas = pd.DataFrame(
                    [{"Empleado": empleados_por_id[eid].full_name, "Horas": round(h, 1)}
                     for eid, h in horas_por_empleado.items() if eid in empleados_por_id]
                ).sort_values("Horas", ascending=False)
                st.altair_chart(
                    charts.barras_magnitud(df_horas, "Empleado", "Horas", altura=260, oscuro=oscuro),
                    width="stretch",
                )
            else:
                st.caption("Todavía no hay salidas registradas en este período.")

    with st.container(key="tarjeta_grafico_indic_semana"):
        st.markdown("###### Llegadas tarde por día de la semana")
        conteo_semana = {d: 0 for d in _DIAS_SEMANA}
        for r in registros_f:
            if r.check_in_status == "late":
                conteo_semana[_DIAS_SEMANA[r.work_date.weekday()]] += 1
        df_semana = pd.DataFrame([{"Día": d, "Llegadas tarde": c} for d, c in conteo_semana.items()])
        st.altair_chart(
            charts.barras_magnitud(df_semana, "Día", "Llegadas tarde", color=charts.AMBAR_ESTADO,
                                    altura=240, oscuro=oscuro),
            width="stretch",
        )

    if sin_ningun_registro:
        with st.expander(f"Ver los {len(sin_ningun_registro)} empleados sin registros en el período"):
            for e in sin_ningun_registro:
                st.write(f"- {e.full_name} ({e.department or 'Sin asignar'})")
