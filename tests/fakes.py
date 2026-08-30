"""Sustituto en memoria del cliente de Supabase, para probar servicios/repositorios reales
sin necesitar una base de datos de verdad. Implementa el subconjunto de la API fluida de
supabase-py que usan los repositorios de este proyecto (select/insert/update, eq/neq/gt/is_,
order/range/limit)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone


class _Resultado:
    def __init__(self, data):
        self.data = data


class _TablaFalsa:
    def __init__(self):
        self.filas: list[dict] = []


class _ConsultaFalsa:
    def __init__(self, tabla: _TablaFalsa):
        self._tabla = tabla
        self._modo = None
        self._payload = None
        self._filtros: list[tuple] = []
        self._order_col = None
        self._order_desc = False
        self._range = None
        self._limit = None

    def select(self, *_a, **_k):
        self._modo = "select"
        return self

    def insert(self, payload: dict):
        self._modo = "insert"
        self._payload = payload
        return self

    def update(self, payload: dict):
        self._modo = "update"
        self._payload = payload
        return self

    def eq(self, col, val):
        self._filtros.append(("eq", col, val))
        return self

    def neq(self, col, val):
        self._filtros.append(("neq", col, val))
        return self

    def gt(self, col, val):
        self._filtros.append(("gt", col, val))
        return self

    def gte(self, col, val):
        self._filtros.append(("gte", col, val))
        return self

    def lte(self, col, val):
        self._filtros.append(("lte", col, val))
        return self

    def is_(self, col, val):
        self._filtros.append(("is", col, val))
        return self

    def order(self, col, desc: bool = False):
        self._order_col = col
        self._order_desc = desc
        return self

    def range(self, desde, hasta):
        self._range = (desde, hasta)
        return self

    def limit(self, n):
        self._limit = n
        return self

    def _coincide(self, fila: dict) -> bool:
        for tipo, col, val in self._filtros:
            actual = fila.get(col)
            if tipo == "eq" and actual != val:
                return False
            if tipo == "neq" and actual == val:
                return False
            if tipo == "gt" and not (actual is not None and str(actual) > str(val)):
                return False
            if tipo == "gte" and not (actual is not None and str(actual) >= str(val)):
                return False
            if tipo == "lte" and not (actual is not None and str(actual) <= str(val)):
                return False
            if tipo == "is" and val == "null" and actual is not None:
                return False
        return True

    def execute(self):
        if self._modo == "insert":
            nueva = dict(self._payload)
            nueva.setdefault("id", str(uuid.uuid4()))
            nueva.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            self._tabla.filas.append(nueva)
            return _Resultado([nueva])

        if self._modo == "update":
            afectadas = [f for f in self._tabla.filas if self._coincide(f)]
            for fila in afectadas:
                fila.update(self._payload)
            return _Resultado([dict(f) for f in afectadas])

        coincidentes = [dict(f) for f in self._tabla.filas if self._coincide(f)]
        if self._order_col:
            coincidentes.sort(key=lambda f: f.get(self._order_col) or "", reverse=self._order_desc)
        if self._range:
            desde, hasta = self._range
            coincidentes = coincidentes[desde : hasta + 1]
        elif self._limit is not None:
            coincidentes = coincidentes[: self._limit]
        return _Resultado(coincidentes)


class ClienteSupabaseFalso:
    def __init__(self):
        self._tablas: dict[str, _TablaFalsa] = {}

    def table(self, nombre: str) -> _ConsultaFalsa:
        self._tablas.setdefault(nombre, _TablaFalsa())
        return _ConsultaFalsa(self._tablas[nombre])

    def seed(self, nombre: str, filas: list[dict]) -> None:
        self._tablas.setdefault(nombre, _TablaFalsa())
        self._tablas[nombre].filas.extend(filas)
