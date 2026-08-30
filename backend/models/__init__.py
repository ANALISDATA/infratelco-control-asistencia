"""Modelos de datos (Fase 1): representan filas de la base de datos como objetos tipados,
para no pasar diccionarios sueltos entre repositorios, servicios y pantallas."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


def _parse_dt(valor) -> datetime | None:
    """Supabase/PostgREST devuelve timestamptz como texto ISO-8601, no como datetime.
    Todo lo que se vaya a comparar con un datetime (ej. locked_until en auth_service)
    debe pasar por aquí al salir de la base de datos."""
    if valor is None or isinstance(valor, datetime):
        return valor
    texto = str(valor).replace("Z", "+00:00")
    return datetime.fromisoformat(texto)


def _parse_date(valor) -> date | None:
    if valor is None or isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor))


@dataclass
class Employee:
    id: str | None
    full_name: str
    document_id: str
    email: str | None = None
    phone: str | None = None
    whatsapp_number: str | None = None
    position: str | None = None
    department: str | None = None
    hire_date: date | None = None
    schedule_id: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @staticmethod
    def from_row(row: dict) -> "Employee":
        return Employee(
            id=row.get("id"),
            full_name=row["full_name"],
            document_id=row["document_id"],
            email=row.get("email"),
            phone=row.get("phone"),
            whatsapp_number=row.get("whatsapp_number"),
            position=row.get("position"),
            department=row.get("department"),
            hire_date=_parse_date(row.get("hire_date")),
            schedule_id=row.get("schedule_id"),
            is_active=row.get("is_active", True),
            created_at=_parse_dt(row.get("created_at")),
            updated_at=_parse_dt(row.get("updated_at")),
        )


@dataclass
class Role:
    id: int
    code: str
    name: str

    ADMIN = "admin"
    EMPLOYEE = "employee"


@dataclass
class User:
    id: str | None
    email: str
    role_code: str
    employee_id: str | None = None
    login_document_id: str | None = None
    password_hash: str = ""
    must_change_password: bool = True
    is_active: bool = True
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None

    @property
    def is_admin(self) -> bool:
        return self.role_code == Role.ADMIN

    @staticmethod
    def from_row(row: dict, role_code: str) -> "User":
        return User(
            id=row.get("id"),
            email=row["email"],
            role_code=role_code,
            employee_id=row.get("employee_id"),
            login_document_id=row.get("login_document_id"),
            password_hash=row.get("password_hash", ""),
            must_change_password=row.get("must_change_password", True),
            is_active=row.get("is_active", True),
            failed_login_attempts=row.get("failed_login_attempts", 0),
            locked_until=_parse_dt(row.get("locked_until")),
            last_login_at=_parse_dt(row.get("last_login_at")),
        )


@dataclass
class CompanySettings:
    company_name: str = "INFRATELCO"
    legal_name: str | None = None
    nit: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    logo_path: str = "assets/logos/infratelco_logo.png"
    timezone: str = "America/Bogota"
    default_check_in_time: str = "08:00"
    default_check_out_time: str = "17:00"
    tolerance_minutes: int = 10
    whatsapp_admin_number: str | None = None
    daily_summary_time: str | None = "18:00"
    min_gps_accuracy_m: float = 50
    require_location_check_in: bool = True
    require_location_check_out: bool = True
    on_location_failure: str = "allow_with_warning"
    geofence_latitude: float | None = None
    geofence_longitude: float | None = None
    geofence_radius_m: float | None = None
    geofence_enabled: bool = False

    @staticmethod
    def from_row(row: dict) -> "CompanySettings":
        campos = {f: row.get(f) for f in CompanySettings.__dataclass_fields__ if f in row}
        return CompanySettings(**campos)
