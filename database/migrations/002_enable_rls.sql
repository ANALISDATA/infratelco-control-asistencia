-- =====================================================================
-- INFRATELCO — Migración 002: Row Level Security (blindaje extra)
-- =====================================================================
-- "Exposed schemas" en Supabase solo hace que la API SEPA que el esquema existe;
-- todavía hace falta una API key válida para leer cualquier cosa, y la app usa
-- exclusivamente la clave "service_role" desde el servidor (nunca llega al navegador
-- del empleado). Aun así, se activa RLS sin ninguna política permisiva en cada tabla:
-- así, ni con la clave pública ("anon") se podría leer una sola fila desde fuera.
-- Solo "service_role" (la que usa esta app) puede pasar por encima de RLS.
--
-- Cómo ejecutar: igual que la migración 001 — SQL Editor → New query → pegar → Run.
-- =====================================================================

set search_path to infratelco, public;

alter table roles                  enable row level security;
alter table employees              enable row level security;
alter table users                  enable row level security;
alter table sessions               enable row level security;
alter table password_resets        enable row level security;
alter table schedules              enable row level security;
alter table schedule_days          enable row level security;
alter table attendance_records     enable row level security;
alter table justifications         enable row level security;
alter table audit_logs             enable row level security;
alter table company_settings       enable row level security;
alter table notification_settings  enable row level security;
alter table notifications          enable row level security;
