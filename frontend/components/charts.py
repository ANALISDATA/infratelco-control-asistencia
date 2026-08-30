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
VERDE_ESTADO = "#4A7519"   # bueno (activo, puntual) -- 5.04:1 sobre #F4F6FA
AMBAR_ESTADO = "#B45309"  # advertencia (tarde) -- 4.64:1 sobre #F4F6FA
GRIS_ESTADO = "#4B5563"   # neutro (inactivo, no marcó) -- 6.98:1 sobre #F4F6FA

_FUENTE = "sans-serif"


def _tema_grafico(oscuro: bool) -> dict:
    if oscuro:
        return dict(fondo="#121826", grid="rgba(255,255,255,0.08)", texto_eje="#8891A5", texto_dato="#E5E7EB")
    return dict(fondo="#FFFFFF", grid="#E3E7EE", texto_eje="#6B7280", texto_dato="#1A1A1A")


def _base(df: pd.DataFrame, x: str, y: str, grid: str) -> alt.Chart:
    return alt.Chart(df).encode(
        x=alt.X(f"{x}:N", sort="-y", title=None, axis=alt.Axis(labelAngle=0, domain=False, ticks=False)),
        y=alt.Y(f"{y}:Q", title=None, axis=alt.Axis(grid=True, gridColor=grid, domain=False, ticks=False)),
    )


def barras_magnitud(df: pd.DataFrame, x: str, y: str, *, color: str = AZUL_OSCURO, altura: int = 280,
                     oscuro: bool = False) -> alt.LayerChart:
    """Barras de una sola serie (identidad = eje X, color fijo = una sola tonalidad).
    Para "¿cuánto hay de cada categoría?" — ej. empleados por área."""
    t = _tema_grafico(oscuro)
    resaltado = alt.selection_point(on="mouseover", fields=[x], empty=False)

    barras = (
        _base(df, x, y, t["grid"])
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=28, color=color)
        .encode(
            opacity=alt.condition(resaltado, alt.value(1.0), alt.value(0.88)),
            tooltip=[alt.Tooltip(f"{x}:N", title=""), alt.Tooltip(f"{y}:Q", title="Empleados")],
        )
        .add_params(resaltado)
    )
    etiquetas = _base(df, x, y, t["grid"]).mark_text(
        dy=-8, fontWeight="bold", color=t["texto_dato"], font=_FUENTE
    ).encode(text=alt.Text(f"{y}:Q", format="d"))
    return (
        (barras + etiquetas)
        .properties(height=altura, background=t["fondo"])
        .configure_view(strokeWidth=0)
        .configure_axis(labelFont=_FUENTE, labelColor=t["texto_eje"], labelFontSize=12)
    )


