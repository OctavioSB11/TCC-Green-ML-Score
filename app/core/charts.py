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


def pareto_chart(
    summary: pd.DataFrame,
    seeds: pd.DataFrame | None = None,
) -> go.Figure:
    """
    F1-Score × energia (escala log): pontos de cada semente, mediana de cada modelo,
    fronteira de Pareto e, ao passar o mouse, o custo frente à Regressão Logística.
    """
    fig = go.Figure()
    if seeds is not None:
        for model in summary.index:
            sub = seeds[seeds.model == model]
            fig.add_trace(
                go.Scatter(
                    x=sub.energy_mwh,
                    y=sub.f1,
                    mode="markers",
                    name=f"{data.model_label(model)} (sementes)",
                    legendgroup=model,
                    showlegend=False,
                    marker={
                        "color": theme.MODEL_COLORS.get(model, theme.GREY),
                        "size": 8,
                        "opacity": 0.35,
                    },
                    customdata=sub.seed,
                    hovertemplate="Semente %{customdata}<br>%{x:.3f} mWh<br>"
                    "F1 %{y:.3f}<extra>" + data.model_label(model) + "</extra>",
                )
            )
    front = summary[summary.pareto].sort_values("energy_mwh_median")
    fig.add_trace(
        go.Scatter(
            x=front.energy_mwh_median,
            y=front.f1_mean,
            mode="lines",
            line={"color": theme.GREEN_DARK, "width": 2, "dash": "dot", "shape": "hv"},
            name="Fronteira de Pareto",
            hoverinfo="skip",
        )
    )
    for model, row in summary.iterrows():
        is_ref = model == data.REFERENCE_MODEL
        color = theme.MODEL_COLORS.get(model, theme.GREY)
        if is_ref:
            detail = "Referência"
        else:
            cost = row.get("marginal_cost_j")
            detail = (
                f"E/E_RL: {theme.fmt(row.energy_ratio_ref, 1)} vezes<br>"
                f"ΔF1: {theme.fmt(row.delta_f1_points, 1)} pontos<br>"
                + (
                    f"Custo marginal: {theme.fmt(cost, 2)} J por ponto de F1"
                    if cost is not None and cost == cost
                    else "Custo marginal: não se aplica (não supera a RL)"
                )
            )
        status = "na fronteira" if row.pareto else "dominado"
        fig.add_trace(
            go.Scatter(
                x=[row.energy_mwh_median],
                y=[row.f1_mean],
                error_y={"type": "data", "array": [row.f1_std], "color": color},
                mode="markers+text",
                name=data.model_label(model)
                + (" (referência)" if is_ref else "")
                + ("" if row.pareto else " (dominado)"),
                legendgroup=model,
                marker={
                    "color": color if row.pareto else "white",
                    "symbol": "star" if is_ref else "circle",
                    "size": 22 if is_ref else 18,
                    "line": {"color": color, "width": 3},
                },
                text=[data.model_label(model)],
                textposition="top center",
                hovertemplate=(
                    f"<b>{data.model_label(model)}</b> ({status})<br>"
                    f"Energia (mediana): {theme.fmt_auto(row.energy_mwh_median)} mWh<br>"
                    f"F1 (média): {theme.fmt(row.f1_mean, 3)}<br>{detail}<extra></extra>"
                ),
            )
        )
    fig.update_xaxes(
        type="log", title="Energia de treino por execução (mWh, escala log)"
    )
    fig.update_yaxes(title="F1-Score macro", tickformat=".2f")
    return _layout(fig, height=520)


# Escala do fator k: verde (contexto limpo) a vermelho (contexto caro).
K_SCALE = [[0.0, "#1B7F3B"], [0.5, "#F2C14E"], [1.0, "#B3261E"]]


LABEL_POSITION: dict[str, str] = {
    "AWS-Stockholm": "top center",
    "FR-local": "middle left",
    "AWS-Frankfurt": "middle right",
    "AWS-Virginia": "top center",
    "IN-local": "top center",
    "BR-local": "middle left",
    "AWS-SaoPaulo": "bottom right",
}
MAP_CONFIG = {"scrollZoom": False, "displaylogo": False}


