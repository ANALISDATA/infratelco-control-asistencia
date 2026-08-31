import pandas as pd
import streamlit as st

from backend.models import User
from backend.repositories import audit_repository, user_repository
from backend.utils.timezone import formato_fecha_hora

_ACCIONES = {
    "auth.login_success": "Inicio de sesión",
    "auth.login_failed": "Intento de inicio de sesión fallido",
    "auth.password_changed": "Cambió su propia contraseña",
    "auth.password_reset_by_admin": "Administrador restableció la contraseña",
    "employee.create": "Empleado creado",
    "employee.update": "Empleado editado",
    "employee.deactivate": "Empleado desactivado",
    "employee.activate": "Empleado reactivado",
    "employee.bulk_schedule_assign": "Horario asignado a todos los empleados",
    "company_settings.update": "Configuración de la empresa actualizada",
    "attendance.check_in": "Registró ingreso",
    "attendance.check_out": "Registró salida",
    "schedule.create": "Horario creado",
    "schedule.update": "Horario editado",
    "schedule.deactivate": "Horario desactivado",
}


def render(admin: User) -> None:
    st.header("Auditoría")
    st.caption(
        "Registro inmutable de acciones administrativas y de inicio de sesión. "
        "No puede editarse ni borrarse desde la app — incluye cada vez que alguien "
        "cambia su contraseña, para que quede constancia de que sí pudo entrar."
    )

    pagina = st.number_input("Página", min_value=1, value=1, step=1)
    registros = audit_repository.listar(pagina=int(pagina), por_pagina=50)

    if not registros:
        st.info("No hay registros de auditoría todavía.")
        return

    # Se resuelve el correo de cada usuario una sola vez por página, no por fila.
    ids_unicos = {r["user_id"] for r in registros if r.get("user_id")}
    correos_por_id = {}
    for uid in ids_unicos:
        u = user_repository.obtener_por_id(uid)
        correos_por_id[uid] = u.email if u else uid

    df = pd.DataFrame(
        [
            {
                "Fecha": formato_fecha_hora(pd.to_datetime(r["created_at"])),
                "Acción": _ACCIONES.get(r["action"], r["action"]),
                "Usuario": correos_por_id.get(r.get("user_id"), "Sistema"),
                "Entidad": r["entity_type"],
                "Motivo": r.get("reason") or "—",
            }
            for r in registros
        ]
    )
    st.dataframe(df, width="stretch", hide_index=True)
