"""Gráficos del dashboard — barras profesionales con Altair (mismo motor que
EXTRACCION OP).

Colores validados por contraste real contra el fondo del dashboard (#F4F6FA), no
elegidos a ojo — el verde y el dorado del logo, tal cual, no pasan 3:1 sobre un fondo
claro, así que aquí se usan versiones más oscuras de la misma familia de color:

    azul oscuro  #00226E  -> 13.35:1  (magnitud, serie única)
    verde marca  #4A7519  ->  5.04:1  (estado "activo" / bueno)
    gris oscuro  #4B5563  ->  6.98:1  (estado "inactivo" / neutro)

Cada barra lleva su valor como etiqueta directa (nunca solo color), esquinas
superiores redondeadas y un resalte sutil al pasar el mouse — sin ejes ni líneas de
más: la única tinta "ruidosa" permitida es la del dato.
"""
from __future__ import annotations

import altair as alt
import pandas as pd

AZUL_OSCURO = "#00226E"
VERDE_ESTADO = "#4A7519"
GRIS_ESTADO = "#4B5563"

_FUENTE = "sans-serif"


def _base(df: pd.DataFrame, x: str, y: str) -> alt.Chart:
    return alt.Chart(df).encode(
        x=alt.X(f"{x}:N", sort="-y", title=None, axis=alt.Axis(labelAngle=0, domain=False, ticks=False)),
        y=alt.Y(f"{y}:Q", title=None, axis=alt.Axis(grid=True, gridColor="#E3E7EE", domain=False, ticks=False)),
    )


def barras_magnitud(df: pd.DataFrame, x: str, y: str, *, color: str = AZUL_OSCURO, altura: int = 280) -> alt.LayerChart:
    """Barras de una sola serie (identidad = eje X, color fijo = una sola tonalidad).
    Para "¿cuánto hay de cada categoría?" — ej. empleados por área."""
    resaltado = alt.selection_point(on="mouseover", fields=[x], empty=False)

    barras = (
        _base(df, x, y)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=28, color=color)
        .encode(
            opacity=alt.condition(resaltado, alt.value(1.0), alt.value(0.88)),
            tooltip=[alt.Tooltip(f"{x}:N", title=""), alt.Tooltip(f"{y}:Q", title="Empleados")],
        )
        .add_params(resaltado)
    )
    etiquetas = _base(df, x, y).mark_text(dy=-8, fontWeight="bold", color="#1A1A1A", font=_FUENTE).encode(
        text=alt.Text(f"{y}:Q", format="d")
    )
    return (
        (barras + etiquetas)
        .properties(height=altura)
        .configure_view(strokeWidth=0)
        .configure_axis(labelFont=_FUENTE, labelColor="#4B5563", labelFontSize=12)
    )


def barras_estado(df: pd.DataFrame, x: str, y: str, *, dominio: list[str], rango: list[str],
                   altura: int = 220) -> alt.LayerChart:
    """Barras con color de estado fijo (ej. Activo=verde, Inactivo=gris) — nunca
    colores categóricos genéricos: el significado de cada color está reservado."""
    resaltado = alt.selection_point(on="mouseover", fields=[x], empty=False)

    barras = (
        _base(df, x, y)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=40)
        .encode(
            color=alt.Color(f"{x}:N", scale=alt.Scale(domain=dominio, range=rango), legend=None),
            opacity=alt.condition(resaltado, alt.value(1.0), alt.value(0.88)),
            tooltip=[alt.Tooltip(f"{x}:N", title=""), alt.Tooltip(f"{y}:Q", title="Empleados")],
        )
        .add_params(resaltado)
    )
    etiquetas = _base(df, x, y).mark_text(dy=-8, fontWeight="bold", color="#1A1A1A", font=_FUENTE).encode(
        text=alt.Text(f"{y}:Q", format="d")
    )
    return (
        (barras + etiquetas)
        .properties(height=altura)
        .configure_view(strokeWidth=0)
        .configure_axis(labelFont=_FUENTE, labelColor="#4B5563", labelFontSize=12)
    )
