from datetime import timedelta

import pandas as pd
import streamlit as st

from backend.models import User
from backend.repositories import attendance_repository
from backend.services.employees import employee_service
from backend.services.reports import excel_service
from backend.utils.timezone import ahora, formato_hora, formato_horas_minutos

_ANCHOS_COLUMNAS = {
    "Fecha": "small",
    "Empleado": "medium",
    "Entrada": "small",
    "Estado": "small",
    "Salida": "small",
    "Horas trab.": "small",
    "Horas extra": "small",
    "Obra / trabajo": "medium",
    "Dirección entrada": "medium",
    "Dirección salida": "medium",
}


def render(admin: User) -> None:
    st.header("Histórico de asistencia")
    st.caption(
        "Todos los registros quedan guardados siempre -- \"Asistencia del día\" solo "
        "muestra un día a la vez. Aquí se saca el reporte de un rango de fechas (por "
        "ejemplo, una quincena) para descargarlo completo en Excel."
    )

    hoy = ahora().date()
    rango = st.date_input("Rango de fechas", value=(hoy - timedelta(days=14), hoy))

    if not isinstance(rango, tuple) or len(rango) != 2:
        st.info("Selecciona una fecha de inicio y una de fin.")
        return
    fecha_inicio, fecha_fin = rango
    if fecha_inicio > fecha_fin:
        st.error("La fecha de inicio no puede ser después de la fecha de fin.")
        return

    registros = attendance_repository.listar_por_rango(fecha_inicio, fecha_fin)
    if not registros:
        st.info("No hay registros de asistencia en ese rango de fechas.")
        return

    # solo_activos=False: un reporte de un rango pasado debe incluir a alguien que ya
    # se desactivó en el medio (ej. renunció a mitad de la quincena) -- sus registros
    # de esos días siguen siendo reales.
    empleados = employee_service.listar_empleados(solo_activos=False, por_pagina=2000)
    nombre_por_id = {e.id: e.full_name for e in empleados}

    registros_ordenados = sorted(
        registros, key=lambda r: (r.work_date, nombre_por_id.get(r.employee_id, ""))
    )

    filas = [
        {
            "Fecha": r.work_date.strftime("%d/%m/%Y"),
            "Empleado": nombre_por_id.get(r.employee_id, "(empleado eliminado)"),
            "Entrada": formato_hora(r.check_in_at) if r.check_in_at else "—",
            "Estado": (
                "Puntual" if r.check_in_status == "on_time"
                else "Tarde" if r.check_in_status == "late" else "—"
            ),
            "Salida": formato_hora(r.check_out_at) if r.check_out_at else "Sin salida",
            "Horas trab.": formato_horas_minutos(r.worked_minutes),
            "Horas extra": formato_horas_minutos(r.overtime_minutes) if r.overtime_minutes else "—",
            "Obra / trabajo": r.observation or "—",
            "Dirección entrada": r.check_in_address or "—",
            "Dirección salida": r.check_out_address or "—",
        }
        for r in registros_ordenados
    ]

    df = pd.DataFrame(filas)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros", len(filas))
    col2.metric("Puntuales", (df["Estado"] == "Puntual").sum())
    col3.metric("Tarde", (df["Estado"] == "Tarde").sum())
    col4.metric("Sin salida", (df["Salida"] == "Sin salida").sum())

    st.dataframe(
        df, width="stretch", hide_index=True,
        column_config={
            col: st.column_config.TextColumn(width=ancho) for col, ancho in _ANCHOS_COLUMNAS.items()
        },
    )

    subtitulo = f"Del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
    excel_bytes = excel_service.generar_reporte_asistencia(subtitulo, filas)
    st.download_button(
        "📥 Descargar Excel del rango",
        data=excel_bytes,
        file_name=f"infratelco_asistencia_{fecha_inicio.isoformat()}_a_{fecha_fin.isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
