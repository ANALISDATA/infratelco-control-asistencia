# Base de datos — INFRATELCO Control de Asistencia

Motor: **PostgreSQL** vía Supabase. El proyecto de Supabase (plan gratuito) es
**compartido** con otras apps de ISTHO (EXTRACCIÓN OP, Barbería) — el plan free solo
permite 2 proyectos y ya estaban en uso. Para no mezclar ni chocar con las tablas de esas
apps, todas las tablas de INFRATELCO viven en su **propio esquema de PostgreSQL,
`infratelco`**, en vez del esquema `public` que usan las otras. Es el mismo mecanismo de
aislamiento que usarían proyectos separados, pero dentro del mismo proyecto Supabase.

Después de correr la migración hay que habilitar ese esquema en la API (un paso único,
manual, en el panel de Supabase): **Project Settings → API → Data API Settings → Exposed
schemas** → agregar `infratelco`. Sin ese paso, PostgREST rechaza las consultas aunque las
tablas ya existan (`db.probar_conexion()` detecta este caso específico y lo explica).

Esquema completo en `database/migrations/001_initial_schema.sql` — se creó de una sola vez, con todas las
tablas de todas las fases (secciones 43-44 del encargo), para no tener que hacer
migraciones que reestructuren tablas ya usadas más adelante. La lógica de aplicación de
la Fase 1 solo usa el subconjunto necesario para autenticación, empleados, auditoría y
configuración; el resto (asistencia, horarios, justificaciones, notificaciones) queda
creado y listo para las fases siguientes.

## Tablas activas en la Fase 1

| Tabla | Para qué |
|---|---|
| `roles` | Catálogo fijo: `admin`, `employee`. |
| `employees` | Datos del empleado (sección 8 del encargo). |
| `users` | Credenciales de acceso, 1:1 con `employees` para el rol `employee`; también admite administradores sin ficha de empleado. |
| `sessions` | Sesiones de login (hash del token, expiración). |
| `password_resets` | Tokens de recuperación (listo para la Fase 5, cuando se conecte email). |
| `audit_logs` | Auditoría inmutable de acciones administrativas. |
| `company_settings` | Fila única con la configuración de la empresa (sección 40). |

## Tablas creadas pero todavía sin lógica de aplicación (fases siguientes)

| Tabla | Fase que la activa |
|---|---|
| `schedules`, `schedule_days` | Fase 2 — horarios y tolerancia. |
| `attendance_records` | Fase 2 — registro de ingreso/salida + geolocalización. Diseñada como **una fila = una jornada de un empleado**, pensando en Power BI (sección 35). |
| `justifications` | Fase 3 — justificar llegadas tarde. |
| `notification_settings`, `notifications` | Fase 5 — WhatsApp/email. |

## Cómo ejecutar el esquema

1. Supabase → tu proyecto → **SQL Editor** → *New query*.
2. Pega el contenido completo de `database/migrations/001_initial_schema.sql`.
3. *Run*. Es seguro volver a ejecutarlo (usa `IF NOT EXISTS` / `ON CONFLICT DO NOTHING`).
4. Verifica con `python Conectar_Supabase.py`.

## Índices

Se crearon pensando en los filtros que el histórico y el dashboard van a usar mucho
(sección 61): `employee_id`, `work_date`, `check_in_at`, `check_out_at`, `document_id`,
`email`. Ver el archivo de migración para el listado completo.
