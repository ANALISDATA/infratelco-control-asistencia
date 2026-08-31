-- =====================================================================
-- INFRATELCO — Migración 004: horas extra
-- =====================================================================
-- Agrega las columnas para calcular y guardar las horas extra en el momento de la
-- salida: cuál era la hora de salida esperada ese día (según el horario del
-- empleado o el predeterminado de la empresa) y cuántos minutos pasaron esa hora.
-- Se guarda en el registro (no se recalcula después) para que quede fijo con la
-- configuración vigente ESE día, igual que ya se hace con check_in_status.
-- =====================================================================

set search_path to infratelco, public;

alter table attendance_records
    add column if not exists check_out_expected_at timestamptz;

alter table attendance_records
    add column if not exists overtime_minutes integer;
