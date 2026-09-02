"""Punto de entrada de la app. Se ejecuta con:  streamlit run frontend/app.py

El enrutamiento por rol usa st.navigation/st.Page (Streamlit >= 1.36) en vez del
autodescubrimiento clásico de la carpeta pages/, precisamente para que cada página
quede controlada por este archivo y nadie pueda llegar a una pantalla de administrador
sin haber pasado por la verificación de sesión y rol de abajo.

IMPORTANTE: st.navigation() se llama SIEMPRE, en cualquier estado (sin sesión, cambio
de contraseña obligatorio, admin, empleado) — nunca con un st.stop() antes de llegar a
él. Si en algún momento no se llega a invocarlo, Streamlit vuelve a su descubrimiento
automático clásico de archivos en frontend/pages/ y expone en la barra lateral el
nombre de CADA página interna (admin_dashboard_page, admin_audit_page...) a cualquier
visitante sin loguear — bug real encontrado en producción el 29/08/2026.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from backend.models import Role  # noqa: E402
from frontend.components import branding  # noqa: E402
from frontend.components.session_state import (  # noqa: E402
    cerrar_sesion,
    guardar_sesion_pendiente,
    usuario_actual,
)
from frontend.pages import (  # noqa: E402
    admin_attendance_history_page,
    admin_attendance_page,
    admin_audit_page,
    admin_dashboard_page,
    admin_employees_page,
    admin_schedules_page,
    admin_settings_page,
    employee_home_page,
    first_access_page,
    login_page,
)

st.set_page_config(
    page_title="INFRATELCO — Control de Asistencia",
    page_icon=str(branding.LOGO_PATH) if branding.LOGO_PATH.exists() else "🏗️",
    layout="wide",
)

usuario = usuario_actual()

if usuario is None:
    # position="hidden": una sola página, no hace falta mostrar un menú de una opción.
    paginas = [st.Page(login_page.render, title="Ingresar", url_path="login", default=True)]
    st.navigation(paginas, position="hidden").run()
    st.stop()

guardar_sesion_pendiente()

if usuario.must_change_password:
    paginas = [
        st.Page(lambda: first_access_page.render(usuario), title="Cambiar contraseña",
                url_path="cambiar-password", default=True)
    ]
    st.navigation(paginas, position="hidden").run()
    st.stop()

branding.aplicar_estilo()

if usuario.role_code == Role.ADMIN:
    # url_path explícito a propósito: st.navigation infiere la URL del nombre de la
    # función, y todas estas son lambdas -> todas se llaman "<lambda>" y chocan
    # ("Multiple Pages specified with URL pathname <lambda>"). Bug real encontrado
    # probando el login completo contra la base de datos real.
    # Iconos de Material Symbols (mismo estilo de línea limpia en todo el panel, en vez
    # de emojis) -- Streamlit ya trae esa fuente cargada, no hace falta nada aparte.
    paginas = [
        st.Page(lambda: admin_dashboard_page.render(usuario), title="Dashboard",
                icon=":material/dashboard:", url_path="dashboard", default=True),
        st.Page(lambda: admin_attendance_page.render(usuario), title="Asistencia del día",
                icon=":material/event_available:", url_path="asistencia"),
        st.Page(lambda: admin_attendance_history_page.render(usuario), title="Histórico",
                icon=":material/history:", url_path="historico"),
        st.Page(lambda: admin_employees_page.render(usuario), title="Empleados",
                icon=":material/group:", url_path="empleados"),
        st.Page(lambda: admin_schedules_page.render(usuario), title="Horarios",
                icon=":material/calendar_month:", url_path="horarios"),
        st.Page(lambda: admin_settings_page.render(usuario), title="Configuración",
                icon=":material/settings:", url_path="configuracion"),
        st.Page(lambda: admin_audit_page.render(usuario), title="Auditoría",
                icon=":material/shield:", url_path="auditoria"),
    ]
else:
    paginas = [
        st.Page(lambda: employee_home_page.render(usuario), title="Mi cuenta",
                icon=":material/person:", url_path="mi-cuenta", default=True),
    ]

with st.sidebar:
    if branding.LOGO_PATH.exists():
        st.image(str(branding.LOGO_PATH), width="stretch")
    st.caption(f"Sesión: {usuario.email}")
    st.caption("Administrador" if usuario.role_code == Role.ADMIN else "Empleado")
    col_tema, col_salir = st.columns([1, 3])
    with col_tema:
        branding.boton_tema()
    with col_salir:
        if st.button("Cerrar sesión", icon=":material/logout:", width="stretch"):
            cerrar_sesion()
            st.rerun()

navegacion = st.navigation(paginas)
navegacion.run()
