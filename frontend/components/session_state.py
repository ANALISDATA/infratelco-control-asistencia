"""Envoltorio sobre st.session_state + localStorage del navegador para la sesión de
login.

st.session_state por sí solo vive mientras dura la conexión del navegador con el
servidor Streamlit: si el usuario cierra la pestaña o recarga, se pierde. Para que un
empleado no tenga que iniciar sesión cada día desde el celular en obra, el token de
sesión también se guarda en el localStorage del navegador (vía streamlit_js_eval, que
ya se usa en la app para la geolocalización) con una duración larga para empleados y
corta para administradores — ver backend/config.py (SESSION_TTL_HOURS_EMPLOYEE / _ADMIN).

Se probó primero con streamlit_cookies_controller, pero su set() nunca llegó a escribir
la cookie de verdad en el navegador (bug conocido y sin resolver de esa librería, no de
esta app -- reproducido en local con Playwright: la cookie nunca aparece ni esperando
varios segundos después de loguear). streamlit_js_eval es más simple (evalúa JS directo,
sin un objeto controlador con estado cacheado que se pueda quedar desactualizado) y ya
está probado en producción para la ubicación GPS, así que se usa el mismo mecanismo aquí.

localStorage por sí solo no basta para entrar: el token todavía se valida contra la
tabla `sessions` en cada carga (auth_service.validar_sesion), así que cerrar sesión
desde otro lado, o que el token expire, la invalida igual aunque siga en el navegador.

Nota sobre recargar la página (F5): como leer localStorage requiere un viaje de ida y
vuelta al navegador, la primerísima vez que corre el script en una sesión de Streamlit
nueva todavía no se sabe el valor real -- se ve un parpadeo muy breve de la pantalla de
login antes de que llegue el valor real y la app se actualice sola. Es la naturaleza de
cómo funcionan los componentes de Streamlit, no un error.
"""
from __future__ import annotations

import streamlit as st
from streamlit_js_eval import get_local_storage, remove_local_storage, set_local_storage

from backend.models import User
from backend.services.auth import auth_service

CLAVE_LOCALSTORAGE = "infratelco_session"


def usuario_actual() -> User | None:
    token = st.session_state.get("session_token")

    if not token:
        # No hay token en esta sesión de navegador todavía: puede que sí exista uno
        # guardado en el localStorage de una visita anterior (celular del empleado).
        token = get_local_storage(CLAVE_LOCALSTORAGE, component_key="leer_sesion_guardada")

    if not token:
        return None

    usuario = auth_service.validar_sesion(token)
    if usuario is None:
        # El token guardado ya no es válido (expiró o se cerró sesión en otro lado).
        st.session_state.pop("session_token", None)
        remove_local_storage(CLAVE_LOCALSTORAGE, component_key="borrar_sesion_invalida")
        return None

    # Válido: se deja en session_state para no tener que releer el localStorage en
    # cada rerun (evita el parpadeo de login en cada clic dentro de la misma visita).
    st.session_state["session_token"] = token
    st.session_state["user_id"] = usuario.id
    return usuario


def iniciar_sesion(resultado: auth_service.ResultadoLogin) -> None:
    st.session_state["session_token"] = resultado.session_token
    st.session_state["user_id"] = resultado.user.id
    # El guardado en localStorage se deja pendiente para el próximo rerun (ver
    # guardar_sesion_pendiente) en vez de llamarlo aquí mismo: justo después de esto
    # login_page.py hace st.rerun(), y si el componente que escribe el localStorage se
    # crea en el mismo instante que se corta el script, el navegador nunca alcanza a
    # ejecutar la escritura -- bug real, reproducido con Playwright (localStorage se
    # queda vacío para siempre en esa sesión).
    st.session_state["_pendiente_guardar_sesion"] = resultado.session_token


def guardar_sesion_pendiente() -> None:
    """Llamar una vez por rerun ya con el usuario autenticado (después de que
    usuario_actual() devolvió alguien). Si el login acaba de pasar en el rerun
    anterior, aquí sí se persiste el token en localStorage -- en un rerun aparte del
    que hizo login, sin un st.rerun() inmediatamente después, para que el navegador
    tenga tiempo real de ejecutar la escritura."""
    token = st.session_state.pop("_pendiente_guardar_sesion", None)
    if token:
        set_local_storage(CLAVE_LOCALSTORAGE, token, component_key="guardar_sesion")


def cerrar_sesion() -> None:
    token = st.session_state.get("session_token")
    if token:
        auth_service.cerrar_sesion(token)
    for clave in ("session_token", "user_id"):
        st.session_state.pop(clave, None)
    remove_local_storage(CLAVE_LOCALSTORAGE, component_key="cerrar_sesion_borrar")
