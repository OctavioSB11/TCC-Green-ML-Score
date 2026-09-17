import pytest

from green_ml_score.estimators import (
    calculate_carbon_emissions,
    calculate_water_usage,
)

# ── Estimador de carbono: C = E × IC_região (Seção 4.2.2 do TCC) ──────────────


def test_carbon_emissions_formula():
    """1 kWh em São Paulo (IC=120 gCO2e/kWh) → 0.12 kg CO2e."""
    assert calculate_carbon_emissions(1.0, 120) == pytest.approx(0.12)


def test_carbon_emissions_us_grid():
    """2 kWh em data center dos EUA (IC=380 gCO2e/kWh) → 0.76 kg CO2e."""
    assert calculate_carbon_emissions(2.0, 380) == pytest.approx(0.76)


def test_carbon_emissions_zero_energy():
    assert calculate_carbon_emissions(0.0, 380) == 0.0


def test_carbon_emissions_negative_energy_raises():
    with pytest.raises(ValueError):
        calculate_carbon_emissions(-1.0, 120)


def test_carbon_emissions_negative_intensity_raises():
    with pytest.raises(ValueError):
        calculate_carbon_emissions(1.0, -120)


# ── Estimador de água: W ≈ E × WUE (Seção 2.8 do TCC) ─────────────────────────


def test_water_usage_formula():
    """10 kWh com WUE do Google 2024 (0.52 L/kWh) → 5.2 L."""
    assert calculate_water_usage(10.0, 0.52) == pytest.approx(5.2)


def test_water_usage_negative_energy_raises():
    with pytest.raises(ValueError, match="energy_kwh"):
        calculate_water_usage(-1.0)


def test_water_usage_negative_wue_raises():
    with pytest.raises(ValueError, match="wue_liters_per_kwh"):
        calculate_water_usage(10.0, -0.5)
