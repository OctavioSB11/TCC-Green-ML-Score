"""
charts.py: gráficos Plotly do GreenML Dashboard.

Cada função recebe tabelas já calculadas por ``data.py`` e devolve uma figura, sem
acessar arquivos. Rótulos em português, separador decimal com vírgula e as cores dos
modelos iguais às das figuras do artigo.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from app.core import data, theme

FONT = {"family": "Source Sans Pro, Arial, sans-serif", "size": 15, "color": "#111111"}


def _layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        font=FONT,
        height=height,
        margin={"l": 10, "r": 10, "t": 40, "b": 10},
        separators=",.",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
    )
    return fig


def rank_chart(summary: pd.DataFrame) -> go.Figure:
    """Posição de cada modelo em cada critério (1 no topo), ligando os pontos."""
    table = summary[list(data.CRITERIA)]
    criteria = list(data.CRITERIA.values())
    n = len(table)
    fig = go.Figure()
    for model, row in table.iterrows():
        fig.add_trace(
            go.Scatter(
                x=criteria,
                y=row.to_list(),
                mode="lines+markers+text",
                name=data.model_label(model),
                line={"color": theme.MODEL_COLORS.get(model, theme.GREY), "width": 4},
                marker={"size": 16},
                text=[f"{p}º" for p in row.to_list()],
                textposition="top center",
                hovertemplate="%{x}: %{y}º lugar<extra>"
                + data.model_label(model)
                + "</extra>",
            )
        )
    fig.update_yaxes(
        autorange="reversed",
        tickvals=list(range(1, n + 1)),
        ticktext=[f"{i}º" for i in range(1, n + 1)],
        title="Posição",
        range=[n + 0.5, 0.5],
    )
    fig.update_xaxes(title=None)
    return _layout(fig)


def seed_energy_chart(runs: pd.DataFrame) -> go.Figure:
    """Energia de treinamento por semente e modelo (escala log), com a mediana."""
    df = runs.assign(energia_mwh=runs.energy_kwh * data.KWH_TO_MWH)
    fig = go.Figure()
    for model in [m for m in data.MODEL_ORDER if m in set(df.model_name)]:
        sub = df[df.model_name == model]
        fig.add_trace(
            go.Box(
                y=sub.energia_mwh,
                name=data.model_label(model),
                boxpoints="all",
                jitter=0.4,
                pointpos=0,
                marker={"color": theme.MODEL_COLORS.get(model, theme.GREY), "size": 8},
                line={"color": theme.MODEL_COLORS.get(model, theme.GREY)},
                customdata=sub.seed,
                hovertemplate="Semente %{customdata}<br>%{y:.3f} mWh<extra></extra>",
            )
        )
    fig.update_yaxes(type="log", title="Energia de treino (mWh, escala log)")
    fig.update_layout(showlegend=False)
    return _layout(fig)


def metric_bars(
    summary: pd.DataFrame,
    column: str,
    title: str,
    log: bool = False,
    error_column: str | None = None,
) -> go.Figure:
    """Barras horizontais de uma métrica por modelo, com barra de erro opcional."""
    models = list(summary.index)
    fig = go.Figure(
        go.Bar(
            x=summary[column],
            y=[data.model_label(m) for m in models],
            orientation="h",
            marker_color=[theme.MODEL_COLORS.get(m, theme.GREY) for m in models],
            error_x=(
                {"type": "data", "array": summary[error_column], "color": "#333333"}
                if error_column
                else None
            ),
            text=[theme.fmt_auto(v) for v in summary[column]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    values = summary[column].astype(float)
    if log:
        lo, hi = np.log10(values[values > 0].min()), np.log10(values.max())
        x_range = [lo - 0.3, hi + 0.45]
    else:
        top = (values + (summary[error_column] if error_column else 0)).max()
        x_range = [0, top * 1.22]
    fig.update_xaxes(title=title, type="log" if log else "linear", range=x_range)
    fig.update_yaxes(autorange="reversed")
    _layout(fig, height=300)
    fig.update_layout(margin={"l": 10, "r": 70, "t": 20, "b": 10})
    return fig
