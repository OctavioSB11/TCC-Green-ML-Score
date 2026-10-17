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
