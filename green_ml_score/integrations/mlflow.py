"""
Integração do GreenML Score com MLflow
"""

import mlflow

from green_ml_score.collectors.codecarbon import GreenMLTracker
from green_ml_score.scoring.gms import NormalizationBounds, Weights, calculate_gms


def log_greenml_run(
    tracker: GreenMLTracker,
    bounds: NormalizationBounds,
    weights: Weights | None = None,
):
    """
    Finaliza o tracker e loga as métricas ambientais + GMS no MLflow
    """
    if weights is None:
        weights = Weights()

    metrics = tracker.get_metrics()
    gms_value = calculate_gms(metrics, bounds, weights, scale_100=True)

    # Métricas ambientais absolutas
    mlflow.log_metric("greenml_energy_kwh", metrics.energy)
    mlflow.log_metric("greenml_carbon_kg", metrics.carbon)
    mlflow.log_metric("greenml_water_liters", metrics.water)

    # Parâmetros de contexto ambiental
    mlflow.log_param("greenml_carbon_intensity", tracker.carbon_intensity)
    mlflow.log_param("greenml_wue", tracker.wue)
    mlflow.log_param("greenml_energy_max_bound", bounds.energy_max)

    # O Score Final
    mlflow.log_metric("GreenML_Score", gms_value)

    return gms_value
