# Decisiones técnicas — INFRATELCO Control de Asistencia

## Stack elegido

| Capa | Tecnología | Por qué |
|---|---|---|
| Frontend + Backend | **Streamlit** (Python) | Mismo framework que EXTRACCIÓN OP y Barbería Esteban Barber (proyectos ya entregados en esta carpeta). El usuario ya sabe abrir/desplegar apps Streamlit, y se despliega gratis en Streamlit Community Cloud. |
| Base de datos | **Supabase (PostgreSQL)** | Mismo motor que EXTRACCIÓN OP y Barbería. Gratis en el plan inicial, soporta índices, relaciones, JSONB (para auditoría) y escala sin cambiar de motor hasta varios miles de empleados. |
| Cliente de BD | `supabase-py` | Ya usado en EXTRACCION OP (`requirements.txt`), evita curva de aprendizaje nueva. |
| Hashing de contraseñas | `bcrypt` (vía `passlib`) | Estándar de la industria, sin costo, sin dependencias externas de pago. |
| Excel corporativo | `openpyxl` | Ya usado en EXTRACCION OP; permite formato, fórmulas, congelar encabezados, imágenes (logo). |
| Geolocalización del navegador | Componente HTML/JS embebido (Geolocation API nativa del navegador) | Streamlit no expone GPS nativamente; se inyecta un pequeño componente JS que llama a `navigator.geolocation.getCurrentPosition` y devuelve lat/lng/precisión a Python. Sin librerías de pago. |
| Reverse Geocoding | **Nominatim (OpenStreetMap)**, gratuito, sin API key | Cumple la regla "preferir herramientas gratuitas". Se implementa detrás de una interfaz (`ReverseGeocodingProvider`) para poder cambiar a Google/Mapbox/HERE más adelante sin tocar la lógica de asistencia — solo se agrega un nuevo archivo en `backend/services/geolocation/providers/`. |
| WhatsApp / Email | Interfaces preparadas, sin proveedor activo | No existen credenciales oficiales de Meta/Twilio/Resend en la carpeta de trabajo. Se deja la arquitectura lista (`notifications/whatsapp`, `notifications/email`) para conectar un proveedor oficial cuando el usuario lo autorice y entregue las credenciales. |
| Zona horaria | `America/Bogota` en toda la app | Requisito explícito. La base de datos guarda timestamps en UTC (estándar Postgres); la conversión a hora de Bogotá ocurre en `backend/utils/timezone.py`. |
| Secrets / credenciales | `st.secrets` (`.streamlit/secrets.toml`) como mecanismo principal, con fallback a variables de entorno (`.env`) para scripts fuera de Streamlit | Mismo patrón que EXTRACCION OP. `secrets.toml` nunca se commitea (ver `.gitignore`). |

## Por qué NO se usó Supabase Auth directamente

Supabase Auth maneja usuarios por email/password de forma nativa, pero el sistema requiere:
- Login por **cédula o correo**.
- Relación estricta 1:1 con el registro de `employees` (nombre, cargo, horario, etc.).
- Roles personalizados (`admin` / `employee`) con reglas de negocio específicas (un empleado no puede modificar sus propios registros).

Por eso se implementó una tabla `users` propia con `password_hash` (bcrypt), controlada completamente por la aplicación. Esto da control total sobre bloqueo por intentos fallidos, expiración de sesión y auditoría — más simple de razonar y depurar para este caso de uso que adaptar Supabase Auth con triggers.

## Diseño de base de datos pensado para Power BI

Regla aplicada: **una fila de `attendance_records` = una jornada de un empleado**, con columnas planas (no anidadas) para que Power BI pueda conectarse directamente vía el Excel exportado o, en el futuro, vía conector de PostgreSQL. Ver `powerbi/README.md`.

## Límite conocido: notificaciones programadas

Streamlit Community Cloud no ejecuta procesos en segundo plano (no hay "cron" nativo). El resumen diario y las alertas de tardanza se preparan como servicios invocables (`notifications/`), pero el disparo automático a una hora fija requiere uno de:
1. Un **Supabase Edge Function con cron** (gratuito dentro del plan free, límites generosos), o
2. Un disparo manual desde el dashboard del administrador ("Enviar resumen ahora"), o
3. Una tarea programada en el equipo del administrador (Task Scheduler de Windows) que llama a un script Python.

Esta decisión se toma y documenta en la Fase 5 (notificaciones), cuando se conecte un proveedor real. Por ahora la arquitectura no bloquea ninguna de las tres opciones.

## Escalabilidad

- Índices en `employee_id`, `work_date`, `check_in_at`, `check_out_at`, `status` (ver `001_initial_schema.sql`).
- Paginación obligatoria en listados de histórico y auditoría (no se traen tablas completas al frontend).
- Servicios y repositorios separados por responsabilidad (`backend/services/*`, `backend/repositories/*`) para poder optimizar o reemplazar una pieza sin afectar las demás.
- Probado en diseño para crecer de 20 a 500+ empleados sin cambio de motor de base de datos.
