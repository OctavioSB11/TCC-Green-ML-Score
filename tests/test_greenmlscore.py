import pytest
from green_ml_score.greenmlscore import EnvironmentalMetrics, NormalizationBounds, Weights, calculate_gms, explain_gms

def test_gms_calculation_equal_weights():
    # Dados do artigo: Modelo A
    metrics = EnvironmentalMetrics(energy=100, carbon=50, water=200)
    bounds = NormalizationBounds(energy_max=200, carbon_max=80, water_max=300)
    weights = Weights(w_E=1/3, w_C=1/3, w_W=1/3)
    
    score = calculate_gms(metrics, bounds, weights)
    
    # E_norm = 1 - (100/200) = 0.5
    # C_norm = 1 - (50/80) = 0.375
    # W_norm = 1 - (200/300) = 0.3333...
    # GMS = (0.5 + 0.375 + 0.3333...) / 3 = 0.40277...
    
    assert abs(score - 0.4027) < 0.001

def test_gms_worst_case():
    # Modelo B do artigo
    metrics = EnvironmentalMetrics(energy=200, carbon=80, water=300)
    bounds = NormalizationBounds(energy_max=200, carbon_max=80, water_max=300)
    weights = Weights(w_E=1/3, w_C=1/3, w_W=1/3)
    
    score = calculate_gms(metrics, bounds, weights)
    
    assert score == 0.0

def test_gms_best_case():
    # Modelo com zero consumo
    metrics = EnvironmentalMetrics(energy=0, carbon=0, water=0)
    bounds = NormalizationBounds(energy_max=200, carbon_max=80, water_max=300)
    weights = Weights(w_E=1/3, w_C=1/3, w_W=1/3)
    
    score = calculate_gms(metrics, bounds, weights)
    
    assert score == 1.0

def test_invalid_weights():
    with pytest.raises(ValueError, match="Os pesos devem somar 1"):
        Weights(w_E=0.5, w_C=0.5, w_W=0.5).validate()
