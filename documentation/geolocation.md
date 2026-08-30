# Geolocalización — INFRATELCO Control de Asistencia

**Estado: construido y probado end-to-end contra Supabase real (Fase 2).**

## Flujo real

```
Empleado hace clic en "Permitir ubicación"
       ↓
navigator.geolocation.getCurrentPosition() (streamlit_js_eval)
       ↓
Latitud + Longitud + Precisión (metros)
       ↓
Reverse Geocoding (Nominatim, OpenStreetMap)
       ↓
Dirección legible
       ↓
Empleado hace clic en "REGISTRAR INGRESO" / "REGISTRAR SALIDA"
       ↓
backend/services/attendance/attendance_service.py:
  - hora oficial = servidor (backend/utils/timezone.ahora())
  - valida precisión mínima vs. Configuración de la empresa
  - guarda lat/lon/precisión/timestamp/dirección junto con el registro
```

## Cómo se pide el permiso

`frontend/pages/employee_home_page.py` — el botón **"📍 Permitir ubicación"** es
obligatoriamente un clic explícito del empleado (regla #16 del encargo): la app nunca
pide ubicación automáticamente al cargar la página. Antes del botón se explica por qué
se necesita y que no hay seguimiento continuo.

## Cómo se obtiene latitud/longitud/precisión

`streamlit_js_eval.get_geolocation()` ejecuta `navigator.geolocation.getCurrentPosition()`
en el navegador **una sola vez por clic** (nunca `watchPosition`, que sería
seguimiento continuo). Devuelve `{coords: {latitude, longitude, accuracy}, timestamp}`
o `{error: {code, message}}` si el usuario lo deniega, el GPS está apagado, o hay
timeout — `backend/services/geolocation/location_service.py` traduce esos tres casos
(códigos 1/2/3 del estándar W3C) a un mensaje en español listo para mostrar.

## Cómo funciona el Reverse Geocoding

`backend/services/geolocation/reverse_geocoding_service.py` es el único punto desde el
que el resto de la app pide una dirección — decide qué proveedor usar según
`GEOCODING_PROVIDER` (`.streamlit/secrets.toml` / `.env`).

Proveedor actual: **Nominatim (OpenStreetMap)**, gratuito, sin API key
(`backend/services/geolocation/providers/nominatim_provider.py`). Arma la dirección a
partir de los componentes estructurados que devuelve (calle + número, barrio/localidad,
departamento, país) — igual al formato pedido:
`Calle 35A #46A-25, Copacabana, Antioquia, Colombia`.

**Cambiar de proveedor** (a Google/Mapbox/HERE, por ejemplo): agregar un archivo nuevo
en `backend/services/geolocation/providers/` con una función
`obtener_direccion(latitud, longitud) -> str | None`, y sumar la rama correspondiente
en `reverse_geocoding_service.py`. Nada más de la app se entera del cambio.

## Qué pasa si el usuario deniega la ubicación

Se muestra el mensaje de error correspondiente y un botón "Reintentar". Si además la
empresa configuró **"Bloquear registro"** (`company_settings.on_location_failure`), el
ingreso/salida no se guarda hasta que haya ubicación válida. Si configuró **"Permitir
registro con advertencia"** (el valor por defecto), el registro se guarda igual, sin
coordenadas, y se le muestra la advertencia al empleado.

## Qué pasa si no hay una dirección exacta

`nominatim_provider.obtener_direccion()` devuelve `None` si Nominatim no tiene
componentes de dirección para esas coordenadas (o si la llamada falla/tarda más de 5
segundos) — **nunca se inventa una dirección**. Latitud, longitud, precisión y el
timestamp de captura se guardan siempre, tenga o no dirección.

## Cómo se protege la información

- Se captura únicamente en el instante de `REGISTRAR INGRESO` / `REGISTRAR SALIDA` —
  no existe ningún proceso en segundo plano que pida ubicación.
- Latitud/longitud/dirección viajan solo entre el navegador del empleado y el backend
  de esta app (Streamlit corre del lado del servidor); no se comparten con nadie más.
- Row Level Security activo en la tabla `attendance_records` (ver
  `database/migrations/002_enable_rls.sql`): solo el backend de la app (`service_role`)
  puede leer o escribir esos datos.

## Probado

- Ciclo completo ingreso → salida contra la base de datos real (esquema `infratelco`
  dentro del proyecto Supabase compartido), incluyendo cálculo de horas trabajadas.
- Bloqueo de doble ingreso / doble salida / salida sin ingreso.
- Registro sin ubicación cuando el navegador la deniega (`on_location_failure =
  allow_with_warning`) — guarda el registro con las coordenadas en blanco y muestra la
  advertencia.
- Precisión por debajo del mínimo configurado — guarda igual las coordenadas reales y
  muestra la advertencia (nunca descarta el dato).
- Determinación de puntualidad usando el horario asignado al empleado, y usando el
  horario predeterminado de la empresa cuando el empleado no tiene uno asignado.

**No probado todavía** (requiere navegador real, no se puede simular desde aquí): el
diálogo real del navegador pidiendo permiso de ubicación, ni el comportamiento en un
celular real en campo. Es el siguiente paso para el usuario antes de dar por cerrada
la Fase 2.
