"""
test_contexts.py — Contextos de execução e avaliação modelo × contexto.
"""

import math

import numpy as np
import pytest

from green_ml_score.contexts import (
    ExecutionContext,
    evaluate_configurations,
    kendall_tau_b,
    load_contexts_csv,
    simplex_grid,
)
from green_ml_score.scoring import NormalizationBounds, Weights, calculate_gms

HEADER = "name,hour,carbon_intensity_g_per_kwh,pue,wue_onsite_l_per_kwh,offsite_water_l_per_kwh,source\n"


def _ctx(name: str, ic: float, wue: float = 0.0, ewif: float = 1.0, **kw):
    return ExecutionContext(name, ic, wue, ewif, **kw)


# ---------------------------------------------------------------------------
# ExecutionContext
# ---------------------------------------------------------------------------


def test_context_converts_energy_with_pue() -> None:
    ctx = _ctx("DC", ic=400.0, wue=1.5, ewif=2.0, pue=1.2)
    m = ctx.metrics(2.0)
    assert m.energy == 2.0
    assert m.carbon == pytest.approx(2.0 * 1.2 * 400.0 / 1000.0)
    assert m.water == pytest.approx(2.0 * 1.5 + 2.0 * 1.2 * 2.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"carbon_intensity_g_per_kwh": -1.0},
        {"wue_onsite_l_per_kwh": -0.1},
        {"offsite_water_l_per_kwh": -0.1},
        {"pue": 0.9},
        {"hour": 24},
        {"name": ""},
    ],
)
def test_context_rejects_invalid_values(kwargs: dict) -> None:
    base = {
        "name": "X",
        "carbon_intensity_g_per_kwh": 100.0,
        "wue_onsite_l_per_kwh": 0.0,
        "offsite_water_l_per_kwh": 1.0,
    }
    with pytest.raises(ValueError):
        ExecutionContext(**{**base, **kwargs})


def test_context_label_includes_hour() -> None:
    assert _ctx("BR", 100.0).label == "BR"
    assert _ctx("BR", 100.0, hour=7).label == "BR@07h"


def test_load_contexts_csv(tmp_path) -> None:
    path = tmp_path / "c.csv"
    path.write_text(
        HEADER + "BR,,100,,0,1.5,ONS\nDE,14,350,1.1,1.8,2.0,EEA\n", encoding="utf-8"
    )
    ctxs = load_contexts_csv(path)
    assert [c.label for c in ctxs] == ["BR", "DE@14h"]
    assert ctxs[0].pue == 1.0 and ctxs[0].hour is None and ctxs[0].source == "ONS"
    assert ctxs[1].pue == 1.1


def test_load_contexts_csv_rejects_empty_file(tmp_path) -> None:
    path = tmp_path / "c.csv"
    path.write_text(HEADER, encoding="utf-8")
    with pytest.raises(ValueError, match="Nenhum contexto"):
        load_contexts_csv(path)


def test_load_contexts_csv_rejects_duplicates_and_bad_values(tmp_path) -> None:
    dup = tmp_path / "dup.csv"
    dup.write_text(HEADER + "BR,,100,,0,1,\nBR,,120,,0,1,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicados"):
        load_contexts_csv(dup)
    bad = tmp_path / "bad.csv"
    bad.write_text(HEADER + "BR,,abc,,0,1,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Linha 2"):
        load_contexts_csv(bad)


def test_template_contexts_file_is_valid_but_empty() -> None:
    """O CSV versionado tem o cabeçalho correto e nenhum valor inventado."""
    with pytest.raises(ValueError, match="Nenhum contexto"):
        load_contexts_csv("experiments/contexts/contexts.csv")


# ---------------------------------------------------------------------------
# Kendall e simplex
# ---------------------------------------------------------------------------


def test_kendall_tau_b_matches_scipy() -> None:
    stats = pytest.importorskip("scipy.stats")
    rng = np.random.default_rng(1)
    x = rng.integers(0, 5, 30).astype(float)  # com empates
    y = x + rng.normal(0, 1.5, 30)
    assert kendall_tau_b(x, y) == pytest.approx(stats.kendalltau(x, y).statistic)


def test_kendall_tau_b_extremes() -> None:
    assert kendall_tau_b([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)
    assert kendall_tau_b([1, 2, 3], [30, 20, 10]) == pytest.approx(-1.0)
    assert math.isnan(kendall_tau_b([1, 1, 1], [1, 2, 3]))


def test_simplex_grid() -> None:
    grid = simplex_grid(0.1)
    assert len(grid) == 66  # C(10 + 2, 2)
    for w in grid:
        w.validate()
    with pytest.raises(ValueError):
        simplex_grid(0.3)


# ---------------------------------------------------------------------------
# evaluate_configurations
# ---------------------------------------------------------------------------


def test_single_context_reduces_to_energy_ranking() -> None:
    """Com um único contexto, IC e WUE são constantes: τ_b = 1 em todo o simplex."""
    ev = evaluate_configurations(
        {"A": 1.0, "B": 2.0, "C": 3.0}, [_ctx("BR", 100.0, wue=0.5)], simplex_step=0.1
    )
    assert ev.kendall_tau == pytest.approx(1.0)
    assert np.allclose(ev.sensitivity["kendall_tau"], 1.0)
    assert ev.selection_change_share == 0.0
    assert ev.energy_best_model == "A"


def test_gms_matches_calculate_gms_with_global_bounds() -> None:
    ctxs = [_ctx("BR", 100.0, ewif=1.0), _ctx("PL", 700.0, ewif=3.0)]
    ev = evaluate_configurations({"A": 1.0, "B": 2.0}, ctxs)
    metrics = [c.metrics(e) for e in (1.0, 2.0) for c in ctxs]
    bounds = NormalizationBounds.from_metrics_list(metrics)
    expected = sorted(
        (calculate_gms(m, bounds, Weights(), scale_100=True) for m in metrics),
        reverse=True,
    )
    np.testing.assert_allclose(ev.configurations["gms"], expected)


def test_context_can_change_selection() -> None:
    """Modelo um pouco mais custoso em região limpa supera o mais econômico em região suja."""
    ctxs = [_ctx("CLEAN", 20.0, ewif=0.1), _ctx("DIRTY", 800.0, ewif=4.0)]
    ev = evaluate_configurations({"A": 1.0, "B": 1.1}, ctxs, simplex_step=0.1)
    assert ev.kendall_tau < 1.0
    top = ev.configurations.iloc[0]
    assert top["context"] == "CLEAN"
    # Com peso todo em energia, o melhor é o modelo de menor energia
    energy_only = ev.sensitivity.query("w_E == 1.0").iloc[0]
    assert energy_only["best_uses_energy_best_model"]
    assert ev.summary()["n_configurations"] == 4


def test_evaluate_configurations_validates_inputs() -> None:
    with pytest.raises(ValueError):
        evaluate_configurations({}, [_ctx("BR", 100.0)])
    with pytest.raises(ValueError):
        evaluate_configurations({"A": 1.0}, [])
    with pytest.raises(ValueError):
        evaluate_configurations({"A": 1.0}, [_ctx("BR", 100.0), _ctx("BR", 200.0)])
