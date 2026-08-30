import streamlit as st

from backend.models import User
from backend.repositories import employee_repository
from frontend.components import branding


def render(usuario: User) -> None:
    branding.aplicar_estilo()
    branding.encabezado("Mi cuenta")

    empleado = employee_repository.obtener_por_id(usuario.employee_id) if usuario.employee_id else None

    if empleado:
        st.markdown(f"### {empleado.full_name}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Cédula:** {empleado.document_id}")
            st.write(f"**Cargo:** {empleado.position or '—'}")
            st.write(f"**Área:** {empleado.department or '—'}")
        with col2:
            st.write(f"**Correo:** {empleado.email or '—'}")
            st.write(f"**Teléfono:** {empleado.phone or '—'}")
            st.write(f"**Fecha de ingreso:** {empleado.hire_date or '—'}")
    else:
        st.warning("Tu usuario no tiene un empleado asociado. Contacta al administrador.")

    st.divider()
    st.info(
        "El registro de ingreso/salida con geolocalización y el histórico de tus marcaciones "
        "se habilitan en la Fase 2 de este proyecto (todavía no construida)."
    )
