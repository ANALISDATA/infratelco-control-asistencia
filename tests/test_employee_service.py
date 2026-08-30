import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from backend.models import Employee
from backend.repositories import employee_repository
from backend.services.employees import employee_service

ADMIN = None  # las funciones de auditoría aceptan None como "actor sistema" en estos tests


def _empleado(document_id="1000000001", email="juan@infratelco.com"):
    return Employee(
        id=None,
        full_name="Juan Pérez",
        document_id=document_id,
        email=email,
        phone="3001234567",
    )


def test_crear_empleado_crea_tambien_su_usuario_de_acceso(fake_db):
    empleado, password_temporal = employee_service.crear_empleado(ADMIN, _empleado())

    assert empleado.id is not None
    assert password_temporal  # se generó una contraseña temporal
    usuarios = fake_db._tablas["users"].filas
    assert len(usuarios) == 1
    assert usuarios[0]["login_document_id"] == "1000000001"
    assert usuarios[0]["must_change_password"] is True
    assert usuarios[0]["role_id"] == 2  # employee


def test_crear_empleado_cedula_duplicada_falla(fake_db):
    employee_service.crear_empleado(ADMIN, _empleado(document_id="111", email="a@infratelco.com"))
    with pytest.raises(employee_repository.DocumentoDuplicado):
        employee_service.crear_empleado(ADMIN, _empleado(document_id="111", email="b@infratelco.com"))


def test_crear_empleado_correo_duplicado_falla(fake_db):
    employee_service.crear_empleado(ADMIN, _empleado(document_id="111", email="dup@infratelco.com"))
    with pytest.raises(employee_repository.CorreoDuplicado):
        employee_service.crear_empleado(ADMIN, _empleado(document_id="222", email="dup@infratelco.com"))


def test_crear_empleado_sin_correo_falla(fake_db):
    with pytest.raises(ValueError):
        employee_service.crear_empleado(ADMIN, _empleado(email=None))


def test_desactivar_empleado_desactiva_tambien_su_usuario(fake_db):
    empleado, _ = employee_service.crear_empleado(ADMIN, _empleado())
    employee_service.desactivar_empleado(ADMIN, empleado.id)

    actualizado = employee_repository.obtener_por_id(empleado.id)
    assert actualizado.is_active is False

    usuario = fake_db._tablas["users"].filas[0]
    assert usuario["is_active"] is False


def test_actualizar_empleado_no_permite_email_duplicado_de_otro(fake_db):
    employee_service.crear_empleado(ADMIN, _empleado(document_id="1", email="uno@infratelco.com"))
    otro, _ = employee_service.crear_empleado(ADMIN, _empleado(document_id="2", email="dos@infratelco.com"))

    with pytest.raises(employee_repository.CorreoDuplicado):
        employee_service.actualizar_empleado(ADMIN, otro.id, {"email": "uno@infratelco.com"})
