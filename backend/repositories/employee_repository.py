"""Acceso a datos de empleados. No contiene reglas de negocio (eso vive en
backend/services) — solo lectura/escritura en la tabla `employees`."""
from __future__ import annotations

from backend.models import Employee
from backend.utils import db


class DocumentoDuplicado(Exception):
    pass


class CorreoDuplicado(Exception):
    pass


def listar(solo_activos: bool = False, pagina: int = 1, por_pagina: int = 50) -> list[Employee]:
    query = db.cliente().table("employees").select("*").order("full_name")
    if solo_activos:
        query = query.eq("is_active", True)
    desde = (pagina - 1) * por_pagina
    hasta = desde + por_pagina - 1
    respuesta = query.range(desde, hasta).execute()
    return [Employee.from_row(r) for r in respuesta.data]


def obtener_por_id(employee_id: str) -> Employee | None:
    respuesta = db.cliente().table("employees").select("*").eq("id", employee_id).limit(1).execute()
    return Employee.from_row(respuesta.data[0]) if respuesta.data else None


def obtener_por_documento(document_id: str) -> Employee | None:
    respuesta = (
        db.cliente().table("employees").select("*").eq("document_id", document_id).limit(1).execute()
    )
    return Employee.from_row(respuesta.data[0]) if respuesta.data else None


def _validar_unicidad(document_id: str, email: str | None, excluir_id: str | None = None) -> None:
    cliente = db.cliente()

    q = cliente.table("employees").select("id").eq("document_id", document_id)
    if excluir_id:
        q = q.neq("id", excluir_id)
    if q.execute().data:
        raise DocumentoDuplicado(f"Ya existe un empleado con la cédula {document_id}.")

    if email:
        q = cliente.table("employees").select("id").eq("email", email)
        if excluir_id:
            q = q.neq("id", excluir_id)
        if q.execute().data:
            raise CorreoDuplicado(f"Ya existe un empleado con el correo {email}.")


def crear(empleado: Employee) -> Employee:
    _validar_unicidad(empleado.document_id, empleado.email)
    fila = {
        "full_name": empleado.full_name,
        "document_id": empleado.document_id,
        "email": empleado.email,
        "phone": empleado.phone,
        "whatsapp_number": empleado.whatsapp_number,
        "position": empleado.position,
        "department": empleado.department,
        "hire_date": empleado.hire_date.isoformat() if empleado.hire_date else None,
        "schedule_id": empleado.schedule_id,
        "is_active": empleado.is_active,
    }
    respuesta = db.cliente().table("employees").insert(fila).execute()
    return Employee.from_row(respuesta.data[0])


def actualizar(employee_id: str, cambios: dict) -> Employee:
    if "document_id" in cambios or "email" in cambios:
        actual = obtener_por_id(employee_id)
        _validar_unicidad(
            cambios.get("document_id", actual.document_id),
            cambios.get("email", actual.email),
            excluir_id=employee_id,
        )
    if "hire_date" in cambios and cambios["hire_date"] is not None:
        cambios = {**cambios, "hire_date": cambios["hire_date"].isoformat()}
    respuesta = db.cliente().table("employees").update(cambios).eq("id", employee_id).execute()
    return Employee.from_row(respuesta.data[0])


def desactivar(employee_id: str) -> None:
    db.cliente().table("employees").update({"is_active": False}).eq("id", employee_id).execute()


def activar(employee_id: str) -> None:
    db.cliente().table("employees").update({"is_active": True}).eq("id", employee_id).execute()
