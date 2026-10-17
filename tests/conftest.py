"""
conftest.py — Configuração de Fixtures e Infraestrutura de Testes.

Seguindo as diretrizes do CTFL (Certified Tester Foundation Level - ISTQB) e
as melhores práticas de engenharia de testes (Padrão Arrange-Act-Assert,
Partição de Equivalência e Análise de Valor Limite):
- Fixtures determinísticas para garantir isolamento e repetibilidade (Test Isolation).
- Casos representativos de classes de equivalência válidas e valores de fronteira.
- Fixtures utilitárias para simulação de hardware/emissões (Mocks/Stubs).
"""

import importlib.util

import pytest

from green_ml_score.scoring.gms import (
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
)

# Os testes do painel (app/) dependem do extra "app" (Streamlit 1.66 ou superior, que
# exige Python 3.11). Sem ele instalado, como no Python 3.10 da CI, não são coletados.
APP_EXTRA_INSTALLED = all(
    importlib.util.find_spec(name) is not None for name in ("streamlit", "plotly")
)
collect_ignore_glob = [] if APP_EXTRA_INSTALLED else ["test_app_*.py"]

# ==============================================================================
# FIXTURES: DIMENSÃO DE DADOS AMBIENTAIS (EnvironmentalMetrics)
# ==============================================================================


@pytest.fixture
def sample_metrics_model_a() -> EnvironmentalMetrics:
    """
    Caso Típico / Válido (Partição de Equivalência):
    Modelo A representativo do TCC (Seção 7.2).
    - Energia: 100 kWh
    - Carbono: 50 kg CO2e
    - Água: 200 L
    """
    return EnvironmentalMetrics(energy=100.0, carbon=50.0, water=200.0)


@pytest.fixture
def sample_metrics_best_case() -> EnvironmentalMetrics:
    """
    Valor Limite Inferior (Boundary Value Analysis):
    Consumo nulo em todas as dimensões -> score máximo esperado (1.0 ou 100).
    """
    return EnvironmentalMetrics(energy=0.0, carbon=0.0, water=0.0)


@pytest.fixture
def sample_metrics_worst_case() -> EnvironmentalMetrics:
    """
    Valor Limite Superior (Boundary Value Analysis):
    Consumo igual aos limites máximos -> score mínimo esperado (0.0).
    """
    return EnvironmentalMetrics(energy=200.0, carbon=80.0, water=300.0)


@pytest.fixture
def sample_metrics_list() -> list[EnvironmentalMetrics]:
    """
    Conjunto heterogêneo de modelos para teste de agregações e bounds automáticos.
    """
    return [
        EnvironmentalMetrics(energy=100.0, carbon=50.0, water=200.0),
        EnvironmentalMetrics(energy=200.0, carbon=80.0, water=300.0),
        EnvironmentalMetrics(energy=150.0, carbon=60.0, water=250.0),
    ]


# ==============================================================================
# FIXTURES: LIMITES DE NORMALIZAÇÃO (NormalizationBounds)
# ==============================================================================


@pytest.fixture
def sample_bounds() -> NormalizationBounds:
    """
    Limites padrão de normalização baseados no benchmark do TCC:
    - energy_max: 200.0 kWh
    - carbon_max: 80.0 kg CO2e
    - water_max: 300.0 L
    """
    return NormalizationBounds(energy_max=200.0, carbon_max=80.0, water_max=300.0)


# ==============================================================================
# FIXTURES: PONDERAÇÃO E PESOS CONTEXTUAIS (Weights)
# ==============================================================================


@pytest.fixture
def uniform_weights() -> Weights:
    """
    Distribuição Neutra/Uniforme (Seção 6 do TCC):
    Pesos equivalentes (1/3 cada) para energia, carbono e água.
    """
    return Weights(w_E=1 / 3, w_C=1 / 3, w_W=1 / 3)


@pytest.fixture
def carbon_centric_weights() -> Weights:
    """
    Ponderação Contextual (Seção 7 do TCC):
    Cenário de matriz elétrica com alta intensidade de carbono (ex.: usinas fósseis).
    """
    return Weights(w_E=0.2, w_C=0.5, w_W=0.3)


@pytest.fixture
def water_centric_weights() -> Weights:
    """
    Ponderação Contextual (Seção 7 do TCC):
    Cenário de data center localizado em região com estresse hídrico.
    """
    return Weights(w_E=0.3, w_C=0.2, w_W=0.5)


# ==============================================================================
# FIXTURES: MOCKS DE SISTEMA DE ARQUIVOS (CodeCarbon / CSV Tracker)
# ==============================================================================


@pytest.fixture
def mock_emissions_csv_path(tmp_path):
    """
    Cria um diretório temporário isolado contendo um emissions.csv sintético
    com formato idêntico ao gerado pelo CodeCarbon.
    Garante isolamento de teste (Test Sandbox).
    """
    csv_content = (
        "timestamp,project_name,run_id,experiment_id,duration,emissions,emissions_rate,"
        "cpu_power,gpu_power,ram_power,cpu_energy,gpu_energy,ram_energy,energy_consumed,"
        "water_consumed,country_name,country_iso_code,region,cloud_provider,cloud_region,"
        "os,python_version,codecarbon_version,cpu_count,cpu_model,gpu_count,gpu_model,"
        "longitude,latitude,ram_total_size,tracking_mode,cpu_utilization_percent,"
        "gpu_utilization_percent,ram_utilization_percent,ram_used_gb,on_cloud,pue,wue\n"
        "2026-08-14T19:00:00,codecarbon,mock-run-1,mock-exp-1,10.0,0.00012,1.2e-05,"
        "35.0,0.0,20.0,0.0001,0.0,0.00005,0.0015,0.0,Brazil,BRA,são paulo,,,Windows-11,"
        "3.13.2,3.2.6,12,Mock CPU,0,,0.0,0.0,16.0,machine,50.0,0,50.0,8.0,N,1.0,0.0\n"
    )
    csv_file = tmp_path / "emissions.csv"
    csv_file.write_text(csv_content, encoding="utf-8")
    return str(tmp_path)
