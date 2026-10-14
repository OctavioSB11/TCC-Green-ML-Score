"""
test_protocol.py — Protocolo de medição da semana 2: repouso (P₀), energia líquida,
avisos de procedência e score relativo no experimento.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from experiments import comparative_experiment as ce
from green_ml_score.collectors.codecarbon import (
    MeasurementDetails,
    MeasurementError,
    provenance_warnings_for,
)

KWH_TO_J = 3.6e6


class FakeTracker:
    """Substitui o GreenMLTracker: energia e duração de sessão predefinidas."""

    energy_kwh_value = 0.0
    duration_s = 10.0

    def __init__(self, **_: object) -> None:
        self.energy_kwh = 0.0
        self.details = MeasurementDetails()

    def start(self) -> None:
        pass

    def stop(self) -> None:
        self.energy_kwh = type(self).energy_kwh_value
        self.details = MeasurementDetails(
            duration_s=type(self).duration_s, tracking_mode="machine"
        )


# ---------------------------------------------------------------------------
# Repouso e energia líquida
# ---------------------------------------------------------------------------


def test_measure_idle_power(monkeypatch) -> None:
    FakeTracker.energy_kwh_value, FakeTracker.duration_s = 100.0 / KWH_TO_J, 20.0
    monkeypatch.setattr(ce, "GreenMLTracker", FakeTracker)
    monkeypatch.setattr(ce.time, "sleep", lambda _: None)
    idle = ce.measure_idle(20.0, {})
    assert idle.power_w == pytest.approx(5.0)  # 100 J / 20 s
    assert idle.duration_s == 20.0


def test_measure_idle_without_energy_raises(monkeypatch) -> None:
    FakeTracker.energy_kwh_value = 0.0
    monkeypatch.setattr(ce, "GreenMLTracker", FakeTracker)
    monkeypatch.setattr(ce.time, "sleep", lambda _: None)
    with pytest.raises(MeasurementError):
        ce.measure_idle(1.0, {})
    with pytest.raises(ValueError):
        ce.measure_idle(0.0, {})


def test_measure_phase_net_energy_uses_session_duration(monkeypatch) -> None:
    # Sessão de 10 s, 200 J brutos, P₀ = 5 W → 150 J líquidos; 5 repetições
    FakeTracker.energy_kwh_value, FakeTracker.duration_s = 200.0 / KWH_TO_J, 10.0
    monkeypatch.setattr(ce, "GreenMLTracker", FakeTracker)
    calls = []
    phase, result = ce.measure_phase(lambda: calls.append(1) or "ok", 5, {}, 5.0)
    assert len(calls) == 5 and result == "ok"
    assert phase.energy_kwh * KWH_TO_J == pytest.approx(40.0)
    assert phase.energy_net_kwh * KWH_TO_J == pytest.approx(30.0)
    assert phase.session_s == 10.0
    assert phase.tracking_mode == "machine"


def test_net_energy_can_be_negative(monkeypatch) -> None:
    """Valores líquidos negativos (carga abaixo do ruído) são mantidos, não truncados."""
    FakeTracker.energy_kwh_value, FakeTracker.duration_s = 10.0 / KWH_TO_J, 10.0
    monkeypatch.setattr(ce, "GreenMLTracker", FakeTracker)
    phase, _ = ce.measure_phase(lambda: None, 1, {}, 5.0)
    assert phase.energy_net_kwh * KWH_TO_J == pytest.approx(-40.0)


def test_warm_up_fits_each_model_once() -> None:
    from sklearn.dummy import DummyClassifier

    X, y = [[0], [1], [0], [1]], [0, 1, 0, 1]
    with patch.object(DummyClassifier, "fit", autospec=True) as fit:
        fit.side_effect = lambda self, *_: self
        with patch.object(DummyClassifier, "predict", return_value=[0, 1]):
            ce.warm_up({"a": DummyClassifier(), "b": DummyClassifier()}, (X, X, y, y))
    assert fit.call_count == 2


# ---------------------------------------------------------------------------
# Procedência
# ---------------------------------------------------------------------------


def test_provenance_warnings() -> None:
    d = MeasurementDetails(
        cpu_energy_kwh=1.0,
        ram_energy_kwh=3.0,
        ram_power_w=10.0,
        tracking_mode="machine",
    )
    msgs = provenance_warnings_for([d, d])
    assert len(msgs) == 3
    assert any("machine" in m for m in msgs)
    assert any("75%" in m for m in msgs)
    assert any("constante" in m for m in msgs)


def test_no_provenance_warnings_for_measured_process() -> None:
    a = MeasurementDetails(
        cpu_energy_kwh=3.0,
        ram_energy_kwh=1.0,
        ram_power_w=10.0,
        tracking_mode="process",
    )
    b = MeasurementDetails(
        cpu_energy_kwh=3.0,
        ram_energy_kwh=1.0,
        ram_power_w=11.0,
        tracking_mode="process",
    )
    assert provenance_warnings_for([a, b]) == []
    assert a.provenance_warnings() == []
    # Uma única medição não permite concluir que a RAM é constante
    assert provenance_warnings_for([a]) == []


# ---------------------------------------------------------------------------
# Score relativo no experimento
# ---------------------------------------------------------------------------


def _results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "seed": [1, 1, 1, 2, 2, 2],
            "model_name": ["LR", "RF", "MLP"] * 2,
            "energy_kwh": [1e-6, 4e-6, 3e-6, 2e-6, 4e-6, 3e-6],
            "f1_macro": [0.90, 0.92, 0.89, 0.90, 0.90, 0.95],
        }
    )


def test_add_relative_scores_paired_by_seed() -> None:
    out = ce.add_relative_scores(_results(), "LR").set_index(["seed", "model_name"])
    assert out.loc[(1, "LR"), "energy_ratio_ref"] == 1.0
    assert not out.loc[(1, "LR"), "dominated"]
    assert out.loc[(1, "RF"), "energy_ratio_ref"] == pytest.approx(4.0)
    assert out.loc[(1, "RF"), "marginal_cost_j_per_f1_point"] == pytest.approx(
        3e-6 * KWH_TO_J / 2.0
    )
    assert out.loc[(1, "MLP"), "dominated"]
    assert out.loc[(2, "RF"), "dominated"]  # ΔF1 = 0
    assert out.loc[(2, "MLP"), "energy_ratio_ref"] == pytest.approx(1.5)


def test_add_relative_scores_requires_reference() -> None:
    with pytest.raises(ValueError, match="ausente"):
        ce.add_relative_scores(_results(), "XGBoost")


# ---------------------------------------------------------------------------
# Janela mínima de medição
# ---------------------------------------------------------------------------


def test_measure_phase_repeats_until_min_window(monkeypatch) -> None:
    """Ação de 1 s com janela mínima de 3,5 s: 4 repetições, valores por repetição."""
    FakeTracker.energy_kwh_value, FakeTracker.duration_s = 400.0 / KWH_TO_J, 5.0
    monkeypatch.setattr(ce, "GreenMLTracker", FakeTracker)
    clock = [0.0]
    monkeypatch.setattr(ce.time, "perf_counter", lambda: clock[0])

    def action() -> None:
        clock[0] += 1.0

    phase, _ = ce.measure_phase(action, 1, {}, idle_power_w=0.0, min_window_s=3.5)
    assert phase.repetitions == 4
    assert phase.wall_time_s == pytest.approx(1.0)
    assert phase.energy_kwh * KWH_TO_J == pytest.approx(100.0)


def test_measure_phase_respects_minimum_repetitions(monkeypatch) -> None:
    """Com janela já atingida, o mínimo de repetições continua valendo."""
    FakeTracker.energy_kwh_value, FakeTracker.duration_s = 1.0 / KWH_TO_J, 5.0
    monkeypatch.setattr(ce, "GreenMLTracker", FakeTracker)
    clock = [0.0]
    monkeypatch.setattr(ce.time, "perf_counter", lambda: clock[0])

    def slow() -> None:
        clock[0] += 10.0

    phase, _ = ce.measure_phase(slow, 3, {}, min_window_s=1.0)
    assert phase.repetitions == 3
