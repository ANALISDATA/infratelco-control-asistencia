-- =====================================================================
-- INFRATELCO — Sistema de Control de Asistencia
-- Migración 001: esquema inicial completo
-- =====================================================================
-- Motor: PostgreSQL (Supabase)
-- Zona horaria de la aplicación: America/Bogota (la BD guarda en UTC,
-- la conversión a hora de Bogotá se hace en la capa de aplicación).
--
-- Cómo ejecutar: Supabase → SQL Editor → New query → pegar todo → Run.
-- Es seguro volver a correrlo: todas las sentencias usan
-- IF NOT EXISTS / ON CONFLICT DO NOTHING donde aplica.
--
-- ESQUEMA DEDICADO: este proyecto Supabase es compartido con otras apps de ISTHO
-- (EXTRACCIÓN OP, Barbería), así que todas las tablas de INFRATELCO viven en su propio
-- esquema "infratelco" en vez de "public", para no mezclarse ni chocar de nombres con
-- las tablas de esas otras apps. Después de correr este script, hay que agregar
-- "infratelco" en Supabase → Project Settings → API → Data API Settings →
-- Exposed schemas (si no, la API no lo deja consultar). Ver documentation/database.md.
-- =====================================================================

create extension if not exists "pgcrypto" schema public;

create schema if not exists infratelco;

set search_path to infratelco, public;

-- ---------------------------------------------------------------------
-- ROLES
-- ---------------------------------------------------------------------
create table if not exists roles (
    id          smallint primary key,
    code        text not null unique,          -- 'admin' | 'employee'
    name        text not null
);

insert into roles (id, code, name) values
    (1, 'admin', 'Administrador'),
    (2, 'employee', 'Empleado')
on conflict (id) do nothing;

