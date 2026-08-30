import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.utils import timezone as tz  # noqa: E402


def test_ahora_tiene_zona_bogota():
    ahora = tz.ahora()
    assert ahora.tzinfo is not None
    assert str(ahora.tzinfo) == "America/Bogota"


def test_a_bogota_convierte_utc_naive_asumido_utc():
    # Postgres/Supabase devuelve timestamps en UTC; simulamos mediodía UTC.
    utc_naive = datetime(2026, 8, 29, 17, 0, 0)  # 17:00 UTC == 12:00 Bogotá (UTC-5)
    convertido = tz.a_bogota(utc_naive)
    assert convertido.hour == 12
    assert convertido.tzinfo is not None


def test_a_bogota_convierte_utc_con_tzinfo():
    utc_aware = datetime(2026, 8, 29, 13, 0, 0, tzinfo=timezone.utc)  # 08:00 Bogotá
    convertido = tz.a_bogota(utc_aware)
    assert convertido.hour == 8


def test_formato_hora():
    utc_aware = datetime(2026, 8, 29, 13, 2, 0, tzinfo=timezone.utc)
    assert tz.formato_hora(utc_aware) == "08:02"


def test_formato_fecha():
    utc_aware = datetime(2026, 8, 29, 13, 2, 0, tzinfo=timezone.utc)
    assert tz.formato_fecha(utc_aware) == "29/08/2026"
