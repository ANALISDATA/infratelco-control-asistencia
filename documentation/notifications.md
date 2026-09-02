# Notificaciones — INFRATELCO Control de Asistencia

**Estado: WhatsApp de llegada tarde implementado con CallMeBot (gratis).**

Cuando un empleado registra su ingreso y queda marcado como "tarde", la app le manda
automáticamente un WhatsApp al administrador configurado en **Configuración → WhatsApp**
(`company_settings.whatsapp_admin_number`) con el nombre del empleado y la hora. No hace
falta ningún cron ni proceso en segundo plano — el aviso sale en el mismo momento del
registro, dentro de `attendance_service.registrar_ingreso()`.

Proveedor: [CallMeBot](https://www.callmebot.com/blog/free-api-whatsapp-messages/),
gratis y sin cuenta de empresa — el número que recibe los avisos le manda un mensaje una
sola vez al bot para obtener su `apikey` personal, y esa clave se guarda en
`secrets.toml` (`whatsapp_provider = "callmebot"`, `whatsapp_api_key = "..."`). Ver
`backend/services/notifications/providers/callmebot_provider.py`.

Es "mejor esfuerzo": si CallMeBot falla o no está conectado, el registro de asistencia
del empleado NUNCA se bloquea — solo queda un renglón en la tabla `notifications` con
`status = 'failed'` para poder revisarlo. Se puede probar la conexión con el botón
"Enviar mensaje de prueba" en Configuración.

**Todavía sin implementar:** resumen diario, aviso de "no marcó salida", y el canal de
email — no había credenciales de un proveedor de email en la carpeta de trabajo, así
que no se inventó ninguna. La tabla `notification_settings` ya tiene las columnas
listas (`daily_summary_enabled`, `missing_check_out_enabled`, etc.) para cuando se
decida construir esto. Ver también la nota sobre límites de "cron" en Streamlit
Community Cloud en `documentation/technical-decisions.md` — el resumen diario sí
necesitaría uno de esos tres mecanismos, a diferencia del aviso de llegada tarde.
