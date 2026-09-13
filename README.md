<p align="center">
  <strong> GreenML Score Framework</strong>
</p>

<p align="center">
  <em>Métrica ambiental composta para avaliação da sustentabilidade em modelos de Machine Learning</em>
</p>

<p align="center">
  <a href="https://github.com/OctavioSB11/TCC-Green-ML-Score/actions/workflows/ci.yml">
    <img src="https://github.com/OctavioSB11/TCC-Green-ML-Score/actions/workflows/ci.yml/badge.svg" alt="CI Status">
  </a>
  <a href="https://github.com/OctavioSB11/TCC-Green-ML-Score/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT">
  </a>
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg" alt="Python Versions">
  <img src="https://img.shields.io/badge/version-0.1.0-green.svg" alt="Version">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
  <img src="https://img.shields.io/badge/linting-ruff-orange.svg" alt="Linting: ruff">
</p>

---

## Sobre o Projeto

O **GreenML Score** é um framework Python profissional e automatizado para **medir, rastrear e reportar o impacto ambiental de modelos de Machine Learning**.

Enquanto a maioria das ferramentas de ML foca exclusivamente em métricas preditivas como Acurácia e F1-Score (*Red AI*), o GreenML traz a **sustentabilidade para o centro da tomada de decisão** (*Green AI*), combinando monitoramento de hardware em tempo real com uma métrica composta rigorosa — o **GreenML Score (GMS)**.

### O que ele mede?

