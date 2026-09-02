"""WhatsApp gratuito con CallMeBot — sin cuenta de empresa ni verificación de Meta.

Cómo funciona (documentado para quien administre esto después): el número que va a
RECIBIR los mensajes le manda, una sola vez, el mensaje "I allow callmebot to send me
messages" al contacto de CallMeBot (+34 644 51 71 41). El bot responde con una
apikey personal. Con ese número + esa apikey, cualquiera puede pedirle a CallMeBot que
le mande un WhatsApp a ESE número — por eso no hace falta ninguna cuenta de desarrollador
ni verificación de negocio.

Límite conocido (gratis): CallMeBot es para volumen bajo (alertas personales, no
marketing masivo) — más que suficiente para "avisar a un administrador quién llegó
tarde". Si en el futuro se necesita mandar a muchos números o mucho volumen, hay que
migrar a WhatsApp Business Cloud API (Meta) — ver `documentation/notifications.md`.
"""
from __future__ import annotations

import requests

_URL = "https://api.callmebot.com/whatsapp.php"
_TIMEOUT_SEGUNDOS = 8


class CallMeBotError(Exception):
    """Mensaje ya listo para guardar en notifications.error_message."""


def _normalizar_numero(numero: str) -> str:
    """CallMeBot espera el número con código de país, solo dígitos (sin '+', espacios
    ni guiones). Si el número no trae código de país se asume Colombia (57) — todos
    los números guardados en la app hasta ahora son celulares colombianos de 10 dígitos."""
    limpio = "".join(c for c in numero if c.isdigit())
    if len(limpio) == 10:
        limpio = f"57{limpio}"
    return limpio


def enviar_whatsapp(numero: str, mensaje: str, apikey: str) -> None:
    """Lanza CallMeBotError con un mensaje ya listo para mostrar/guardar si falla.
    Nunca inventa un envío exitoso: solo se considera enviado si CallMeBot responde
    200 con un cuerpo que no empiece con un error conocido."""
    if not apikey:
        raise CallMeBotError("Falta la apikey de CallMeBot (whatsapp_api_key en secrets.toml).")

    numero_normalizado = _normalizar_numero(numero)
    try:
        respuesta = requests.get(
            _URL,
            params={"phone": numero_normalizado, "text": mensaje, "apikey": apikey},
            timeout=_TIMEOUT_SEGUNDOS,
        )
        respuesta.raise_for_status()
    except requests.RequestException as error:
        raise CallMeBotError(f"No se pudo contactar a CallMeBot: {error}") from None

    cuerpo = respuesta.text.strip()
    if "message queued" not in cuerpo.lower() and "success" not in cuerpo.lower():
        raise CallMeBotError(f"CallMeBot respondió con un error: {cuerpo[:200]}")
