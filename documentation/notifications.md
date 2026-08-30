# Notificaciones — INFRATELCO Control de Asistencia

**Estado: arquitectura preparada, sin proveedor conectado (Fase 5).**

No existen credenciales de WhatsApp Business/Meta, Twilio ni de un proveedor de email en
la carpeta de trabajo, así que no se inventaron ni se conectó ninguna. Las carpetas
`notifications/whatsapp/`, `notifications/email/` y `notifications/templates/`, la tabla
`notifications`/`notification_settings` (ver `database/migrations/001_initial_schema.sql`)
y la pantalla de configuración ya están listas para recibir un proveedor real cuando el
usuario lo autorice y entregue las credenciales oficiales — ver también la nota sobre
límites de "cron" en Streamlit Community Cloud en `documentation/technical-decisions.md`.
