"""
test_relative_and_card.py — Score relativo à referência e cartão ambiental.
"""

import math

import pytest

from green_ml_score.reporting import EnvironmentalCard
from green_ml_score.scoring import relative_to_reference

KWH_TO_J = 3.6e6


def test_marginal_cost_in_joules_per_f1_point() -> None:
    s = relative_to_reference(
        energy_kwh=3e-6, f1=0.92, reference_energy_kwh=1e-6, reference_f1=0.90
    )
    assert s.energy_ratio == pytest.approx(3.0)
    assert s.delta_f1_points == pytest.approx(2.0)
    assert s.marginal_cost_j_per_f1_point == pytest.approx(2e-6 * KWH_TO_J / 2.0)
    assert not s.dominated and not s.is_reference


@pytest.mark.parametrize("f1", [0.90, 0.85])
def test_no_f1_gain_is_dominated(f1: float) -> None:
    s = relative_to_reference(2e-6, f1, 1e-6, 0.90)
    assert s.dominated
    assert math.isnan(s.marginal_cost_j_per_f1_point)


def test_reference_itself() -> None:
    s = relative_to_reference(1e-6, 0.9, 1e-6, 0.9, is_reference=True)
    assert s.is_reference and not s.dominated
    assert s.energy_ratio == 1.0
    assert math.isnan(s.marginal_cost_j_per_f1_point)


@pytest.mark.parametrize(
    "args",
    [(-1.0, 0.9, 1.0, 0.9), (1.0, 0.9, 0.0, 0.9), (1.0, 1.2, 1.0, 0.9)],
)
def test_relative_validates_inputs(args: tuple) -> None:
    with pytest.raises(ValueError):
        relative_to_reference(*args)


def _card(**kw) -> EnvironmentalCard:
    base = dict(
        model="XGBoost",
        dataset="breast_cancer",
        n_runs=10,
        accuracy_mean=0.95,
        accuracy_std=0.01,
        f1_mean=0.94,
        f1_std=0.02,
        train_energy_median_kwh=1e-5,
        train_energy_iqr_kwh=1e-6,
        train_wall_time_median_s=0.5,
        carbon_median_kg=1.2e-6,
        water_median_l=5.2e-6,
        gms_median=40.0,
        carbon_intensity_g_per_kwh=120.0,
        wue_l_per_kwh=0.52,
        train_energy_net_median_kwh=4e-6,
        idle_power_w=6.5,
        reference_model="Logistic_Regression",
        energy_ratio_median=5.0,
        marginal_cost_median_j_per_f1_point=12.5,
        dominated_share=0.2,
        tracking_modes=["machine"],
        ram_share_median=0.3,
        provenance_warnings=["tracking_mode = machine: ..."],
    )
    return EnvironmentalCard(**{**base, **kw})


def test_card_markdown_contains_all_sections() -> None:
    md = _card().to_markdown()
    assert md.startswith("# Cartão ambiental — XGBoost")
    assert "36 J" in md  # 1e-5 kWh = 36 J
    assert "Energia líquida" in md and "14.4 J" in md
    assert "Comparação com a referência (Logistic_Regression)" in md
    assert "20% das sementes" in md
    assert "⚠ tracking_mode = machine" in md


def test_card_for_reference_and_missing_values() -> None:
    md = _card(
        model="Logistic_Regression",
        accuracy_std=None,
        train_energy_net_median_kwh=None,
        ram_share_median=None,
        provenance_warnings=[],
    ).to_markdown()
    assert "Este é o modelo de referência" in md
    assert "—" in md
    assert "⚠" not in md