def context_map(table: pd.DataFrame, model_label: str) -> go.Figure:
    """
    Mapa-múndi com os contextos coloridos pelo fator k relativo ao melhor contexto
    (1 = região de menor k); a melhor região aparece como estrela.
    """
    hover = [
        f"<b>{r.contexto}</b> ({r.tipo})<br>"
        f"k relativo ao melhor: {theme.fmt(r.k_rel, 2)}<br>"
        f"GMS de {model_label}: {theme.fmt(r.gms_modelo, 1)}<br>"
        f"IC: {theme.fmt(r.ic_g_kwh, 1)} gCO₂e/kWh · PUE {theme.fmt(r.pue, 2)}<br>"
        f"WUE: {theme.fmt(r.wue_l_kwh, 2)} L/kWh · água da geração "
        f"{theme.fmt(r.agua_geracao_l_kwh, 2)} L/kWh"
        for r in table.itertuples()
    ]
    fig = go.Figure(
        go.Scattergeo(
            lat=table.lat,
            lon=table.lon,
            text=[
                f"<b>{c}</b> {theme.fmt(g, 1)}"
                for c, g in zip(table.contexto, table.gms_modelo)
            ],
            mode="markers+text",
            textposition=[LABEL_POSITION.get(c, "top center") for c in table.contexto],
            textfont={"size": 13, "color": "#111111"},
            marker={
                "size": [28 if b else 18 for b in table.melhor],
                "color": table.k_rel,
                "cmin": 1,
                "colorscale": K_SCALE,
                "line": {
                    "color": ["#000000" if b else "#FFFFFF" for b in table.melhor],
                    "width": 2,
                },
                "colorbar": {
                    "title": {"text": "k relativo<br>ao melhor"},
                    "thickness": 14,
                    "tickformat": ".1f",
                },
                "symbol": ["star" if b else "circle" for b in table.melhor],
            },
            hovertext=hover,
            hoverinfo="text",
        )
    )
    fig.update_geos(
        projection_type="equirectangular",
        showcountries=True,
        countrycolor="#BBBBBB",
        showland=True,
        landcolor="#F3F3EE",
        showocean=True,
        oceancolor="#E6F1F7",
        showframe=False,
        lataxis_range=[-38, 68],
        lonaxis_range=[-95, 92],
    )
    fig = _layout(fig, height=520)
    fig.update_layout(margin={"l": 0, "r": 0, "t": 10, "b": 0})
    return fig


def gms_heatmap(configurations: pd.DataFrame, context_order: list[str]) -> go.Figure:
    """GMS de cada modelo (linhas) em cada contexto (colunas, do menor ao maior k)."""
    grid = configurations.pivot(index="model", columns="context", values="gms")
    models = [m for m in data.MODEL_ORDER if m in grid.index]
    grid = grid.loc[models, context_order]
    best = configurations.iloc[0]
    text = [
        [
            theme.fmt(v, 1) + (" ★" if (m, c) == (best.model, best.context) else "")
            for c, v in row.items()
        ]
        for m, row in grid.iterrows()
    ]
    fig = go.Figure(
        go.Heatmap(
            z=grid.to_numpy(),
            x=context_order,
            y=[data.model_label(m) for m in models],
            text=text,
            texttemplate="%{text}",
            textfont={"size": 14},
            colorscale=theme.GMS_SCALE,
            zmin=0,
            zmax=100,
            colorbar={"title": {"text": "GMS"}, "thickness": 14},
            hovertemplate="%{y} em %{x}<br>GMS %{z:.1f}<extra></extra>",
        )
    )
    fig.update_yaxes(autorange="reversed")
    return _layout(fig, height=360)


def simplex_chart(
    sensitivity: pd.DataFrame, weights, color_by: str = "vencedor"
) -> go.Figure:
    """
    Triângulo de pesos: cada ponto é uma combinação (w_E, w_C, w_W) do passo de 0,05,
    colorido pela configuração vencedora ou pelo τ_b; a estrela marca os pesos atuais.
    """
    fig = go.Figure()
    if color_by == "tau":
        fig.add_trace(
            go.Scatterternary(
                a=sensitivity.w_E,
                b=sensitivity.w_C,
                c=sensitivity.w_W,
                mode="markers",
                marker={
                    "size": 11,
                    "symbol": "hexagon",
                    "color": sensitivity.kendall_tau,
                    "colorscale": "Viridis",
                    "colorbar": {"title": {"text": "τ_b"}, "thickness": 14},
                },
                hovertemplate="w_E %{a:.2f} · w_C %{b:.2f} · w_W %{c:.2f}<br>"
                "τ_b %{marker.color:.3f}<extra></extra>",
                showlegend=False,
            )
        )
    else:
        palette = [
            "#1B7F3B",
            "#1F77B4",
            "#D62728",
            "#FF7F0E",
            "#9467BD",
            "#8C564B",
            "#17BECF",
        ]
        for i, (name, sub) in enumerate(sensitivity.groupby("best_configuration")):
            model, context = name.split(" | ")
            fig.add_trace(
                go.Scatterternary(
                    a=sub.w_E,
                    b=sub.w_C,
                    c=sub.w_W,
                    mode="markers",
                    name=f"{data.model_label(model)} em {context}",
                    marker={
                        "size": 11,
                        "symbol": "hexagon",
                        "color": palette[i % len(palette)],
                    },
                    hovertemplate="w_E %{a:.2f} · w_C %{b:.2f} · w_W %{c:.2f}<extra>"
                    + f"{data.model_label(model)} em {context}</extra>",
                )
            )
    fig.add_trace(
        go.Scatterternary(
            a=[weights.w_E],
            b=[weights.w_C],
            c=[weights.w_W],
            mode="markers",
            name="Pesos atuais",
            cliponaxis=False,
            marker={
                "size": 22,
                "symbol": "star",
                "color": "#000000",
                "line": {"color": "#FFFFFF", "width": 2},
            },
            hovertemplate="Pesos atuais<extra></extra>",
        )
    )
    fig.update_layout(
        ternary={
            "aaxis": {"title": {"text": "Energia"}, "min": 0},
            "baxis": {"title": {"text": "Carbono"}, "min": 0},
            "caxis": {"title": {"text": "Água"}, "min": 0},
        }
    )
    fig = _layout(fig, height=620)
    fig.update_layout(
        margin={"l": 40, "r": 40, "t": 50, "b": 130},
        legend={"orientation": "h", "yanchor": "top", "y": -0.16, "x": 0},
    )
    return fig
