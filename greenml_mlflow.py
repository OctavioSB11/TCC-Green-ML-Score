"""
Integração do GreenML Score com MLflow
"""

def log_gms(metrics, gms_value):
    """
    Loga métricas ambientais + GMS no MLflow
    """

    try:
        import mlflow

        mlflow.log_metric("energy_kwh", metrics.energy)
        mlflow.log_metric("carbon_kg", metrics.carbon)
        mlflow.log_metric("water_liters", metrics.water)
        mlflow.log_metric("GMS", gms_value)

    except ImportError:
        raise ImportError("MLflow não está instalado. Use: pip install mlflow")


def log_full_experiment(metrics, bounds, weights, gms_value):
    """
    Log completo (útil para experimentos mais robustos)
    """

    import mlflow

    # Métricas ambientais
    mlflow.log_metric("energy_kwh", metrics.energy)
    mlflow.log_metric("carbon_kg", metrics.carbon)
    mlflow.log_metric("water_liters", metrics.water)

    # Normalização bounds
    mlflow.log_param("energy_max", bounds.energy_max)
    mlflow.log_param("carbon_max", bounds.carbon_max)
    mlflow.log_param("water_max", bounds.water_max)

    # Pesos
    mlflow.log_param("w_E", weights.w_E)
    mlflow.log_param("w_C", weights.w_C)
    mlflow.log_param("w_W", weights.w_W)

    # Resultado final
    mlflow.log_metric("GMS", gms_value)