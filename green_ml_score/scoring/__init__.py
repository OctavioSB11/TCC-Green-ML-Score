# Camada (c) scoring — cálculo do GMS, normalização e pesos contextuais (Seção 3.4 do TCC)
from green_ml_score.scoring.gms import (
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
    calculate_gms,
    explain_gms,
)
from green_ml_score.scoring.relative import (
    RelativeScore,
    pareto_dominated,
    relative_to_reference,
)

__all__ = [
    "EnvironmentalMetrics",
    "NormalizationBounds",
    "RelativeScore",
    "Weights",
    "calculate_gms",
    "explain_gms",
    "pareto_dominated",
    "relative_to_reference",
]
