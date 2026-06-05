"""
GreenML Score — métrica ambiental para avaliação de modelos de Machine Learning.

A biblioteca é organizada nas quatro camadas descritas na Seção 3.4 do TCC:
    - collectors  : adaptadores de instrumentação (CodeCarbon)
    - estimators  : conversões energia→carbono e energia→água
    - scoring     : cálculo do GMS, normalização e pesos contextuais
    - integrations: conectores para MLflow e callbacks de frameworks

O núcleo de scoring (puro, sem dependências de I/O) é reexportado aqui.
As camadas collectors/integrations devem ser importadas a partir de seus
subpacotes, pois dependem de bibliotecas pesadas (codecarbon, mlflow).
"""
from green_ml_score.scoring import (
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
    calculate_gms,
    explain_gms,
)
from green_ml_score.estimators import (
    calculate_water_usage,
    calculate_carbon_emissions,
)

__all__ = [
    "EnvironmentalMetrics",
    "NormalizationBounds",
    "Weights",
    "calculate_gms",
    "explain_gms",
    "calculate_water_usage",
    "calculate_carbon_emissions",
]
