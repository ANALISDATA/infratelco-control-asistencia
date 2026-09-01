import pandas as pd
import streamlit as st

from backend.models import User
from backend.repositories import attendance_repository
from backend.services.employees import employee_service
from backend.services.reports import excel_service
from backend.utils.timezone import ahora, formato_hora, formato_horas_minutos


def _fila(fecha_str: str, nombre: str, registro) -> dict:
    if registro is None:
        return {
            "Fecha": fecha_str, "Empleado": nombre, "Entrada": "—", "Estado": "No marcó",
            "Salida": "—", "Horas trab.": "—", "Horas extra": "—",
            "Obra / trabajo": "—", "Dirección entrada": "—", "Dirección salida": "—",
        }
    return {
        "Fecha": fecha_str,
        "Empleado": nombre,
        "Entrada": formato_hora(registro.check_in_at) if registro.check_in_at else "—",
        "Estado": "Puntual" if registro.check_in_status == "on_time" else "Tarde",
        "Salida": formato_hora(registro.check_out_at) if registro.check_out_at else "Sin salida",
        "Horas trab.": formato_horas_minutos(registro.worked_minutes),
        "Horas extra": formato_horas_minutos(registro.overtime_minutes) if registro.overtime_minutes else "—",
        "Obra / trabajo": registro.observation or "—",
        "Dirección entrada": registro.check_in_address or "—",
        "Dirección salida": registro.check_out_address or "—",
    }


def render(admin: User) -> None:
    st.header("Asistencia del día")

    fecha = st.date_input("Fecha", value=ahora().date())
    registros = attendance_repository.listar_por_fecha(fecha)
    registros_por_empleado = {r.employee_id: r for r in registros}

    # operativos = sin quienes tienen acceso de Administrador (ej. gerencia): a ellos
    # no se les espera que marquen, así que no deben salir como "No marcó".
    empleados_activos = employee_service.listar_empleados_operativos(solo_activos=True, por_pagina=1000)
    # Para resolver nombres se usan TODOS los empleados (no solo activos): un registro
    # real de alguien que se desactivó después (ej. renunció el mismo día que trabajó)
    # no debe desaparecer ni reventar la pantalla por no encontrar su nombre.
    todos_los_empleados = employee_service.listar_empleados(solo_activos=False, por_pagina=2000)
    nombre_por_id = {e.id: e.full_name for e in todos_los_empleados}

    fecha_str = fecha.strftime("%d/%m/%Y")
    filas = []
    ids_incluidos = set()
    for empleado in empleados_activos:
        ids_incluidos.add(empleado.id)
        filas.append(_fila(fecha_str, empleado.full_name, registros_por_empleado.get(empleado.id)))

    # Registros reales de empleados ya inactivos para esta fecha -- se muestran igual,
    # al final, en vez de ocultarse silenciosamente.
    for r in registros:
        if r.employee_id not in ids_incluidos:
            ids_incluidos.add(r.employee_id)
            nombre = nombre_por_id.get(r.employee_id, "(empleado eliminado)")
            filas.append(_fila(fecha_str, f"{nombre} (inactivo)", r))

    if not filas:
        st.info("No hay empleados activos registrados todavía.")
        return

    df = pd.DataFrame(filas)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Puntuales", (df["Estado"] == "Puntual").sum())
    col2.metric("Tarde", (df["Estado"] == "Tarde").sum())
    col3.metric("No marcaron", (df["Estado"] == "No marcó").sum())
    col4.metric("Sin salida", (df["Salida"] == "Sin salida").sum())

    # Columnas cortas (hora, estado, horas) angostas a propósito -- para que quepa todo
    # sin tener que deslizar la tabla, incluyendo Empleado en cada fila (con más de 20
    # personas no sirve de nada ver "Obra copacabana" sin saber de quién es).
    st.dataframe(
        df, width="stretch", hide_index=True,
        column_config={
            "Fecha": st.column_config.TextColumn(width="small"),
            "Empleado": st.column_config.TextColumn(width="medium"),
            "Entrada": st.column_config.TextColumn(width="small"),
            "Estado": st.column_config.TextColumn(width="small"),
            "Salida": st.column_config.TextColumn(width="small"),
            "Horas trab.": st.column_config.TextColumn(width="small"),
            "Horas extra": st.column_config.TextColumn(width="small"),
            "Obra / trabajo": st.column_config.TextColumn(width="medium"),
            "Dirección entrada": st.column_config.TextColumn(width="medium"),
            "Dirección salida": st.column_config.TextColumn(width="medium"),
        },
    )

    excel_bytes = excel_service.generar_reporte_asistencia(f"Fecha: {fecha_str}", filas)
    st.download_button(
        "📥 Descargar Excel",
        data=excel_bytes,
        file_name=f"infratelco_asistencia_{fecha.isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    with st.expander("Ver coordenadas originales (latitud / longitud)"):
        filas_coords = [
            {
                "Empleado": nombre_por_id.get(r.employee_id, "(empleado eliminado)"),
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
