import pandas as pd
import streamlit as st

from backend.models import User
from backend.repositories import audit_repository
from backend.utils.timezone import formato_fecha_hora


def render(admin: User) -> None:
    st.header("Auditoría")
    st.caption("Registro inmutable de acciones administrativas. No puede editarse ni borrarse desde la app.")

    pagina = st.number_input("Página", min_value=1, value=1, step=1)
    registros = audit_repository.listar(pagina=int(pagina), por_pagina=50)

    if not registros:
        st.info("No hay registros de auditoría todavía.")
        return

    df = pd.DataFrame(
        [
            {
                "Fecha": formato_fecha_hora(pd.to_datetime(r["created_at"])),
                "Acción": r["action"],
                "Entidad": r["entity_type"],
                "ID entidad": r.get("entity_id"),
                "Motivo": r.get("reason") or "—",
                "Usuario": r.get("user_id") or "—",
            }
            for r in registros
        ]
    )
    st.dataframe(df, width="stretch", hide_index=True)