| Dimensão | Unidade | Fonte |
|---|---|---|
| **Consumo Energético** | kWh | [CodeCarbon](https://github.com/mlco2/codecarbon) (RAPL / NVML) |
| **Emissões de Carbono** | kg CO₂e | `C = E × IC_região` |
| **Pegada Hídrica** | Litros | `W = E × WUE` | ---

## A Métrica: GreenML Score (GMS)

O GMS é uma métrica composta que pertence ao intervalo **[0, 1]** (ou **[0, 100]** na escala operacional). Valores maiores representam modelos **mais sustentáveis e eficientes**.

### Fórmula Matemática

```
GMS = w_E · Ê + w_C · Ĉ + w_W · Ŵ
```

Onde cada componente normalizado usa **normalização inversa**:

```
X̂ = 1 − (X / X_max)
```

| Símbolo | Descrição | Padrão |
|---|---|---|
| `w_E` | Peso da dimensão energética | 1/3 |
| `w_C` | Peso da dimensão de carbono | 1/3 |
| `w_W` | Peso da dimensão hídrica | 1/3 |
| `X_max` | Maior valor observado no conjunto de modelos comparados | Auto | > **Interpretação:** Quanto menor o consumo de recursos (energia, carbono, água), maior o GMS. Um GMS de 100 indica o modelo mais eficiente do grupo; um GMS próximo de 0 indica o mais custoso.

### Pesos Contextuais (Seção 7 do TCC)

Os pesos podem ser ajustados conforme o contexto operacional:

| Cenário | `w_E` | `w_C` | `w_W` | Justificativa |
|---|:---:|:---:|:---:|---|
| Neutro (padrão) | 1/3 | 1/3 | 1/3 | Sem viés dimensional |
| Alta intensidade de carbono | 0.2 | 0.5 | 0.3 | Regiões com grid elétrico fóssil |
| Estresse hídrico | 0.3 | 0.2 | 0.5 | Data centers em regiões áridas | ---

## Arquitetura

O framework é organizado em **4 camadas** independentes e desacopladas:

```mermaid
graph TB
    subgraph "Camada 1 — Collectors"
        A[" CodeCarbon Adapter<br/><i>Instrumentação de Hardware</i>"]
    end

    subgraph "Camada 2 — Estimators"
        B[" Carbon Estimator<br/><i>E × IC_região → kg CO₂e</i>"]
        C[" Water Estimator<br/><i>E × WUE → Litros</i>"]
    end

    subgraph "Camada 3 — Scoring"
        D[" GMS Calculator<br/><i>Normalização Inversa + Pesos</i>"]
    end

    subgraph "Camada 4 — Integrations"
        E[" MLflow Logger"]
        F[" Sklearn Wrapper"]
    end

    A -->|"energia kWh"| B
    A -->|"energia kWh"| C
    B -->|"carbono"| D
    C -->|"água"| D
    A -->|"energia"| D
    D -->|"GMS"| E
    D -->|"GMS"| F
    F -->|"auto-tracking"| A

    style A fill:#2d6a4f,stroke:#1b4332,color:#fff
    style B fill:#52796f,stroke:#354f52,color:#fff
    style C fill:#52796f,stroke:#354f52,color:#fff
    style D fill:#84a98c,stroke:#52796f,color:#fff
    style E fill:#cad2c5,stroke:#84a98c,color:#333
    style F fill:#cad2c5,stroke:#84a98c,color:#333
```

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/OctavioSB11/TCC-Green-ML-Score.git
cd TCC-Green-ML-Score

# Instale em modo editável com dependências de desenvolvimento
pip install -e .[dev]
```

### Dependências Opcionais

```bash
# Para executar os experimentos comparativos (XGBoost, datasets HuggingFace, etc.)
pip install -e .[experiments]
```

---

## Como Usar

### Integração com Scikit-Learn (Fricção Zero)

O framework foi projetado para exigir **mínima alteração** no seu código existente:

```python
import mlflow
from sklearn.ensemble import RandomForestClassifier
from green_ml_score.integrations.sklearn import GreenMLSklearnWrapper
from green_ml_score.scoring import NormalizationBounds

# 1. Defina seus limites máximos teóricos (para a normalização do GMS)
bounds = NormalizationBounds(energy_max=1.5, carbon_max=0.2, water_max=2.7)

# 2. Inicialize o MLflow
mlflow.set_experiment("GreenML_Demonstration")

with mlflow.start_run():
    # 3. Envolva seu modelo com o Wrapper
    base_model = RandomForestClassifier()
    green_model = GreenMLSklearnWrapper(
        base_model,
        bounds=bounds,
        tracker_kwargs={
            "carbon_intensity_g_per_kwh": 120,  # São Paulo, Brasil
            "wue_liters_per_kwh": 0.52,         # Google 2024
        },
    )

    # 4. Ao chamar .fit(), o Tracker liga automaticamente em background!
    green_model.fit(X_train, y_train)
    # → Métricas ambientais logadas automaticamente no MLflow 
```

### Uso Direto da API de Scoring

```python
from green_ml_score import (
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
    calculate_gms,
    explain_gms,
)

# Métricas coletadas de um modelo treinado
metrics = EnvironmentalMetrics(energy=0.05, carbon=0.006, water=0.026)
bounds = NormalizationBounds(energy_max=0.1, carbon_max=0.012, water_max=0.052)

# GMS com pesos uniformes
score = calculate_gms(metrics, bounds, scale_100=True)
print(f"GreenML Score: {score:.2f} / 100")

# Decomposição por dimensão
decomposition = explain_gms(metrics, bounds)
print(decomposition)
# {'E_norm': 0.5, 'C_norm': 0.5, 'W_norm': 0.5, 'GMS': 0.5, ...}
```

---

## Resultados Experimentais

Experimento comparativo com **4 modelos** no dataset **IMDb Reviews** (25k amostras de análise de sentimento), cada um executado com **3 sementes aleatórias** (42, 123, 2024):

| Ranking | Modelo | Acurácia | Tempo (s) | Energia (kWh) | GMS (0–100) |
|:---:|---|:---:|:---:|:---:|:---:|
| 1º | **Regressão Logística** | 0.9268 | 2.42 | 0.000010 | **92.70 ± 2.14** |
| 2º | **Random Forest** | 0.8788 | 2.95 | 0.000023 | **82.29 ± 7.28** |
| 3º | **Rede Neural (MLP)** | 0.9175 | 5.78 | 0.000042 | **68.22 ± 5.34** |
| 4º | **XGBoost** | 0.8611 | 6.48 | 0.000102 | **21.83 ± 20.58** | >  Gráficos completos (PNG 300 DPI e SVG vetorial), tabela LaTeX e análise detalhada disponíveis em [`docs/Results/`](docs/Results/).

### Principais Conclusões

1. **Eficiência Clássica Confirmada:** A Regressão Logística atingiu a maior acurácia (92.68%) gastando 10× menos energia, liderando o GMS com folga.
2. **Trade-off Red AI vs Green AI:** XGBoost e MLP consumiram ordens de magnitude a mais sem ganho proporcional de acurácia.
3. **Fronteira de Pareto:** O GMS oferece uma régua objetiva para balancear performance preditiva × custo ecológico.

---

## Visualizando Resultados no MLflow

```bash
mlflow ui
```

Abra o navegador em `http://127.0.0.1:5000` para visualizar todas as métricas ambientais e o GMS registrados automaticamente.

---

## Testes

O framework possui **32 testes unitários** cobrindo todas as camadas da arquitetura:

```bash
# Rodar todos os testes
pytest

# Rodar com relatório de cobertura
pytest --cov=green_ml_score --cov-report=term-missing
```

---

## Estrutura do Projeto

```
TCC-Green-ML-Score/
├── green_ml_score/            # Código-fonte do framework
│   ├── collectors/            # Camada 1: Adaptadores de instrumentação (CodeCarbon)
│   ├── estimators/            # Camada 2: Carbono (E×IC) e Água (E×WUE)
│   ├── scoring/               # Camada 3: Cálculo do GMS, normalização, pesos
│   └── integrations/          # Camada 4: MLflow logger, Sklearn wrapper
├── experiments/               # Experimento comparativo e geração de resultados
│   ├── comparative_experiment.py
│   ├── generate_results.py
│   ├── config.py
│   └── results/               # Dados brutos do experimento
├── tests/                     # 32 testes unitários (pytest)
├── docs/
│   ├── Diagrams/              # Diagramas de arquitetura (.drawio)
│   └── Results/               # Gráficos e tabelas gerados
├── .github/workflows/ci.yml   # CI: Ruff + Black + Pytest (Python 3.10–3.13)
├── pyproject.toml             # Configuração do projeto e dependências
├── CHANGELOG.md               # Histórico de versões
├── CONTRIBUTING.md            # Guia para contribuidores
├── LICENSE                    # MIT License
└── README.md                  # Este arquivo
```

---

## Citação (BibTeX)

Se este framework ou o artigo associado foi útil para a sua pesquisa, por favor cite:

```bibtex
@software{greenml_score_2026,
  title     = {GreenML Score: Framework para Avaliação e Rastreamento do Impacto Ambiental em Modelos de Machine Learning},
  author    = {Bordotti, Octavio and Parolin, Danilo},
  year      = {2026},
  url       = {https://github.com/OctavioSB11/TCC-Green-ML-Score},
  version   = {0.1.0},
  license   = {MIT}
}
```

---

## Contribuindo

Contribuições são bem-vindas! Consulte o guia completo em [`CONTRIBUTING.md`](CONTRIBUTING.md).

```bash
# Resumo rápido
git clone https://github.com/OctavioSB11/TCC-Green-ML-Score.git
cd TCC-Green-ML-Score
pip install -e .[dev]
ruff check .          # Linting
black .               # Formatação
pytest                # Testes
```

---

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## Autores

- **Octavio Bordotti** — [GitHub](https://github.com/OctavioSB11)
- **Danilo Parolin**

**Trabalho de Conclusão de Curso (TCC)** — 2026
