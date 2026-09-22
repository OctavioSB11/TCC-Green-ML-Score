"""
config.py — Parâmetros e Constantes do Experimento Comparativo (Seção 5 do TCC).

Centraliza hiperparâmetros, coeficientes de intensidade de carbono,
eficiência de uso de água (WUE) e sementes aleatórias para reprodutibilidade.
"""

from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    """Configurações globais do protocolo experimental do TCC."""

    # Parametrização ambiental (Seção 5.4 do TCC)
    CARBON_INTENSITY_SAO_PAULO: float = 120.0  # gCO2e/kWh (Brasil / SP)
    CARBON_INTENSITY_US_GRID: float = 380.0  # gCO2e/kWh (EUA / US-East)
    WUE_GOOGLE_2024: float = 0.52  # L/kWh (Média Data Center Google 2024)
    WUE_INDUSTRY_AVG: float = 1.8  # L/kWh (Média global de data centers)

    # Reprodutibilidade (Seção 5.4 do TCC)
    SEEDS: list[int] = field(default_factory=lambda: [42, 123, 2024])

    # Dataset e Divisão (Seção 5.2 do TCC)
    TEST_SIZE: float = 0.2
    MAX_TFIDF_FEATURES: int = 5000

    # Datasets disponíveis
    AVAILABLE_DATASETS: list[str] = field(
        default_factory=lambda: ["newsgroups", "breast_cancer", "covtype"]
    )
    COVTYPE_N_SAMPLES: int = 50000  # Reduzido para ser treinável em tempo razoável

    # MLflow Experiment Name
    MLFLOW_EXPERIMENT_NAME: str = "GreenML_Comparative_Experiment"


# Instância padrão global para uso rápido
config = ExperimentConfig()
