"""Reglas de negocio de gestión de empleados: crear un empleado crea también su usuario
de acceso (login por cédula, contraseña temporal, cambio obligatorio en primer ingreso —
regla #7 del encargo). Toda acción administrativa queda en auditoría (regla #24).
"""
from __future__ import annotations

import secrets
import string

from backend.models import Employee, Role, User
from backend.repositories import employee_repository, user_repository
from backend.services.audit import audit_service
from backend.utils import security


def _generar_password_temporal() -> str:
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(12))


def crear_empleado(admin: User, datos: Employee, rol: str = Role.EMPLOYEE) -> tuple[Employee, str]:
    """Crea el empleado y su usuario de acceso. Devuelve (empleado, password_temporal)
    para que el administrador se la entregue al empleado por un canal seguro (no se envía
    por ningún canal automático porque no hay proveedor de email/WhatsApp conectado).

    `rol`: Role.EMPLOYEE (por defecto, solo puede marcar su propia asistencia) o
    Role.ADMIN (acceso completo al panel administrativo -- ej. para darle acceso a una
    secretaria/asistente sin que el dueño tenga que compartir su propia clave)."""
    empleado = employee_repository.crear(datos)

    password_temporal = _generar_password_temporal()
    if not datos.email:
        raise ValueError("El empleado necesita un correo electrónico para crear su acceso.")

    user_repository.crear(
        email=datos.email,
        password_hash=security.hash_password(password_temporal),
        role_code=rol,
        employee_id=empleado.id,
        login_document_id=empleado.document_id,
        must_change_password=True,
    )

    audit_service.registrar(
        admin, "employee.create", "employee", empleado.id,
        new_value={"full_name": empleado.full_name, "document_id": empleado.document_id},
    )
    return empleado, password_temporal


def actualizar_empleado(admin: User, employee_id: str, cambios: dict) -> Employee:
    anterior = employee_repository.obtener_por_id(employee_id)
    actualizado = employee_repository.actualizar(employee_id, cambios)
    audit_service.registrar(
        admin, "employee.update", "employee", employee_id,
        old_value={"full_name": anterior.full_name, "document_id": anterior.document_id},
        new_value=cambios,
    )
    return actualizado


def desactivar_empleado(admin: User, employee_id: str) -> None:
    employee_repository.desactivar(employee_id)
    usuario = user_repository.obtener_por_documento(
        employee_repository.obtener_por_id(employee_id).document_id
    )
    if usuario:
        user_repository.actualizar(usuario.id, {"is_active": False})
    audit_service.registrar(admin, "employee.deactivate", "employee", employee_id)


def activar_empleado(admin: User, employee_id: str) -> None:
    employee_repository.activar(employee_id)
    usuario = user_repository.obtener_por_documento(
        employee_repository.obtener_por_id(employee_id).document_id
    )
    if usuario:
        user_repository.actualizar(usuario.id, {"is_active": True})
    audit_service.registrar(admin, "employee.activate", "employee", employee_id)


def listar_empleados(solo_activos: bool = False, pagina: int = 1, por_pagina: int = 50):
    return employee_repository.listar(solo_activos=solo_activos, pagina=pagina, por_pagina=por_pagina)


def asignar_horario_a_todos(admin: User, schedule_id: str | None) -> int:
    """Para cuando el horario es igual para todo el mundo -- evita tener que entrar a
    editar empleado por empleado. Quien tenga un horario individual distinto se lo
    pisa; si se necesita una excepción puntual, se reasigna después desde Empleados."""
    total = employee_repository.asignar_horario_a_todos(schedule_id)
    audit_service.registrar(
        admin, "employee.bulk_schedule_assign", "employee", None,
        new_value={"schedule_id": schedule_id, "empleados_afectados": total},
    )
    return total
