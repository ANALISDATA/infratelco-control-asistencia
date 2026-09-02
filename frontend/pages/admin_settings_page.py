from datetime import time as dtime

import streamlit as st

from backend import config
from backend.models import User
from backend.services.company import company_settings_service
from backend.services.notifications import whatsapp_service
from backend.services.notifications.providers.callmebot_provider import CallMeBotError


def render(admin: User) -> None:
    st.header("Configuración de la empresa")
    st.caption(
        "NIT, dirección, teléfono y correo se dejan vacíos a propósito: no existían en la "
        "carpeta de trabajo y no deben inventarse. Complétalos aquí cuando los tengas a mano."
    )

    settings = company_settings_service.obtener()

    with st.form("form_configuracion"):
        st.subheader("Datos corporativos")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre comercial", value=settings.company_name)
            razon_social = st.text_input("Razón social", value=settings.legal_name or "")
            nit = st.text_input("NIT", value=settings.nit or "")
        with col2:
            direccion = st.text_input("Dirección", value=settings.address or "")
            telefono = st.text_input("Teléfono", value=settings.phone or "")
            correo = st.text_input("Correo corporativo", value=settings.email or "")

        st.subheader("Horario y puntualidad")
        col3, col4, col5 = st.columns(3)
        with col3:
            hora_entrada = st.time_input(
                "Hora de entrada predeterminada",
                value=dtime.fromisoformat(settings.default_check_in_time),
            )
        with col4:
            hora_salida = st.time_input(
                "Hora de salida predeterminada",
                value=dtime.fromisoformat(settings.default_check_out_time),
            )
        with col5:
            tolerancia = st.number_input(
                "Tolerancia (minutos)", min_value=0, max_value=120, value=settings.tolerance_minutes
            )

        st.subheader("Geolocalización")
        col6, col7 = st.columns(2)
        with col6:
            precision_minima = st.number_input(
                "Precisión mínima permitida (metros)",
                min_value=1.0, max_value=1000.0, value=float(settings.min_gps_accuracy_m),
            )
            requerir_ingreso = st.checkbox(
                "Requerir ubicación para registrar ingreso", value=settings.require_location_check_in
            )
            requerir_salida = st.checkbox(
                "Requerir ubicación para registrar salida", value=settings.require_location_check_out
            )
        with col7:
            comportamiento = st.radio(
                "Si falla la geolocalización",
                options=["allow_with_warning", "block"],
                index=0 if settings.on_location_failure == "allow_with_warning" else 1,
                format_func=lambda v: "Permitir registro con advertencia" if v == "allow_with_warning" else "Bloquear registro",
            )

        st.subheader("WhatsApp — aviso de llegada tarde")
        whatsapp_admin = st.text_input(
            "Número de WhatsApp del administrador (a donde llega el aviso)",
            value=settings.whatsapp_admin_number or "",
            help="Celular colombiano con o sin indicativo, ej. 3127726924.",
        )

        guardar = st.form_submit_button("Guardar configuración", icon=":material/save:", width="stretch")

    if guardar:
        company_settings_service.actualizar(
            admin,
            {
                "company_name": nombre.strip(),
                "legal_name": razon_social.strip() or None,
                "nit": nit.strip() or None,
                "address": direccion.strip() or None,
                "phone": telefono.strip() or None,
                "email": correo.strip() or None,
                "default_check_in_time": hora_entrada.isoformat(),
                "default_check_out_time": hora_salida.isoformat(),
                "tolerance_minutes": int(tolerancia),
                "min_gps_accuracy_m": float(precision_minima),
                "require_location_check_in": requerir_ingreso,
                "require_location_check_out": requerir_salida,
                "on_location_failure": comportamiento,
                "whatsapp_admin_number": whatsapp_admin.strip() or None,
            },
        )
        st.success("Configuración guardada.")
        st.rerun()

    st.divider()
    conectado = config.WHATSAPP_PROVIDER == "callmebot" and bool(config.WHATSAPP_API_KEY)
    if conectado:
        st.success("WhatsApp conectado (CallMeBot) — los avisos de llegada tarde se envían automáticamente.")
    else:
        st.warning(
            "WhatsApp todavía sin conectar: falta la apikey de CallMeBot en `secrets.toml` "
            "(`whatsapp_api_key`). Mientras tanto, ningún aviso se envía — el registro de "
            "asistencia sigue funcionando normal."
        )
    if st.button("Enviar mensaje de prueba", icon=":material/send:", disabled=not settings.whatsapp_admin_number):
        try:
            whatsapp_service.enviar_mensaje_prueba(settings.whatsapp_admin_number)
            st.success(f"Mensaje de prueba enviado a {settings.whatsapp_admin_number}.")
        except CallMeBotError as error:
            st.error(str(error))
