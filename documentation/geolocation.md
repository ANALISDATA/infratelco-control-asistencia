# Geolocalización — INFRATELCO Control de Asistencia

**Estado: pendiente de construir (Fase 2).** Este documento se completará con el detalle
real de la implementación (cómo se pide el permiso, cómo se llama a Reverse Geocoding, qué
pasa si el usuario lo deniega) cuando esa fase se construya y se pruebe, para no describir
comportamiento que todavía no existe.

Lo ya decidido y documentado mientras tanto está en
`documentation/technical-decisions.md`:

- Se captura ubicación **solo** al registrar ingreso y al registrar salida — nunca de
  forma continua (regla #10 y #59 del encargo).
- Reverse Geocoding con **Nominatim (OpenStreetMap)**, gratuito, detrás de una interfaz
  reemplazable en `backend/services/geolocation/providers/`.
- Se guardan siempre latitud + longitud + precisión + timestamp + dirección — nunca solo
  una parte (regla #58/#64).
- La precisión mínima aceptada y qué hacer si falla la geolocalización (bloquear o
  permitir con advertencia) son configurables desde **Configuración de la empresa**, ya
  construida en la Fase 1 (`frontend/pages/admin_settings_page.py`), aunque todavía no
  tiene efecto porque el registro de ingreso/salida no existe hasta la Fase 2.
