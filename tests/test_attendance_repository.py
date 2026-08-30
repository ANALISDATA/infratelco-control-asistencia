import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.repositories import attendance_repository


def test_listar_por_rango_filtra_fechas_dentro_del_rango(fake_db):
    fake_db.seed("attendance_records", [
        {"id": "1", "employee_id": "e1", "work_date": "2026-08-01", "check_in_status": "on_time"},
        {"id": "2", "employee_id": "e1", "work_date": "2026-08-15", "check_in_status": "late"},
        {"id": "3", "employee_id": "e1", "work_date": "2026-08-31", "check_in_status": "on_time"},
    ])

    resultado = attendance_repository.listar_por_rango(date(2026, 8, 10), date(2026, 8, 20))

    assert [r.id for r in resultado] == ["2"]


def test_listar_por_rango_incluye_los_extremos(fake_db):
    fake_db.seed("attendance_records", [
        {"id": "1", "employee_id": "e1", "work_date": "2026-08-10"},
        {"id": "2", "employee_id": "e1", "work_date": "2026-08-20"},
    ])

    resultado = attendance_repository.listar_por_rango(date(2026, 8, 10), date(2026, 8, 20))

    assert {r.id for r in resultado} == {"1", "2"}
