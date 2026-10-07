"""
Integração do GreenML Score com MLflow.
"""

from __future__ import annotations

import mlflow

from green_ml_score.collectors.codecarbon import GreenMLTracker, MeasurementDetails
from green_ml_score.scoring.gms import NormalizationBounds, Weights, calculate_gms


def log_greenml_run(
    tracker: GreenMLTracker,
    bounds: NormalizationBounds | None = None,
    weights: Weights | None = None,
) -> float | None:
    """
    Registra no MLflow as métricas ambientais absolutas e, se houver limites
    de normalização conhecidos, o GMS.

    O GMS só é registrado quando ``bounds`` é informado: sem limites definidos
    sobre o conjunto de comparação, qualquer score seria arbitrário.

    Returns:
        O GMS (escala 0–100) ou None quando ``bounds`` não foi informado.
    """
    metrics = tracker.get_metrics()

    mlflow.log_metric("greenml_energy_kwh", metrics.energy)
    mlflow.log_metric("greenml_carbon_kg", metrics.carbon)
    mlflow.log_metric("greenml_water_liters", metrics.water)
    mlflow.log_param("greenml_carbon_intensity", tracker.carbon_intensity)
    mlflow.log_param("greenml_wue", tracker.wue)

    details = getattr(tracker, "details", None)
    if isinstance(details, MeasurementDetails):
        if details.tracking_mode is not None:
            mlflow.log_param("greenml_tracking_mode", details.tracking_mode)
        if details.ram_share is not None:
            mlflow.log_metric("greenml_ram_energy_share", details.ram_share)

    if bounds is None:
        return None

    gms_value = calculate_gms(metrics, bounds, weights or Weights(), scale_100=True)
    mlflow.log_param("greenml_energy_max_bound", bounds.energy_max)
    mlflow.log_metric("GreenML_Score", gms_value)
    return gms_value
