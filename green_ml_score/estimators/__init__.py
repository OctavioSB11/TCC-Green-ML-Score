# Camada (b) estimators — conversões energia→carbono e energia→água (Seção 3.4 do TCC)
from green_ml_score.estimators.carbon import calculate_carbon_emissions
from green_ml_score.estimators.water import calculate_water_usage

__all__ = ["calculate_carbon_emissions", "calculate_water_usage"]
