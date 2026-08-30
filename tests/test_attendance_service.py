import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from backend.models import Employee
from backend.repositories import attendance_repository, company_settings_repository
from backend.services.attendance import attendance_service
from backend.services.geolocation import reverse_geocoding_service
from backend.utils.timezone import ahora


def _empleado(schedule_id=None):
    return Employee(
        id="emp-1", full_name="Juan Pérez", document_id="123", email="juan@infratelco.com",
        schedule_id=schedule_id,
    )


def _ubicacion_navegador(lat=6.123456, lon=-75.123456, accuracy=12.0):
    return {"coords": {"latitude": lat, "longitude": lon, "accuracy": accuracy}, "timestamp": 0}


@pytest.fixture(autouse=True)
def _sin_red_real(monkeypatch):
    # Ninguna prueba debe depender de que Nominatim responda de verdad.
    monkeypatch.setattr(
        reverse_geocoding_service, "obtener_direccion",
        lambda lat, lon: "Calle 35A #46A-25, Copacabana, Antioquia, Colombia",
    )


def _sembrar_ajustes(fake_db, **cambios):
    fila = {
        "id": 1, "company_name": "INFRATELCO", "default_check_in_time": "08:00:00",
        "default_check_out_time": "17:00:00", "tolerance_minutes": 10,
        "min_gps_accuracy_m": 50, "require_location_check_in": True,
        "require_location_check_out": True, "on_location_failure": "allow_with_warning",
    }
    fila.update(cambios)
    fake_db.seed("company_settings", [fila])


def test_ingreso_puntual(fake_db):
    # Hora esperada muy tarde en el día: sea cual sea la hora real a la que corra esta
    # prueba, siempre cae "a tiempo" -- sin depender del reloj de la máquina.
    _sembrar_ajustes(fake_db, default_check_in_time="23:59:00")
    empleado = _empleado()
    resultado = attendance_service.registrar_ingreso(empleado, _ubicacion_navegador())

    assert resultado.registro.check_in_status == "on_time"
    assert resultado.registro.check_in_address == "Calle 35A #46A-25, Copacabana, Antioquia, Colombia"
    assert resultado.advertencias == []


def test_ingreso_guarda_el_comentario_de_obra(fake_db):
    _sembrar_ajustes(fake_db, default_check_in_time="23:59:00")
    empleado = _empleado()
    resultado = attendance_service.registrar_ingreso(
        empleado, _ubicacion_navegador(), comentario="Obra Torre Norte — instalación eléctrica"
    )
    assert resultado.registro.observation == "Obra Torre Norte — instalación eléctrica"


def test_ingreso_sin_comentario_guarda_none(fake_db):
    _sembrar_ajustes(fake_db, default_check_in_time="23:59:00")
    empleado = _empleado()
    resultado = attendance_service.registrar_ingreso(empleado, _ubicacion_navegador(), comentario="   ")
    assert resultado.registro.observation is None


def test_ingreso_tarde_fuera_de_tolerancia(fake_db, monkeypatch):
    # Hora esperada muy temprano en el día, sin tolerancia: cualquier hora real a la
    # que corra esta prueba queda "tarde" -- sin depender del reloj de la máquina.
    _sembrar_ajustes(fake_db, default_check_in_time="00:00:00", tolerance_minutes=0)
    empleado = _empleado()
    resultado = attendance_service.registrar_ingreso(empleado, _ubicacion_navegador())
    assert resultado.registro.check_in_status == "late"


def test_no_se_puede_registrar_dos_ingresos_el_mismo_dia(fake_db):
    _sembrar_ajustes(fake_db)
    empleado = _empleado()
    attendance_service.registrar_ingreso(empleado, _ubicacion_navegador())
    with pytest.raises(attendance_service.AttendanceError, match="Ya registraste tu ingreso"):
        attendance_service.registrar_ingreso(empleado, _ubicacion_navegador())


def test_no_se_puede_registrar_salida_sin_ingreso(fake_db):
    _sembrar_ajustes(fake_db)
    empleado = _empleado()
    with pytest.raises(attendance_service.AttendanceError, match="Todavía no has registrado"):
        attendance_service.registrar_salida(empleado, _ubicacion_navegador())