-- ---------------------------------------------------------------------
-- EMPLEADOS
-- ---------------------------------------------------------------------
create table if not exists employees (
    id                  uuid primary key default gen_random_uuid(),
    full_name           text not null,
    document_id         text not null unique,      -- cédula
    email               text unique,
    phone               text,
    whatsapp_number     text,
    position             text,                      -- cargo
    department          text,                       -- área/departamento
    hire_date           date,
    schedule_id         uuid,                        -- FK -> schedules, se agrega tras crear schedules
    is_active           boolean not null default true,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

create index if not exists idx_employees_document_id on employees (document_id);
create index if not exists idx_employees_is_active on employees (is_active);

-- ---------------------------------------------------------------------
-- USUARIOS (credenciales de acceso, 1:1 con employees para rol employee;
-- también soporta administradores sin registro de asistencia propio)
-- ---------------------------------------------------------------------
create table if not exists users (
    id                      uuid primary key default gen_random_uuid(),
    employee_id             uuid references employees(id) on delete set null,
    role_id                 smallint not null references roles(id),
    login_document_id       text unique,        -- cédula (login empleado)
    email                   text not null unique,
    password_hash           text not null,
    must_change_password    boolean not null default true,
    is_active               boolean not null default true,
    failed_login_attempts   smallint not null default 0,
    locked_until            timestamptz,
    last_login_at           timestamptz,
    created_at              timestamptz not null default now(),
    updated_at              timestamptz not null default now()
);

create index if not exists idx_users_email on users (email);
create index if not exists idx_users_login_document_id on users (login_document_id);

-- ---------------------------------------------------------------------
-- SESIONES
-- ---------------------------------------------------------------------
create table if not exists sessions (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid not null references users(id) on delete cascade,
    token_hash      text not null unique,
    ip_address      text,
    user_agent      text,
    expires_at      timestamptz not null,
    revoked_at      timestamptz,
    created_at      timestamptz not null default now()
);

create index if not exists idx_sessions_user_id on sessions (user_id);
create index if not exists idx_sessions_expires_at on sessions (expires_at);

-- ---------------------------------------------------------------------
-- RECUPERACIÓN DE CONTRASEÑA
-- ---------------------------------------------------------------------
create table if not exists password_resets (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid not null references users(id) on delete cascade,
    token_hash      text not null unique,
    expires_at      timestamptz not null,
    used_at         timestamptz,
    created_at      timestamptz not null default now()
);

create index if not exists idx_password_resets_user_id on password_resets (user_id);

-- ---------------------------------------------------------------------
-- HORARIOS
-- ---------------------------------------------------------------------
create table if not exists schedules (
    id                      uuid primary key default gen_random_uuid(),
    name                    text not null,
    tolerance_minutes       smallint not null default 10,
    is_active               boolean not null default true,
    created_at              timestamptz not null default now(),
    updated_at              timestamptz not null default now()
);

alter table employees
    add constraint fk_employees_schedule
    foreign key (schedule_id) references schedules(id) on delete set null;

-- Día de la semana: 1=Lunes ... 7=Domingo (ISO-8601)
create table if not exists schedule_days (
    id              uuid primary key default gen_random_uuid(),
    schedule_id     uuid not null references schedules(id) on delete cascade,
    weekday         smallint not null check (weekday between 1 and 7),
    is_working_day  boolean not null default true,
    start_time      time,
    end_time        time,
    unique (schedule_id, weekday)
);

create index if not exists idx_schedule_days_schedule_id on schedule_days (schedule_id);

-- ---------------------------------------------------------------------
-- ASISTENCIA — una fila = una jornada de un empleado (para Power BI)
-- ---------------------------------------------------------------------
create table if not exists attendance_records (
    id                          uuid primary key default gen_random_uuid(),
    employee_id                 uuid not null references employees(id),
    work_date                   date not null,

    check_in_at                 timestamptz,
    check_in_status              text check (check_in_status in ('on_time','late')),
    check_in_expected_at        timestamptz,

    check_in_latitude           numeric(10,7),
    check_in_longitude          numeric(10,7),
    check_in_accuracy_m         numeric(8,2),
    check_in_location_at        timestamptz,
    check_in_address             text,

    check_out_at                timestamptz,
    check_out_status              text check (check_out_status in ('registered','missing')),

    check_out_latitude          numeric(10,7),
    check_out_longitude         numeric(10,7),
    check_out_accuracy_m        numeric(8,2),
    check_out_location_at       timestamptz,
    check_out_address            text,

    worked_minutes               integer,

    original_check_in_at        timestamptz,
    modified_check_in_at        timestamptz,

    original_check_out_at       timestamptz,
    modified_check_out_at       timestamptz,

    observation                  text,
    justification_id             uuid,

    modified_by                  uuid references users(id),
    modified_at                  timestamptz,

    created_at                   timestamptz not null default now(),
    updated_at                   timestamptz not null default now(),

    unique (employee_id, work_date)
);

create index if not exists idx_attendance_employee_id on attendance_records (employee_id);
create index if not exists idx_attendance_work_date on attendance_records (work_date);
create index if not exists idx_attendance_check_in_at on attendance_records (check_in_at);
create index if not exists idx_attendance_check_out_at on attendance_records (check_out_at);
create index if not exists idx_attendance_status on attendance_records (check_in_status);

-- ---------------------------------------------------------------------
-- JUSTIFICACIONES
-- ---------------------------------------------------------------------
create table if not exists justifications (
    id                      uuid primary key default gen_random_uuid(),
    attendance_record_id    uuid not null references attendance_records(id) on delete cascade,
    justification_type      text not null,     -- ej: 'actividad_laboral', 'salud', 'personal'
    reason                  text not null,
    original_status         text,
    new_status               text,
    authorized_by            uuid not null references users(id),
    created_at               timestamptz not null default now()
);

create index if not exists idx_justifications_attendance_id on justifications (attendance_record_id);

alter table attendance_records
    add constraint fk_attendance_justification
    foreign key (justification_id) references justifications(id) on delete set null;

-- ---------------------------------------------------------------------
-- AUDITORÍA (inmutable para usuarios normales)
-- ---------------------------------------------------------------------
create table if not exists audit_logs (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid references users(id),
    action          text not null,             -- ej: 'attendance.update', 'employee.create'
    entity_type     text not null,
    entity_id       text,
    old_value       jsonb,
    new_value       jsonb,
    reason          text,
    ip_address      text,
    created_at      timestamptz not null default now()
);

create index if not exists idx_audit_logs_entity on audit_logs (entity_type, entity_id);
create index if not exists idx_audit_logs_user_id on audit_logs (user_id);
create index if not exists idx_audit_logs_created_at on audit_logs (created_at);

-- ---------------------------------------------------------------------
-- CONFIGURACIÓN DE EMPRESA (fila única)
-- ---------------------------------------------------------------------
create table if not exists company_settings (
    id                              smallint primary key default 1,
    company_name                    text not null default 'INFRATELCO',
    legal_name                      text,
    nit                             text,
    address                         text,
    phone                           text,
    email                           text,
    logo_path                       text default 'assets/logos/infratelco_logo.png',
    timezone                        text not null default 'America/Bogota',
    default_check_in_time           time not null default '08:00',
    default_check_out_time          time not null default '17:00',
    tolerance_minutes               smallint not null default 10,
    whatsapp_admin_number           text,
    daily_summary_time              time default '18:00',
    min_gps_accuracy_m              numeric(8,2) not null default 50,
    require_location_check_in       boolean not null default true,
    require_location_check_out      boolean not null default true,
    on_location_failure             text not null default 'allow_with_warning'
                                        check (on_location_failure in ('block','allow_with_warning')),
    geofence_latitude               numeric(10,7),
    geofence_longitude              numeric(10,7),
    geofence_radius_m               numeric(8,2),
    geofence_enabled                boolean not null default false,
    updated_at                      timestamptz not null default now(),
    constraint single_row check (id = 1)
);

insert into company_settings (id, company_name)
values (1, 'INFRATELCO')
on conflict (id) do nothing;

-- ---------------------------------------------------------------------
-- NOTIFICACIONES
-- ---------------------------------------------------------------------
create table if not exists notification_settings (
    id                      smallint primary key default 1,
    late_arrival_enabled    boolean not null default true,
    daily_summary_enabled   boolean not null default true,
    missing_check_in_enabled  boolean not null default true,
    missing_check_out_enabled boolean not null default true,
    provider                text default 'none',   -- 'none' | 'whatsapp_meta' | 'twilio' | 'email'
    constraint single_row_ns check (id = 1)
);

insert into notification_settings (id) values (1) on conflict (id) do nothing;

create table if not exists notifications (
    id              uuid primary key default gen_random_uuid(),
    notification_type text not null,       -- 'late_arrival' | 'daily_summary' | 'missing_check_in' | 'missing_check_out'
    channel          text not null,        -- 'whatsapp' | 'email' | 'internal'
    recipient        text not null,
    subject          text,
    body             text not null,
    status           text not null default 'pending' check (status in ('pending','sent','failed')),
    related_entity_type text,
    related_entity_id   text,
    sent_at          timestamptz,
    error_message    text,
    created_at       timestamptz not null default now()
);

create index if not exists idx_notifications_status on notifications (status);
create index if not exists idx_notifications_created_at on notifications (created_at);
