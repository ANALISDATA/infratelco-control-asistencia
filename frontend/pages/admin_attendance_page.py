import pandas as pd
import streamlit as st

from backend.models import User
from backend.repositories import attendance_repository
from backend.services.employees import employee_service
from backend.utils.timezone import ahora, formato_hora


def render(admin: User) -> None:
    st.header("Asistencia del día")

    fecha = st.date_input("Fecha", value=ahora().date())
    registros = attendance_repository.listar_por_fecha(fecha)
    registros_por_empleado = {r.employee_id: r for r in registros}

    empleados = employee_service.listar_empleados(solo_activos=True, por_pagina=1000)

    filas = []
    for empleado in empleados:
        registro = registros_por_empleado.get(empleado.id)
        if registro is None:
            filas.append({
                "Empleado": empleado.full_name, "Entrada": "—", "Estado": "No marcó",
                "Obra / trabajo": "—",
                "Dirección entrada": "—", "Salida": "—", "Dirección salida": "—",
            })
        else:
            filas.append({
                "Empleado": empleado.full_name,
                "Entrada": formato_hora(registro.check_in_at) if registro.check_in_at else "—",
                "Estado": "Puntual" if registro.check_in_status == "on_time" else "Tarde",
                "Obra / trabajo": registro.observation or "—",
                "Dirección entrada": registro.check_in_address or "—",
                "Salida": formato_hora(registro.check_out_at) if registro.check_out_at else "Sin salida",
                "Dirección salida": registro.check_out_address or "—",
            })

    if not filas:
        st.info("No hay empleados activos registrados todavía.")
        return

    df = pd.DataFrame(filas)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Puntuales", (df["Estado"] == "Puntual").sum())
    col2.metric("Tarde", (df["Estado"] == "Tarde").sum())
    col3.metric("No marcaron", (df["Estado"] == "No marcó").sum())
    col4.metric("Sin salida", (df["Salida"] == "Sin salida").sum())

    st.dataframe(df, width="stretch", hide_index=True)

    with st.expander("Ver coordenadas originales (latitud / longitud)"):
        filas_coords = [
            {
                "Empleado": next(e.full_name for e in empleados if e.id == r.employee_id),
                "Lat. entrada": r.check_in_latitude, "Lon. entrada": r.check_in_longitude,
                "Precisión entrada (m)": r.check_in_accuracy_m,
                "Lat. salida": r.check_out_latitude, "Lon. salida": r.check_out_longitude,
                "Precisión salida (m)": r.check_out_accuracy_m,
            }
            for r in registros
        ]
        if filas_coords:
            st.dataframe(pd.DataFrame(filas_coords), width="stretch", hide_index=True)
        else:
            st.caption("Sin registros con ubicación para esta fecha.")
