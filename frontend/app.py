"""Punto de entrada de la app. Se ejecuta con:  streamlit run frontend/app.py

El enrutamiento por rol usa st.navigation/st.Page (Streamlit >= 1.36) en vez del
autodescubrimiento clásico de la carpeta pages/, precisamente para que cada página
quede controlada por este archivo y nadie pueda llegar a una pantalla de administrador
sin haber pasado por la verificación de sesión y rol de abajo.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from backend.models import Role  # noqa: E402
from frontend.components import branding  # noqa: E402
from frontend.components.session_state import cerrar_sesion, usuario_actual  # noqa: E402
from frontend.pages import (  # noqa: E402
    admin_audit_page,
    admin_dashboard_page,
    admin_employees_page,
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
    login_page.render()
    st.stop()

if usuario.must_change_password:
    first_access_page.render(usuario)
    st.stop()

branding.aplicar_estilo()

if usuario.role_code == Role.ADMIN:
    paginas = [
        st.Page(lambda: admin_dashboard_page.render(usuario), title="Dashboard", icon="📊", default=True),
        st.Page(lambda: admin_employees_page.render(usuario), title="Empleados", icon="👥"),
        st.Page(lambda: admin_settings_page.render(usuario), title="Configuración", icon="⚙️"),
        st.Page(lambda: admin_audit_page.render(usuario), title="Auditoría", icon="🛡️"),
    ]
else:
    paginas = [
        st.Page(lambda: employee_home_page.render(usuario), title="Mi cuenta", icon="👤", default=True),
    ]

with st.sidebar:
    if branding.LOGO_PATH.exists():
        st.image(str(branding.LOGO_PATH), use_container_width=True)
    st.caption(f"Sesión: {usuario.email}")
    st.caption("Administrador" if usuario.role_code == Role.ADMIN else "Empleado")
    if st.button("Cerrar sesión", use_container_width=True):
        cerrar_sesion()
        st.rerun()

navegacion = st.navigation(paginas)
navegacion.run()
