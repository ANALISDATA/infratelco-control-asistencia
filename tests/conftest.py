import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from backend.utils import db
from tests.fakes import ClienteSupabaseFalso


@pytest.fixture
def fake_db(monkeypatch):
    """Reemplaza el cliente de Supabase por uno en memoria para toda la duración del test."""
    cliente_falso = ClienteSupabaseFalso()
    monkeypatch.setattr(db, "cliente", lambda: cliente_falso)
    monkeypatch.setattr(db, "disponible", lambda: True)
    return cliente_falso
