# Backups — INFRATELCO Control de Asistencia

## Base de datos (Supabase)

- Supabase toma **backups automáticos diarios** en el plan gratuito (retención de
  ~7 días; los planes pagos extienden la retención y agregan point-in-time recovery).
  No requiere configuración adicional de nuestra parte.
- Backup manual bajo demanda: Supabase → Project Settings → Database → *Backups* →
  *Download*, o `pg_dump` con la cadena de conexión del proyecto (Project Settings →
  Database → Connection string) para quien tenga psql instalado.
- Recomendación operativa: antes de ejecutar una migración nueva (`database/migrations/`)
  sobre datos reales, descargar un backup manual.

## Excel corporativo

- Cada Excel generado (Fase 4) es un archivo independiente con fecha en el nombre — no se
  sobrescribe el anterior. Guardarlos en una carpeta de OneDrive/SharePoint sincronizada
  (mismo patrón que EXTRACCIÓN OP) le da versión e historial automáticos sin trabajo extra.

## Código de la aplicación

- El código vive en esta carpeta (`app_control_asistencia/`). Se recomienda inicializar
  un repositorio git y subirlo a un remoto privado (GitHub) apenas se conecte Supabase,
  igual que EXTRACCIÓN OP (`Subir_a_GitHub.bat`) — así el código también queda respaldado
  fuera del equipo local.

## Restauración

1. Base de datos: Supabase → *Backups* → restaurar el punto deseado (o recrear el esquema
   con `database/migrations/001_initial_schema.sql` + reinsertar desde un `pg_dump`).
2. Código: `git clone` del remoto, o restaurar la copia de OneDrive.
3. Secrets (`.streamlit/secrets.toml`, `.env`): **no se pueden recuperar de un backup de
   git** porque nunca se suben (están en `.gitignore` a propósito). Deben guardarse aparte,
   en un gestor de contraseñas de la empresa.
