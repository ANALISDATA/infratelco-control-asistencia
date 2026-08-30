"""Ejecuta la app real con el framework oficial de pruebas de Streamlit (AppTest):
corre el script frontend/app.py de punta a punta, sin navegador, y falla si hay
cualquier excepción de Python durante el render. Sin credenciales de Supabase
configuradas, debe mostrar el aviso de "no conectado" en vez de reventar.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

from backend import config


def test_login_page_sin_supabase_no_revienta(monkeypatch):
    # Se fuerza "sin credenciales" explícitamente: si la máquina donde corren las
    # pruebas tiene un .streamlit/secrets.toml real (como este equipo, ya conectado a
    # Supabase), el test no debe depender de ese estado ambiental para ser determinista.
    monkeypatch.setattr(config, "SUPABASE_URL", None)
    monkeypatch.setattr(config, "SUPABASE_KEY", None)

    at = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "frontend" / "app.py"))
    at.run(timeout=15)
    assert not at.exception, f"La app lanzó una excepción: {at.exception}"

    mensajes_error = [e.value for e in at.error]
    assert any("no está conectada a la base de datos" in m for m in mensajes_error), (
        f"Se esperaba el aviso de base de datos no conectada. Errores mostrados: {mensajes_error}"
    )
