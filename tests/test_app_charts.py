"""Testes dos gráficos do GreenML Dashboard (app/core/charts.py)."""

import math

import pytest

from app.core import charts, data


@pytest.mark.parametrize("dataset", ["newsgroups", "breast_cancer", "covtype"])
def test_overview_figures_build_for_every_dataset(dataset: str) -> None:
    summary = data.model_summary(dataset)
    rank = charts.rank_chart(summary)
    assert len(rank.data) == 4
    # Eixo de posição invertido: 1º lugar no topo.
    assert rank.layout.yaxis.range[0] > rank.layout.yaxis.range[1]
    seeds = charts.seed_energy_chart(data.load_runs(dataset))
    assert len(seeds.data) == 4
    assert all(len(trace.y) == 10 for trace in seeds.data)


def test_bar_axis_leaves_room_for_labels() -> None:
    summary = data.model_summary("covtype")
    linear = charts.metric_bars(summary, "water_ul", "Água")
    assert linear.layout.xaxis.range[1] >= 1.2 * summary.water_ul.max()
    log = charts.metric_bars(summary, "energy_mwh_mean", "Energia", log=True)
    assert log.layout.xaxis.type == "log"
    assert log.layout.xaxis.range[1] > math.log10(summary.energy_mwh_mean.max())


def test_pareto_chart_marks_frontier_and_dominated() -> None:
    summary = data.model_summary("covtype")
    fig = charts.pareto_chart(summary, data.seed_points("covtype"))
    names = [t.name for t in fig.data]
    assert "Fronteira de Pareto" in names
    assert "MLP (dominado)" in names
    assert "XGBoost" in names and "Regressão Logística (referência)" in names
    front = next(t for t in fig.data if t.name == "Fronteira de Pareto")
    assert len(front.x) == 3  # RL, XGBoost e Random Forest
    xgb = next(t for t in fig.data if t.name == "XGBoost")
    assert "1,64 J por ponto de F1" in xgb.hovertemplate


def test_simulator_figures_for_carbon_only_covertype() -> None:
    w = data.make_weights(0, 1, 0)
    sim = data.simulate("covtype", w)
    table = data.map_table(sim, "XGBoost")
    world = charts.context_map(table, "XGBoost")
    assert len(world.data[0].lat) == 7
    assert "star" in list(world.data[0].marker.symbol)
    heat = charts.gms_heatmap(sim["configurations"], list(sim["k"].index))
    assert list(heat.data[0].x) == list(sim["k"].index)
    assert "★" in heat.data[0].text[0][0]  # RL no contexto de menor k
    tri = charts.simplex_chart(sim["sensitivity"], w)
    assert tri.data[-1].name == "Pesos atuais"
    assert len(tri.data) >= 3
    tau = charts.simplex_chart(sim["sensitivity"], w, color_by="tau")
    assert len(tau.data) == 2
