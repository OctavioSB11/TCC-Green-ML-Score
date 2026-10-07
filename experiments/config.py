"""
config.py — Parâmetros e constantes do experimento comparativo (Seção 5 do TCC).

Centraliza sementes, carga de trabalho, paralelismo e fatores ambientais.
"""

from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    """Configurações globais do protocolo experimental do TCC."""

    # Fatores ambientais do ambiente de medição (Seção 5.4).
    # Os cenários regionais (EUA, Alemanha etc.) serão tratados pelo módulo de
    # contextos de execução (modelo × região × horário), e não aqui.
    CARBON_INTENSITY_SAO_PAULO: float = 120.0  # gCO2e/kWh
    CARBON_INTENSITY_US_GRID: float = 380.0  # gCO2e/kWh
    WUE_GOOGLE_2024: float = 0.52  # L/kWh
    WUE_INDUSTRY_AVG: float = 1.8  # L/kWh

    # Reprodutibilidade: cada semente define a divisão treino/teste E a
    # inicialização dos modelos, de modo que a variância reportada inclua a
    # variabilidade dos dados, e não apenas o ruído da medição.
    SEEDS: list[int] = field(
        default_factory=lambda: [42, 123, 2024, 7, 314, 1001, 2718, 4242, 8080, 9999]
    )

    # Semente FIXA para a subamostragem do dataset (covtype e quick-run):
    # garante que todas as sementes partam do mesmo conjunto de dados.
    DATA_SAMPLE_SEED: int = 42

    # Carga de trabalho: cada fase (treino, inferência) é repetida N vezes com
    # o MESMO estimador clonado; reporta-se a energia por repetição. A repetição
    # serve apenas para elevar a energia acumulada acima do ruído de medição.
    WORKLOAD_REPETITIONS: int = 10
    QUICK_RUN_REPETITIONS: int = 1

    # Paralelismo idêntico para TODOS os modelos (estimadores e BLAS/OpenMP).
    # Diferenças de n_jobs entre modelos confundiriam a comparação de energia.
    N_JOBS: int = 1

    # Dataset e divisão (Seção 5.2)
    TEST_SIZE: float = 0.2
    MAX_TFIDF_FEATURES: int = 5000
    QUICK_RUN_SAMPLES: int = 500
    NEWSGROUPS_CATEGORIES: list[str] = field(
        default_factory=lambda: ["rec.autos", "sci.med"]
    )
    AVAILABLE_DATASETS: list[str] = field(
        default_factory=lambda: ["newsgroups", "breast_cancer", "covtype"]
    )
    COVTYPE_N_SAMPLES: int = 50000

    # Saídas
    RESULTS_DIR: str = "experiments/results"
    MLFLOW_EXPERIMENT_NAME: str = "GreenML_Comparative_Experiment"


config = ExperimentConfig()
