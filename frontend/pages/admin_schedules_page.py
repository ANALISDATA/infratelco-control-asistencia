from datetime import time as dtime

import streamlit as st

from backend.models import User
from backend.services.employees import employee_service
from backend.services.schedules import schedule_service

DIAS = [(1, "Lunes"), (2, "Martes"), (3, "Miércoles"), (4, "Jueves"), (5, "Viernes"), (6, "Sábado"), (7, "Domingo")]


def _formulario_dias(prefijo: str, dias_existentes: dict) -> list[dict]:
    dias = []
    for weekday, nombre in DIAS:
        existente = dias_existentes.get(weekday)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            laboral = st.checkbox(nombre, value=(existente.is_working_day if existente else weekday <= 5),
                                   key=f"{prefijo}_lab_{weekday}")
        with col2:
            # Sin disabled=not laboral a propósito: estos campos viven dentro de un
            # st.form, y los widgets de un form no vuelven a correr el script hasta que
            # se envía -- el checkbox de al lado quedaba marcado pero la hora se veía
            # "congelada" en gris hasta guardar (bug real reportado). El día sí queda
            # bien guardado: start_time/end_time se ponen en None si laboral es falso,
            # sin importar qué muestre el campo en pantalla.
            entrada = st.time_input(
                "Entrada", value=(existente.start_time if existente and existente.start_time else dtime(8, 0)),
                key=f"{prefijo}_in_{weekday}", label_visibility="collapsed",
            )
        with col3:
            salida = st.time_input(
                "Salida", value=(existente.end_time if existente and existente.end_time else dtime(17, 0)),
                key=f"{prefijo}_out_{weekday}", label_visibility="collapsed",
            )
        dias.append({
            "weekday": weekday, "is_working_day": laboral,
            "start_time": entrada.isoformat() if laboral else None,
            "end_time": salida.isoformat() if laboral else None,
        })
    return dias


def render(admin: User) -> None:
    st.header("Horarios")

    with st.expander("➕ Crear nuevo horario"):
        with st.form("form_crear_horario"):
            nombre = st.text_input("Nombre del horario *", placeholder="Ej. Horario Administrativo")
            tolerancia = st.number_input("Tolerancia (minutos)", min_value=0, max_value=120, value=10)
            st.caption("Día · hora de entrada · hora de salida")
            dias = _formulario_dias("nuevo", {})
            crear = st.form_submit_button("Crear horario", width="stretch")

        if crear:
            if not nombre.strip():
                st.error("El nombre es obligatorio.")
            else:
                schedule_service.crear_horario(admin, nombre.strip(), int(tolerancia), dias)
                st.success(f"Horario «{nombre}» creado.")
                st.rerun()

    st.divider()
    horarios = schedule_service.listar_horarios()
    if not horarios:
        st.info("No hay horarios creados todavía. Mientras tanto, se usa el horario predeterminado de Configuración.")
        return

    opciones = {h.name: h.id for h in horarios}
    seleccion = st.selectbox("Editar horario existente", ["—"] + list(opciones.keys()))
    if seleccion == "—":
        return

    horario = schedule_service.obtener_horario(opciones[seleccion])
    dias_existentes = {d.weekday: d for d in (horario.dias or [])}

    with st.form(f"form_editar_{horario.id}"):
        nombre = st.text_input("Nombre del horario", value=horario.name)
        tolerancia = st.number_input("Tolerancia (minutos)", min_value=0, max_value=120,
                                      value=horario.tolerance_minutes)
        st.caption("Día · hora de entrada · hora de salida")
        dias = _formulario_dias("editar", dias_existentes)
        guardar = st.form_submit_button("Guardar cambios", width="stretch")

    if guardar:
        schedule_service.actualizar_horario(admin, horario.id, nombre.strip(), int(tolerancia), dias)
        st.success("Horario actualizado.")
        st.rerun()

    st.markdown("#### Asignar este horario")
    st.caption(
        "Por defecto cada empleado puede tener su propio horario (o ninguno, y usar "
        "el predeterminado de Configuración). Elige si este horario es igual para "
        "todo el personal, o distinto solo para una persona en particular."
    )
    modo = st.radio(
        "¿A quién se lo asignas?",
        ["A todos los empleados activos", "A una persona en particular"],
        key=f"modo_asignacion_{horario.id}", horizontal=True, label_visibility="collapsed",
    )

    if modo == "A todos los empleados activos":
        if st.button("Aplicar a todos los empleados activos", key=f"aplicar_todos_{horario.id}"):
            total = employee_service.asignar_horario_a_todos(admin, horario.id)
            st.success(f"Horario «{horario.name}» asignado a {total} empleado(s) activo(s).")
    else:
        # operativos: quienes de verdad marcan asistencia -- un administrador con
        # ficha de empleado (ej. gerencia) no tiene horario que cumplir.
        empleados_operativos = employee_service.listar_empleados_operativos(solo_activos=True, por_pagina=1000)
        if not empleados_operativos:
            st.info("No hay empleados activos para asignarles un horario individual.")
        else:
            opciones_empleado = {e.full_name: e.id for e in empleados_operativos}
            col_select, col_boton = st.columns([2, 1])
            with col_select:
                empleado_elegido = st.selectbox(
                    "Empleado", list(opciones_empleado.keys()), key=f"empleado_para_horario_{horario.id}",
                    label_visibility="collapsed",
                )
            with col_boton:
                if st.button("Asignar a esta persona", key=f"aplicar_uno_{horario.id}", width="stretch"):
                    employee_service.actualizar_empleado(
                        admin, opciones_empleado[empleado_elegido], {"schedule_id": horario.id}
                    )
                    st.success(f"Horario «{horario.name}» asignado a {empleado_elegido}.")

    st.divider()
    if st.button("Desactivar este horario", key=f"desactivar_{horario.id}"):
        schedule_service.desactivar_horario(admin, horario.id)
        st.success("Horario desactivado.")
        st.rerun()