def tendencia_lineas(
    df: pd.DataFrame,
    x: str,
    series: list[tuple[str, str, str]],
    *,
    oscuro: bool = False,
    altura: int = 300,
) -> alt.LayerChart:
    """Tendencia en el tiempo — curvas suaves con relleno degradado y el último punto
    de cada serie resaltado con su valor, estilo "hero chart" de dashboard ejecutivo.

    `series`: lista de (columna_en_df, color_hex, etiqueta_para_tooltip).
    `df` debe venir ordenado por `x` ascendente (más antiguo primero).
    """
    fondo = "#121826" if oscuro else "#FFFFFF"
    grid = "rgba(255,255,255,0.08)" if oscuro else "#EEF1F6"
    texto_eje = "#8891A5" if oscuro else "#6B7280"
    texto_etiqueta = "#E5E7EB" if oscuro else "#14213D"

    orden_x = list(dict.fromkeys(df[x]))  # orden real de las filas, no alfabético
    ultimo_x = df[x].iloc[-1]
    dominio = [c for c, _, _ in series]
    rango = [c for _, c, _ in series]

    # UNA sola fuente de datos (formato largo) y UNA sola codificación base para todas
    # las capas -- el patrón estándar de Altair para varias series. Se probaron antes
    # dos variantes con una capa (o un Chart) distinto por serie y en ambas Vega-Lite
    # terminaba sin poder calcular la escala del eje Y ("Infinite extent for field"
    # en la consola del navegador, verificado con Playwright) — bug real, no solo de
    # apariencia. Compartir literalmente la misma capa base para todo lo evita.
    columnas = [c for c, _, _ in series]
    df_largo = df.melt(id_vars=[x], value_vars=columnas, var_name="_serie", value_name="_valor")

    escala_color = alt.Scale(domain=dominio, range=rango)
    base = alt.Chart(df_largo).encode(
        x=alt.X(f"{x}:N", title=None, sort=orden_x, axis=alt.Axis(grid=False, domain=False, ticks=False)),
        y=alt.Y("_valor:Q", title=None, axis=alt.Axis(grid=True, gridColor=grid, domain=False, ticks=False)),
        color=alt.Color("_serie:N", scale=escala_color, legend=None),
        detail="_serie:N",  # una línea/área continua por serie, no una sola mezclada
    )

    area = base.mark_area(interpolate="monotone", line=False, opacity=0.18)
    linea = base.mark_line(interpolate="monotone", strokeWidth=2.5)

    # Objetivo de hover invisible en cada punto -- más fácil de acertar con el
    # mouse/dedo que la línea de 2px, y es lo que dispara el tooltip.
    hover = base.mark_circle(size=110, opacity=0).encode(
        tooltip=[
            alt.Tooltip(f"{x}:N", title=""),
            alt.Tooltip("_serie:N", title="Serie"),
            alt.Tooltip("_valor:Q", title="Valor"),
        ]
    )

    # Punto + etiqueta destacados solo en el último dato de cada serie.
    base_final = base.transform_filter(alt.datum[x] == ultimo_x)
    punto_final = base_final.mark_circle(size=90, stroke=fondo, strokeWidth=3)
    etiqueta_final = base_final.mark_text(
        dy=-16, fontWeight="bold", fontSize=13, color=texto_etiqueta, font=_FUENTE
    ).encode(text=alt.Text("_valor:Q", format=".0f"), color=alt.value(texto_etiqueta))

    return (
        alt.layer(area, linea, hover, punto_final, etiqueta_final)
        .properties(height=altura, width="container", background=fondo)
        .configure_view(strokeWidth=0)
        .configure_axis(labelFont=_FUENTE, labelColor=texto_eje, labelFontSize=11)
    )


def barras_estado(df: pd.DataFrame, x: str, y: str, *, dominio: list[str], rango: list[str],
                   altura: int = 220, oscuro: bool = False) -> alt.LayerChart:
    """Barras con color de estado fijo (ej. Activo=verde, Inactivo=gris) — nunca
    colores categóricos genéricos: el significado de cada color está reservado."""
    t = _tema_grafico(oscuro)
    resaltado = alt.selection_point(on="mouseover", fields=[x], empty=False)

    barras = (
        _base(df, x, y, t["grid"])
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=40)
        .encode(
            color=alt.Color(f"{x}:N", scale=alt.Scale(domain=dominio, range=rango), legend=None),
            opacity=alt.condition(resaltado, alt.value(1.0), alt.value(0.88)),
            tooltip=[alt.Tooltip(f"{x}:N", title=""), alt.Tooltip(f"{y}:Q", title="Empleados")],
        )
        .add_params(resaltado)
    )
    etiquetas = _base(df, x, y, t["grid"]).mark_text(
        dy=-8, fontWeight="bold", color=t["texto_dato"], font=_FUENTE
    ).encode(text=alt.Text(f"{y}:Q", format="d"))
    return (
        (barras + etiquetas)
        .properties(height=altura, background=t["fondo"])
        .configure_view(strokeWidth=0)
        .configure_axis(labelFont=_FUENTE, labelColor=t["texto_eje"], labelFontSize=12)
    )
