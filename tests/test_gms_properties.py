"""
Testes de propriedade que documentam formalmente o comportamento do GMS.

O teste `test_gms_reduces_to_energy_when_factors_are_constant` NÃO é um bug:
ele registra, como especificação executável, a degeneração demonstrada na
Seção 4 do texto (IC e WUE constantes ⇒ GMS = E_norm, independentemente dos pesos).
"""

import numpy as np
import pytest

from green_ml_score.scoring import EnvironmentalMetrics, NormalizationBounds, Weights, calculate_gms

RNG = np.random.default_rng(seed=0)
WEIGHT_GRID = [Weights(), Weights(0.2, 0.5, 0.3), Weights(0.3, 0.2, 0.5), Weights(1.0, 0.0, 0.0)]


def _metrics(energy: np.ndarray, ic: np.ndarray, wue: np.ndarray) -> list[EnvironmentalMetrics]:
    return [EnvironmentalMetrics(e, e * c / 1000, e * w) for e, c, w in zip(energy, ic, wue)]


@pytest.mark.parametrize("weights", WEIGHT_GRID)
def test_gms_reduces_to_energy_when_factors_are_constant(weights: Weights) -> None:
    energy = RNG.uniform(1e-6, 1e-2, size=50)
    ms = _metrics(energy, np.full(50, 120.0), np.full(50, 0.52))
    bounds = NormalizationBounds.from_metrics_list(ms)
    gms = np.array([calculate_gms(m, bounds, weights) for m in ms])
    np.testing.assert_allclose(gms, 1 - energy / energy.max(), atol=1e-12)


def test_weights_matter_when_factors_vary() -> None:
    energy = RNG.uniform(1e-6, 1e-2, size=50)
    ms = _metrics(energy, RNG.uniform(50, 700, 50), RNG.uniform(0.2, 1.8, 50))
    bounds = NormalizationBounds.from_metrics_list(ms)
    scores = {
        i: np.array([calculate_gms(m, bounds, w) for m in ms]) for i, w in enumerate(WEIGHT_GRID)
    }
    assert not np.allclose(scores[1], scores[2])


def test_score_is_relative_to_benchmark() -> None:
    """Adicionar um modelo mais custoso altera o GMS dos demais (Seção 4.3)."""
    ms = _metrics(np.array([1.0, 2.0]), np.full(2, 120.0), np.full(2, 0.52))
    before = calculate_gms(ms[0], NormalizationBounds.from_metrics_list(ms))
    ms_plus = ms + _metrics(np.array([10.0]), np.array([120.0]), np.array([0.52]))
    after = calculate_gms(ms[0], NormalizationBounds.from_metrics_list(ms_plus))
    assert after > before
