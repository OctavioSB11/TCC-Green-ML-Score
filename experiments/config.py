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
    # IC média do Brasil em 2024 (Ember, Yearly electricity data, "CO2 intensity"),
    # mesma fonte do contexts.csv; o BR-local usa o ano de 2025 (109,95).
    CARBON_INTENSITY_BR_2024: float = 106.06  # gCO2/kWh
    CARBON_INTENSITY_US_GRID: float = 380.0  # gCO2e/kWh
    # WUE global da Microsoft no ano fiscal de 2024 (julho/2023 a junho/2024),
    # "Measuring energy and water efficiency for Microsoft datacenters".
    WUE_MICROSOFT_FY24: float = 0.30  # L/kWh
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

    # Janela mínima de medição: cada fase é repetida (além do mínimo acima) até
    # ocupar ao menos este tempo. Sessões curtas são dominadas pelo overhead fixo
    # do CodeCarbon (≈ 1,5 s por sessão) e por sua leitura esparsa de potência; no
    # quick-run de 14/10, fases de 1,5–2 s produziram energia líquida negativa.
    MIN_MEASUREMENT_WINDOW_S: float = 30.0
    QUICK_RUN_MIN_WINDOW_S: float = 5.0

    # Baseline de repouso: no início de cada dataset, mede-se a máquina sem carga
    # para obter a potência ociosa P₀ e reportar a energia líquida E − P₀·t.
    IDLE_BASELINE_S: float = 60.0
    QUICK_RUN_IDLE_BASELINE_S: float = 10.0

    # Aquecimento: uma execução (treino + inferência) descartada por modelo, antes
    # da primeira semente, para estabilizar caches, JIT e frequência da CPU.
    WARMUP: bool = True

    # Modelo de referência para o score relativo (razão de energia e custo marginal).
    REFERENCE_MODEL: str = "Logistic_Regression"

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
