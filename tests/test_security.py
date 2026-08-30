import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.utils import security  # noqa: E402


def test_hash_password_no_es_texto_plano():
    hashed = security.hash_password("ClaveSegura123")
    assert hashed != "ClaveSegura123"
    assert hashed.startswith("$2b$")


def test_verificar_password_correcta():
    hashed = security.hash_password("ClaveSegura123")
    assert security.verificar_password("ClaveSegura123", hashed) is True


def test_verificar_password_incorrecta():
    hashed = security.hash_password("ClaveSegura123")
    assert security.verificar_password("OtraClave123", hashed) is False


def test_verificar_password_hash_invalido_no_revienta():
    assert security.verificar_password("cualquiera", "no-es-un-hash-valido") is False


def test_validar_fortaleza_corta():
    ok, motivo = security.validar_fortaleza("abc123")
    assert ok is False
    assert "caracteres" in motivo


def test_validar_fortaleza_sin_numero():
    ok, motivo = security.validar_fortaleza("abcdefgh")
    assert ok is False
    assert "número" in motivo


def test_validar_fortaleza_sin_letra():
    ok, motivo = security.validar_fortaleza("12345678")
    assert ok is False
    assert "letra" in motivo


def test_validar_fortaleza_valida():
    ok, motivo = security.validar_fortaleza("Clave1234")
    assert ok is True
    assert motivo == ""


def test_generar_token_es_unico_y_verificable():
    token1, hash1 = security.generar_token()
    token2, hash2 = security.generar_token()
    assert token1 != token2
    assert hash1 != hash2
    assert security.hash_token(token1) == hash1


def test_hash_token_es_determinista():
    assert security.hash_token("mismo-texto") == security.hash_token("mismo-texto")
