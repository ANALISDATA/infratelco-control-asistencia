-- =====================================================================
-- INFRATELCO — Migración 003: permisos para service_role
-- =====================================================================
-- Un esquema nuevo no tiene permisos automáticos, ni para "service_role" (el rol
-- interno que usa esta app desde el servidor). Se los da explícitamente aquí.
--
-- A propósito NO se le da nada a "anon" ni "authenticated" (los roles que usarían
-- claves públicas) — así el esquema queda accesible únicamente desde el backend de
-- esta app, igual que pediste.
-- =====================================================================

grant usage on schema infratelco to service_role;

grant all on all tables in schema infratelco to service_role;
grant all on all sequences in schema infratelco to service_role;
grant all on all routines in schema infratelco to service_role;

alter default privileges in schema infratelco grant all on tables to service_role;
alter default privileges in schema infratelco grant all on sequences to service_role;
alter default privileges in schema infratelco grant all on routines to service_role;
