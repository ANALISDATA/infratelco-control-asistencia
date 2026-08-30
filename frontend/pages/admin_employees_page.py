import secrets
import string
from datetime import date

import pandas as pd
import streamlit as st

from backend.models import Employee, User
from backend.repositories import employee_repository, user_repository
from backend.services.auth import auth_service
from backend.services.employees import employee_service
from backend.services.schedules import schedule_service


def _generar_password_temporal() -> str:
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(12))


def _opciones_horario() -> dict[str, str | None]:
    horarios = schedule_service.listar_horarios()
    return {"Predeterminado de la empresa": None, **{h.name: h.id for h in horarios}}


def _formulario_crear(admin: User) -> None:
    with st.expander("➕ Crear nuevo empleado", expanded=False):
        opciones_horario = _opciones_horario()
        with st.form("form_crear_empleado", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo *")
                cedula = st.text_input("Cédula *")
                correo = st.text_input("Correo electrónico *")
                telefono = st.text_input("Teléfono")
            with col2:
                whatsapp = st.text_input("Número de WhatsApp")
                cargo = st.text_input("Cargo")
                area = st.text_input("Área / departamento")
                fecha_ingreso = st.date_input("Fecha de ingreso", value=date.today())
            horario_nombre = st.selectbox("Horario", list(opciones_horario.keys()))

            enviar = st.form_submit_button("Crear empleado", width="stretch")

        if enviar:
            if not nombre or not cedula or not correo:
                st.error("Nombre, cédula y correo son obligatorios.")
                return
            try:
                empleado, password_temporal = employee_service.crear_empleado(
                    admin,
                    Employee(
                        id=None,
                        full_name=nombre.strip(),
                        document_id=cedula.strip(),
                        email=correo.strip().lower(),
                        phone=telefono.strip() or None,
                        whatsapp_number=whatsapp.strip() or None,
                        position=cargo.strip() or None,
                        department=area.strip() or None,
                        hire_date=fecha_ingreso,
                        schedule_id=opciones_horario[horario_nombre],
                    ),
                )
            except (employee_repository.DocumentoDuplicado, employee_repository.CorreoDuplicado) as e:
                st.error(str(e))
                return
            except ValueError as e:
                st.error(str(e))
                return

            st.success(f"Empleado {empleado.full_name} creado correctamente.")
            st.warning(
                f"Contraseña temporal para **{empleado.email}**: `{password_temporal}`\n\n"
                "Entrégala al empleado por un canal seguro (en persona, llamada). "
                "Se le pedirá cambiarla en su primer ingreso. No se envía automáticamente "
                "porque todavía no hay un proveedor de correo/WhatsApp conectado."
            )


def _tabla_empleados(admin: User) -> None:
    solo_activos = st.checkbox("Mostrar solo empleados activos", value=True)
    empleados = employee_service.listar_empleados(solo_activos=solo_activos, por_pagina=500)

    if not empleados:
        st.info("No hay empleados registrados todavía.")
        return

    df = pd.DataFrame(
        [
            {
                "Nombre": e.full_name,
                "Cédula": e.document_id,
                "Correo": e.email,
                "Cargo": e.position,
                "Área": e.department,
                "Estado": "Activo" if e.is_active else "Inactivo",
                "_id": e.id,
            }
            for e in empleados
        ]
    )
    st.dataframe(df.drop(columns=["_id"]), width="stretch", hide_index=True)

    st.markdown("#### Editar / activar / desactivar")
    opciones = {f"{e.full_name} — {e.document_id}": e for e in empleados}
    seleccion = st.selectbox("Selecciona un empleado", ["—"] + list(opciones.keys()))
    if seleccion == "—":
        return

    empleado = opciones[seleccion]
    opciones_horario = _opciones_horario()
    nombre_horario_actual = next(
        (nombre for nombre, sid in opciones_horario.items() if sid == empleado.schedule_id),
        "Predeterminado de la empresa",
    )
    with st.form(f"form_editar_{empleado.id}"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo", value=empleado.full_name)
            correo = st.text_input("Correo electrónico", value=empleado.email or "")
            telefono = st.text_input("Teléfono", value=empleado.phone or "")
        with col2:
            cargo = st.text_input("Cargo", value=empleado.position or "")
            area = st.text_input("Área / departamento", value=empleado.department or "")
            whatsapp = st.text_input("WhatsApp", value=empleado.whatsapp_number or "")
        horario_nombre = st.selectbox(
            "Horario", list(opciones_horario.keys()),
            index=list(opciones_horario.keys()).index(nombre_horario_actual),
        )
        guardar = st.form_submit_button("Guardar cambios")

    if guardar:
        try:
            employee_service.actualizar_empleado(
                admin,
                empleado.id,
                {
                    "full_name": nombre.strip(),
                    "email": correo.strip().lower() or None,
                    "phone": telefono.strip() or None,
                    "position": cargo.strip() or None,
                    "department": area.strip() or None,
                    "whatsapp_number": whatsapp.strip() or None,
                    "schedule_id": opciones_horario[horario_nombre],
                },
            )
        except (employee_repository.DocumentoDuplicado, employee_repository.CorreoDuplicado) as e:
            st.error(str(e))
            return
        st.success("Cambios guardados.")
        st.rerun()

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if empleado.is_active and st.button("Desactivar empleado", key=f"desactivar_{empleado.id}"):
            employee_service.desactivar_empleado(admin, empleado.id)
            st.success(f"{empleado.full_name} desactivado.")
            st.rerun()
    with col_b:
        if not empleado.is_active and st.button("Reactivar empleado", key=f"activar_{empleado.id}"):
            employee_service.activar_empleado(admin, empleado.id)
            st.success(f"{empleado.full_name} reactivado.")
            st.rerun()
    with col_c:
        # Resuelve "no me sé la clave" al instante, sin depender de un correo que
        # todavía no está conectado (ver documentation/notifications.md) -- y sin
        # que la contraseña real de nadie se guarde en texto plano ni se muestre
        # nunca (regla de seguridad del proyecto).
        if st.button("🔑 Restablecer contraseña", key=f"reset_pw_{empleado.id}"):
            usuario_empleado = user_repository.obtener_por_documento(empleado.document_id)
            if usuario_empleado is None:
                st.error("Este empleado no tiene un usuario de acceso asociado.")
            else:
                password_temporal = _generar_password_temporal()
                auth_service.restablecer_password_administrador(admin, usuario_empleado, password_temporal)
                st.success(f"Contraseña restablecida para {empleado.full_name}.")
                st.warning(
                    f"Nueva contraseña temporal: `{password_temporal}`\n\n"
                    "Entrégasela por un canal seguro. Se le pedirá cambiarla en su "
                    "próximo ingreso — así queda registrado en Auditoría."
                )


def render(admin: User) -> None:
    st.header("Gestión de empleados")
    _formulario_crear(admin)
    st.divider()
    _tabla_empleados(admin)
