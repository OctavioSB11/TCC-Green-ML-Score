import pytest
from green_ml_score.scoring import (
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
    calculate_gms,
    explain_gms,
)


# ── Testes originais (validam os exemplos numéricos do TCC) ──────────────────

def test_gms_calculation_equal_weights():
    """Modelo A do TCC — seção 7.2"""
    metrics = EnvironmentalMetrics(energy=100, carbon=50, water=200)
    bounds  = NormalizationBounds(energy_max=200, carbon_max=80, water_max=300)
    weights = Weights(w_E=1/3, w_C=1/3, w_W=1/3)

    score = calculate_gms(metrics, bounds, weights)

    # E_norm=0.5, C_norm=0.375, W_norm=0.3333 → GMS≈0.4027
    assert abs(score - 0.4027) < 0.001


def test_gms_worst_case():
    """Modelo B do TCC — maior consumo em todas as dimensões → GMS = 0"""
    metrics = EnvironmentalMetrics(energy=200, carbon=80, water=300)
    bounds  = NormalizationBounds(energy_max=200, carbon_max=80, water_max=300)
    weights = Weights(w_E=1/3, w_C=1/3, w_W=1/3)

    assert calculate_gms(metrics, bounds, weights) == 0.0


def test_gms_best_case():
    """Consumo zero em todas as dimensões → GMS = 1.0"""
    metrics = EnvironmentalMetrics(energy=0, carbon=0, water=0)
    bounds  = NormalizationBounds(energy_max=200, carbon_max=80, water_max=300)
    weights = Weights(w_E=1/3, w_C=1/3, w_W=1/3)

    assert calculate_gms(metrics, bounds, weights) == 1.0


def test_invalid_weights():
    with pytest.raises(ValueError, match="Os pesos devem somar 1"):
        Weights(w_E=0.5, w_C=0.5, w_W=0.5).validate()


# ── Testes novos (cobrem as correções aplicadas) ──────────────────────────────

def test_default_weights_are_uniform():
    """Pesos padrão devem ser 1/3 cada, conforme Seção 6 do TCC."""
    w = Weights()
    assert abs(w.w_E - 1/3) < 1e-9
    assert abs(w.w_C - 1/3) < 1e-9
    assert abs(w.w_W - 1/3) < 1e-9


def test_calculate_gms_default_weights_no_mutation():
    """
    Chamar calculate_gms sem passar weights duas vezes deve produzir
    o mesmo resultado — garante que não há mutable default argument.
    """
    metrics = EnvironmentalMetrics(energy=100, carbon=50, water=200)
    bounds  = NormalizationBounds(energy_max=200, carbon_max=80, water_max=300)

    score1 = calculate_gms(metrics, bounds)
    score2 = calculate_gms(metrics, bounds)

    assert score1 == score2
    assert abs(score1 - 0.4027) < 0.001


def test_normalization_bounds_from_metrics_list():
    """from_metrics_list() deve capturar o máximo de cada dimensão."""
    m1 = EnvironmentalMetrics(energy=100, carbon=50,  water=200)
    m2 = EnvironmentalMetrics(energy=200, carbon=80,  water=300)
    m3 = EnvironmentalMetrics(energy=150, carbon=60,  water=250)

    bounds = NormalizationBounds.from_metrics_list([m1, m2, m3])

    assert bounds.energy_max == 200
    assert bounds.carbon_max == 80
    assert bounds.water_max  == 300