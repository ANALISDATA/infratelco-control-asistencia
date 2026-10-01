"""App desactivada — INFRATELCO Control de Asistencia.

Esta versión del archivo reemplaza la app funcional para desactivar el link público
de Streamlit Community Cloud. Los archivos originales están conservados en este
repositorio en el historial de git.
"""
import streamlit as st

st.set_page_config(
    page_title="INFRATELCO — Servicio finalizado",
    page_icon="🔒",
    layout="centered",
)

st.markdown(
    """
    <style>
    .bloque-central {
        max-width: 520px;
        margin: 80px auto 0 auto;
        text-align: center;
    }
    .titulo {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00226E;
        margin-top: 24px;
    }
    .subtitulo {
        font-size: 1rem;
        color: #555;
        margin-top: 12px;
        line-height: 1.6;
    }
    .empresa {
        font-size: 0.85rem;
        color: #888;
        margin-top: 32px;
    }
    </style>
    <div class="bloque-central">
        <div class="titulo">Esta aplicación ya no está disponible</div>
        <div class="subtitulo">
            El sistema de Control de Asistencia de INFRATELCO ha sido dado de baja.<br>
            Si tienes dudas, contacta al administrador de la empresa.
        </div>
        <div class="empresa">INFRATELCO — Ingeniería Eléctrica e Infraestructura</div>
    </div>
    """,
    unsafe_allow_html=True,
)
