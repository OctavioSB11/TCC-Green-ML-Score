# Experimento Comparativo — GreenML Score (Seção 5 do TCC)

Este repositório contém a infraestrutura e o protocolo experimental para avaliação empírica do **GreenML Score (GMS)** comparando modelos de Machine Learning clássicos (*Green AI*) e redes profundas (*Red AI*).

---

## Hipóteses de Trabalho (Seção 5.6 do TCC)

* **H1 (Tensão Red AI vs Green AI):** Modelos de maior complexidade computacional (ex.: Rede Neural MLP e XGBoost) atingem acurácia competitiva, porém registram o menor **GreenML Score (GMS)** sob pesos uniformes, devido ao custo energético elevado de treinamento iterativo.
* **H2 (Fronteira de Pareto):** Modelos de complexidade intermediária (ex.: XGBoost) posicionam-se na fronteira de Pareto entre acurácia preditiva e sustentabilidade ambiental, representando o trade-off entre performance e eficiência energética.
* **H3 (Eficiência Clássica):** Modelos lineares e ensembles clássicos (ex.: Regressão Logística, Random Forest) apresentam os maiores valores de **GMS**, consolidando-se como alternativas ecológicas viáveis em cenários de restrição energética.

---

## Protocolo Experimental (Seção 5.4 do TCC)

| Parâmetro | Valor Padrão | Descrição |
|---|---|---|
| **Intensidade de Carbono (IC)** | `120.0 gCO2e/kWh` | Matriz regional de São Paulo (IEA 2024) |
| **Fator Hídrico (WUE)** | `0.52 L/kWh` | Eficiência de uso de água em Data Centers (Google 2024) |
| **Sementes Aleatórias (Seeds)** | `[42, 123, 2024]` | Múltiplas execuções para média e desvio padrão |
| **Normalização** | `Global Bounds` | `NormalizationBounds.from_metrics_list()` sobre todos os modelos |
| **Pesos Padrão** | `w_E = w_C = w_W = 1/3` | Distribuição uniforme neutra | ---

## Como Executar

### 1. Teste Rápido (Quick Run)
Executa em poucos segundos usando um subset do dataset de benchmark para validação ágil da pipeline:

```bash
python experiments/comparative_experiment.py --quick-run
```

### 2. Execução com Modelos Clássicos
Avalia modelos Scikit-Learn (Regressão Logística e Random Forest) nas sementes padrão:

```bash
python experiments/comparative_experiment.py --models sklearn
```

### 3. Execução Completa (All Models)
Avalia todas as famílias de modelos (incluindo XGBoost):

```bash
python experiments/comparative_experiment.py --models all --seeds 42 123 2024
```

---

## Visualização no MLflow

Após a execução, inicie a interface do MLflow para visualizar a dashboard comparativa e gráficos nativos:

```bash
mlflow ui
```

Abra o navegador em `http://127.0.0.1:5000` para visualizar os experimentos e métricas registradas.
