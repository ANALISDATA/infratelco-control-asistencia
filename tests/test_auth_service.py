import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from backend import config
from backend.services.auth import auth_service
from backend.utils import security


def _seed_admin(fake_db, password="ClaveAdmin123"):
    fake_db.seed(
        "users",
        [
            {
                "id": "admin-1",
                "email": "admin@infratelco.com",
                "password_hash": security.hash_password(password),
                "role_id": 1,
                "employee_id": None,
                "login_document_id": None,
                "must_change_password": False,
                "is_active": True,
                "failed_login_attempts": 0,
                "locked_until": None,
            }
        ],
    )


def test_login_exitoso_con_correo(fake_db):
    _seed_admin(fake_db)
    resultado = auth_service.login("admin@infratelco.com", "ClaveAdmin123")
    assert resultado.user.email == "admin@infratelco.com"
    assert resultado.session_token


def test_login_password_incorrecta(fake_db):
    _seed_admin(fake_db)
    with pytest.raises(auth_service.AuthError, match=auth_service.MENSAJE_CREDENCIALES_INVALIDAS):
        auth_service.login("admin@infratelco.com", "clave-mala")


def test_login_usuario_inexistente_mismo_mensaje_que_password_mala(fake_db):
    _seed_admin(fake_db)
    with pytest.raises(auth_service.AuthError, match=auth_service.MENSAJE_CREDENCIALES_INVALIDAS):
        auth_service.login("noexiste@infratelco.com", "cualquiera")


def test_bloqueo_tras_intentos_fallidos(fake_db):
    _seed_admin(fake_db)
    for _ in range(config.MAX_FAILED_LOGIN_ATTEMPTS):
        with pytest.raises(auth_service.AuthError):
            auth_service.login("admin@infratelco.com", "clave-mala")

    # Ahora, aunque use la contraseña CORRECTA, debe seguir bloqueado.
    with pytest.raises(auth_service.AuthError, match="bloqueada"):
        auth_service.login("admin@infratelco.com", "ClaveAdmin123")


def test_login_por_cedula_empleado(fake_db):
    fake_db.seed(
        "users",
        [
            {
                "id": "emp-1",
                "email": "empleado@infratelco.com",
                "password_hash": security.hash_password("Temporal123"),
                "role_id": 2,
                "employee_id": "employee-1",
                "login_document_id": "1020304050",
                "must_change_password": True,
                "is_active": True,
                "failed_login_attempts": 0,
                "locked_until": None,
            }
        ],
    )
    resultado = auth_service.login("1020304050", "Temporal123")
    assert resultado.user.role_code == "employee"
    assert resultado.user.must_change_password is True


def test_cambiar_password_actualiza_hash_y_desmarca_primer_acceso(fake_db):
    _seed_admin(fake_db, password="Temporal123")
    resultado = auth_service.login("admin@infratelco.com", "Temporal123")
    auth_service.cambiar_password(resultado.user, "Temporal123", "NuevaClave456")

    # El login con la clave vieja ya no debe funcionar; con la nueva, sí.
    with pytest.raises(auth_service.AuthError):
        auth_service.login("admin@infratelco.com", "Temporal123")
    nuevo_login = auth_service.login("admin@infratelco.com", "NuevaClave456")
    assert nuevo_login.user.must_change_password is False


def test_validar_sesion_token_invalido_devuelve_none(fake_db):
    assert auth_service.validar_sesion("token-que-no-existe") is None


def test_cerrar_sesion_invalida_el_token(fake_db):
    _seed_admin(fake_db)
    resultado = auth_service.login("admin@infratelco.com", "ClaveAdmin123")
    assert auth_service.validar_sesion(resultado.session_token) is not None
    auth_service.cerrar_sesion(resultado.session_token)
    assert auth_service.validar_sesion(resultado.session_token) is None
