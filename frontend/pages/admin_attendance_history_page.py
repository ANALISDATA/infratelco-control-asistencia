from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from backend.models import User
from backend.repositories import attendance_repository
from backend.services.attendance import attendance_service, correction_service
from backend.services.reports import excel_service
from backend.utils.timezone import BOGOTA, ahora, formato_hora, formato_horas_minutos
from frontend.components import branding, cache

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

    # Registros con coordenadas GPS (siempre se guardan bien, vienen del celular) pero
    # sin dirección de texto -- pasa cuando el servicio gratuito de direcciones no
    # respondió a tiempo justo en ese momento (ver nominatim_provider). No se pierde
    # nada: siempre se puede reintentar.
    faltantes = [
        r for r in registros
        if (r.check_in_latitude is not None and not r.check_in_address)
        or (r.check_out_latitude is not None and not r.check_out_address)
    ]
    if faltantes:
        col_aviso, col_boton = st.columns([3, 1])
        with col_aviso:
            st.warning(f"{len(faltantes)} registro(s) en este rango tienen ubicación pero sin dirección de texto.")
        with col_boton:
            if st.button("Completar direcciones", icon=":material/refresh:"):
                with st.spinner("Consultando direcciones faltantes..."):
                    completados = attendance_service.completar_direcciones_faltantes(faltantes)
                st.success(f"Se completaron {completados} de {len(faltantes)} direcciones.")
                st.rerun()

    # solo_activos=False: un reporte de un rango pasado debe incluir a alguien que ya
    # se desactivó en el medio (ej. renunció a mitad de la quincena) -- sus registros
    # de esos días siguen siendo reales.
    empleados = cache.empleados(solo_activos=False)
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
    with col1:
        branding.tarjeta_metrica("Registros", len(filas), "list_alt", "azul")
    with col2:
        branding.tarjeta_metrica("Puntuales", (df["Estado"] == "Puntual").sum(), "check_circle", "verde")
    with col3:
        branding.tarjeta_metrica("Tarde", (df["Estado"] == "Tarde").sum(), "schedule", "dorado")
    with col4:
        branding.tarjeta_metrica("Sin salida", (df["Salida"] == "Sin salida").sum(), "logout", "rojo")

    st.dataframe(
        df, width="stretch", hide_index=True,
        column_config={
            col: st.column_config.TextColumn(width=ancho) for col, ancho in _ANCHOS_COLUMNAS.items()
        },
    )

    subtitulo = f"Del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
    excel_bytes = excel_service.generar_reporte_asistencia(subtitulo, filas)
    st.download_button(
        "Descargar Excel del rango", icon=":material/download:",
        data=excel_bytes,
        file_name=f"infratelco_asistencia_{fecha_inicio.isoformat()}_a_{fecha_fin.isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.divider()
    _seccion_corregir_registro(admin, registros_ordenados, nombre_por_id)


def _seccion_corregir_registro(admin: User, registros_ordenados: list, nombre_por_id: dict) -> None:
    st.subheader("Corregir un registro")
    st.caption(
        "Para cuando un empleado marcó mal, olvidó marcar la salida, o necesita una "
        "justificación (cita médica, permiso, etc.). El dato original nunca se borra "
        "-- queda en la auditoría -- y toda corrección pide un motivo obligatorio."
    )

    opciones = {
        r.id: (
            f"{r.work_date.strftime('%d/%m/%Y')} — {nombre_por_id.get(r.employee_id, '(empleado eliminado)')} "
            f"(entrada: {formato_hora(r.check_in_at) if r.check_in_at else '—'}, "
            f"salida: {formato_hora(r.check_out_at) if r.check_out_at else 'sin salida'})"
        )
        for r in registros_ordenados
    }
    registro_id = st.selectbox(
        "Selecciona el registro", options=list(opciones.keys()), format_func=lambda rid: opciones[rid],
    )
    registro = next(r for r in registros_ordenados if r.id == registro_id)

    with st.form("form_correccion_asistencia"):
        col1, col2 = st.columns(2)
        with col1:
            corregir_entrada = st.checkbox("Corregir hora de entrada")
            hora_entrada_nueva = st.time_input(
                "Nueva hora de entrada",
                value=registro.check_in_at.time() if registro.check_in_at else None,
            )
        with col2:
            corregir_salida = st.checkbox("Corregir hora de salida")
            hora_salida_nueva = st.time_input(
                "Nueva hora de salida",
                value=registro.check_out_at.time() if registro.check_out_at else None,
            )

        tipo = st.selectbox(
            "Tipo de justificación",
            options=list(correction_service.TIPOS_JUSTIFICACION.keys()),
            format_func=lambda k: correction_service.TIPOS_JUSTIFICACION[k],
        )
        motivo = st.text_area("Motivo (obligatorio)")

        guardar = st.form_submit_button("Guardar corrección", icon=":material/edit_note:")

    if guardar:
        if corregir_entrada and hora_entrada_nueva is None:
            st.error("Indica la nueva hora de entrada.")
            return
        if corregir_salida and hora_salida_nueva is None:
            st.error("Indica la nueva hora de salida.")
            return

        nuevo_check_in = (
            datetime.combine(registro.work_date, hora_entrada_nueva, tzinfo=BOGOTA) if corregir_entrada else None
        )
        nuevo_check_out = (
            datetime.combine(registro.work_date, hora_salida_nueva, tzinfo=BOGOTA) if corregir_salida else None
        )
        try:
            correction_service.corregir_registro(
                admin, registro.id,
                nuevo_check_in=nuevo_check_in, nuevo_check_out=nuevo_check_out,
                tipo=tipo, motivo=motivo,
            )
        except correction_service.CorrectionError as error:
            st.error(str(error))
        else:
            st.success("Registro corregido.")
            st.rerun()
