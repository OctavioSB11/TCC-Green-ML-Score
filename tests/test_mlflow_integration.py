"""
test_mlflow_integration.py — Testes unitários para o conector MLflow.

Aplica o padrão CTFL / ISTQB:
- Testes isolados com Mocks para as funções de logging do MLflow.
- Validação do oráculo: todas as métricas essenciais e parâmetros ambientais devem ser registrados.
"""

from unittest.mock import MagicMock, patch

import pytest

from green_ml_score.integrations.mlflow import log_greenml_run
from green_ml_score.scoring.gms import EnvironmentalMetrics


@patch("green_ml_score.integrations.mlflow.mlflow")
def test_log_greenml_run_all_metrics_logged(
    mock_mlflow, sample_bounds, uniform_weights
):
    """Testa se todas as métricas ambientais e o GMS final escalado são logados no MLflow."""
    # Arrange
    mock_tracker = MagicMock()
    mock_tracker.get_metrics.return_value = EnvironmentalMetrics(
        energy=100.0, carbon=50.0, water=200.0
    )
    mock_tracker.carbon_intensity = 120.0
    mock_tracker.wue = 0.52

    # Act
    gms_result = log_greenml_run(
        tracker=mock_tracker,
        bounds=sample_bounds,
        weights=uniform_weights,
    )

    # Assert
    # GMS para 100/200, 50/80, 200/300 na escala 100 deve ser ~40.27
    assert gms_result == pytest.approx(40.277, rel=1e-3)

    # Verifica chamadas de métricas
    metric_calls = {
        call.args[0]: call.args[1] for call in mock_mlflow.log_metric.call_args_list
    }
    assert metric_calls["greenml_energy_kwh"] == 100.0
    assert metric_calls["greenml_carbon_kg"] == 50.0
    assert metric_calls["greenml_water_liters"] == 200.0
    assert metric_calls["GreenML_Score"] == pytest.approx(40.277, rel=1e-3)

    # Verifica chamadas de parâmetros
    param_calls = {
        call.args[0]: call.args[1] for call in mock_mlflow.log_param.call_args_list
    }
    assert param_calls["greenml_carbon_intensity"] == 120.0
    assert param_calls["greenml_wue"] == 0.52
    assert param_calls["greenml_energy_max_bound"] == sample_bounds.energy_max


@patch("green_ml_score.integrations.mlflow.mlflow")
def test_log_greenml_run_default_weights_fallback(mock_mlflow, sample_bounds):
    """Testa se a função utiliza pesos uniformes por padrão quando weights=None."""
    mock_tracker = MagicMock()
    mock_tracker.get_metrics.return_value = EnvironmentalMetrics(
        energy=0.0, carbon=0.0, water=0.0
    )
    mock_tracker.carbon_intensity = 0.0
    mock_tracker.wue = 1.8

    gms_result = log_greenml_run(tracker=mock_tracker, bounds=sample_bounds)

    # Para consumo 0, GMS na escala 100 deve ser 100.0
    assert gms_result == 100.0
    mock_mlflow.log_metric.assert_any_call("GreenML_Score", 100.0)