def test_no_se_puede_registrar_dos_salidas(fake_db):
    _sembrar_ajustes(fake_db)
    empleado = _empleado()
    attendance_service.registrar_ingreso(empleado, _ubicacion_navegador())
    attendance_service.registrar_salida(empleado, _ubicacion_navegador())
    with pytest.raises(attendance_service.AttendanceError, match="Ya registraste tu salida"):
        attendance_service.registrar_salida(empleado, _ubicacion_navegador())


def test_calculo_de_horas_trabajadas(fake_db):
    _sembrar_ajustes(fake_db)
    empleado = _empleado()
    attendance_service.registrar_ingreso(empleado, _ubicacion_navegador())

    # Adelantamos el check_in_at guardado para simular una jornada de 9h 3min real.
    registro = attendance_repository.obtener_por_empleado_y_fecha(empleado.id, ahora().date())
    hace_9h3m = (ahora() - timedelta(hours=9, minutes=3)).isoformat()
    attendance_repository.actualizar(registro.id, {"check_in_at": hace_9h3m})

    resultado = attendance_service.registrar_salida(empleado, _ubicacion_navegador())
    assert resultado.registro.worked_minutes == 9 * 60 + 3


def test_ubicacion_denegada_bloquea_si_la_empresa_lo_exige(fake_db):
    _sembrar_ajustes(fake_db, on_location_failure="block")
    empleado = _empleado()
    resultado_navegador = {"error": {"code": 1, "message": "User denied Geolocation"}}
    with pytest.raises(attendance_service.AttendanceError, match="denegaste el permiso"):
        attendance_service.registrar_ingreso(empleado, resultado_navegador)


def test_ubicacion_denegada_permite_con_advertencia(fake_db):
    _sembrar_ajustes(fake_db, on_location_failure="allow_with_warning")
    empleado = _empleado()
    resultado_navegador = {"error": {"code": 2, "message": "Position unavailable"}}
    resultado = attendance_service.registrar_ingreso(empleado, resultado_navegador)

    assert resultado.registro.check_in_latitude is None
    assert len(resultado.advertencias) == 1
    assert "GPS apagado" in resultado.advertencias[0]


def test_precision_insuficiente_agrega_advertencia_pero_guarda_coordenadas(fake_db):
    _sembrar_ajustes(fake_db, min_gps_accuracy_m=10, on_location_failure="allow_with_warning")
    empleado = _empleado()
    resultado = attendance_service.registrar_ingreso(empleado, _ubicacion_navegador(accuracy=80.0))

    assert resultado.registro.check_in_latitude == 6.123456
    assert resultado.registro.check_in_accuracy_m == 80.0
    assert "precisión" in resultado.advertencias[0].lower()


def test_empleado_inactivo_no_puede_registrar(fake_db):
    _sembrar_ajustes(fake_db)
    empleado = _empleado()
    empleado.is_active = False
    with pytest.raises(attendance_service.AttendanceError, match="desactivado"):
        attendance_service.registrar_ingreso(empleado, _ubicacion_navegador())


def test_usa_horario_del_empleado_si_tiene_uno_asignado(fake_db):
    _sembrar_ajustes(fake_db, default_check_in_time="08:00:00", tolerance_minutes=10)
    fake_db.seed("schedules", [{"id": "sch-1", "name": "Turno mañana", "tolerance_minutes": 0, "is_active": True}])
    hoy_weekday = ahora().isoweekday()
    fake_db.seed("schedule_days", [{
        "id": "sd-1", "schedule_id": "sch-1", "weekday": hoy_weekday,
        "is_working_day": True, "start_time": "23:59:00", "end_time": None,
    }])
    empleado = _empleado(schedule_id="sch-1")

    resultado = attendance_service.registrar_ingreso(empleado, _ubicacion_navegador())
    # La hora esperada (23:59) es después de la hora real -> siempre "on_time" hoy.
    assert resultado.registro.check_in_status == "on_time"
