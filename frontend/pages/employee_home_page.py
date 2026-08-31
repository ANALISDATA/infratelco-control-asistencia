import streamlit as st
from streamlit_js_eval import get_geolocation

from backend.models import Employee, User
from backend.repositories import attendance_repository, employee_repository
from backend.services.attendance import attendance_service
from backend.utils.timezone import ahora, formato_fecha, formato_hora, formato_horas_minutos
from frontend.components import branding


def _saludo(hora: int) -> str:
    if hora < 12:
        return "Buenos días"
    if hora < 18:
        return "Buenas tardes"
    return "Buenas noches"


def _bloque_ubicacion(clave: str) -> dict | None:
    """Explica por qué se pide la ubicación y la solicita solo cuando el empleado lo
    autoriza explícitamente (regla #16) — nunca automáticamente al cargar la página."""
    clave_solicitada = f"{clave}_solicitada"

    if not st.session_state.get(clave_solicitada):
        st.caption(
            "Para registrar tu asistencia, INFRATELCO necesita tu ubicación en este "
            "momento — no se hace seguimiento continuo."
        )
        if st.button("📍 Permitir ubicación", key=f"btn_{clave}", width="stretch"):
            st.session_state[clave_solicitada] = True
            st.rerun()
        return None

    resultado = get_geolocation(component_key=clave)
    if resultado is None:
        st.info("Esperando autorización del navegador…")
        return None
    if "error" in resultado:
        st.error(resultado["error"].get("message", "No se pudo obtener tu ubicación."))
        if st.button("Reintentar", key=f"retry_{clave}"):
            st.session_state.pop(clave_solicitada, None)
            st.rerun()
        return None

    precision = resultado.get("coords", {}).get("accuracy")
    st.success(f"Ubicación disponible (precisión: {precision:.0f} m)" if precision else "Ubicación disponible")
    return resultado


def _mostrar_confirmacion(titulo: str, hora, direccion: str | None, extra: str | None = None) -> None:
    st.success(f"✓ {titulo}")
    st.write(f"**Hora:** {formato_hora(hora)}")
    st.write(f"**Ubicación:** {direccion or 'No disponible'}")
    if extra:
        st.write(extra)


def render(usuario: User) -> None:
    branding.aplicar_estilo()
    branding.encabezado("Registro de asistencia")

    if not usuario.employee_id:
        st.warning("Tu usuario no tiene un empleado asociado. Contacta al administrador.")
        return

    empleado: Employee | None = employee_repository.obtener_por_id(usuario.employee_id)
    if empleado is None:
        st.warning("No se encontró tu información de empleado. Contacta al administrador.")
        return

    momento = ahora()
    st.markdown(f"#### {_saludo(momento.hour)}")
    st.markdown(f"## {empleado.full_name}")

    col1, col2 = st.columns(2)
    col1.metric("Fecha", formato_fecha(momento))
    col2.metric("Hora actual", momento.strftime("%H:%M:%S"))

    registro_hoy = attendance_repository.obtener_por_empleado_y_fecha(empleado.id, momento.date())

    st.divider()

    extra_ingreso = f"**Estado:** {'Puntual' if registro_hoy and registro_hoy.check_in_status == 'on_time' else 'Tarde'}" if registro_hoy else ""
    if registro_hoy and registro_hoy.observation:
        extra_ingreso += f"  \n**Obra / trabajo:** {registro_hoy.observation}"

    if registro_hoy and registro_hoy.check_out_at:
        st.markdown("### Jornada finalizada")
        _mostrar_confirmacion("Ingreso registrado", registro_hoy.check_in_at, registro_hoy.check_in_address,
                               extra=extra_ingreso)
        st.markdown("---")
        extra_salida = f"**Horas trabajadas:** {formato_horas_minutos(registro_hoy.worked_minutes)}"
        if registro_hoy.overtime_minutes:
            extra_salida += f"  \n**Horas extra:** {formato_horas_minutos(registro_hoy.overtime_minutes)}"
        _mostrar_confirmacion("Salida registrada", registro_hoy.check_out_at, registro_hoy.check_out_address,
                               extra=extra_salida)

    elif registro_hoy:
        _mostrar_confirmacion("Ingreso registrado", registro_hoy.check_in_at, registro_hoy.check_in_address,
                               extra=extra_ingreso)
        st.divider()
        st.markdown("### Registrar salida")
        resultado_gps = _bloque_ubicacion("gps_salida")
        if st.button("REGISTRAR SALIDA", type="primary", width="stretch"):
            if resultado_gps is None:
                st.error("Debes permitir tu ubicación antes de registrar la salida.")
            else:
                try:
                    resultado = attendance_service.registrar_salida(empleado, resultado_gps)
                except attendance_service.AttendanceError as error:
                    st.error(str(error))
                else:
                    for advertencia in resultado.advertencias:
                        st.warning(advertencia)
                    st.session_state.pop("gps_salida_solicitada", None)
                    st.rerun()

    else:
        st.markdown("### Registrar ingreso")
        comentario = st.text_input(
            "Obra o trabajo a realizar *",
            key="comentario_ingreso",
            placeholder="Ej: Obra Torre Norte — instalación eléctrica",
        )
        resultado_gps = _bloque_ubicacion("gps_ingreso")
        if st.button("REGISTRAR INGRESO", type="primary", width="stretch"):
            if not comentario or not comentario.strip():
                st.error("Debes indicar la obra o el trabajo que vas a realizar.")
            elif resultado_gps is None:
                st.error("Debes permitir tu ubicación antes de registrar el ingreso.")
            else:
                try:
                    resultado = attendance_service.registrar_ingreso(empleado, resultado_gps, comentario)
                except attendance_service.AttendanceError as error:
                    st.error(str(error))
                else:
                    for advertencia in resultado.advertencias:
                        st.warning(advertencia)
                    st.session_state.pop("gps_ingreso_solicitada", None)
                    st.rerun()

    st.divider()
    with st.expander("Mis últimos registros"):
        historicos = attendance_repository.listar_por_empleado(empleado.id, por_pagina=15)
        if not historicos:
            st.caption("Todavía no tienes registros.")
        for r in historicos:
            estado = "Puntual" if r.check_in_status == "on_time" else "Tarde" if r.check_in_status else "—"
            hora_salida = formato_hora(r.check_out_at) if r.check_out_at else "—"
            linea = (
                f"**{r.work_date.strftime('%d/%m/%Y')}** — Ingreso "
                f"{formato_hora(r.check_in_at) if r.check_in_at else '—'} ({estado}) · Salida {hora_salida}"
            )
            if r.worked_minutes:
                linea += f" · {formato_horas_minutos(r.worked_minutes)}"
                if r.overtime_minutes:
                    linea += f" ({formato_horas_minutos(r.overtime_minutes)} extra)"
            if r.observation:
                linea += f"  \n*{r.observation}*"
            st.write(linea)
