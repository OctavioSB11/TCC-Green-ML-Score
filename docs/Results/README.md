# Resultados Experimentais — GreenML Score

Este diretório reúne as **visualizações gráficas** e **tabelas estatísticas** geradas a partir das 12 execuções experimentais (4 modelos × 3 sementes aleatórias: 42, 123 e 2024), conforme protocolo metodológico definido na Seção 5 do TCC.

---

## Protocolo Experimental

| Parâmetro | Valor |
|---|---|
| **Dataset** | IMDb Movie Reviews (25.000 amostras) |
| **Tarefa** | Classificação binária de sentimento (positivo/negativo) |
| **Pré-processamento** | TF-IDF com max_features=10.000 |
| **Split** | 80% treino / 20% teste |
| **Sementes** | 42, 123, 2024 |
| **IC regional** | 120 gCO₂e/kWh (São Paulo, Brasil) |
| **WUE** | 0.52 L/kWh (Google 2024) |
| **Pesos do GMS** | Uniformes (w_E = w_C = w_W = 1/3) | ---

## Visualizações Geradas

Todos os gráficos estão disponíveis em **PNG (300 DPI)** para uso em documentos e **SVG vetorial** para escalonamento sem perda.

### 1. Ranking GMS — Gráfico de Barras

**Arquivo:** `gms_comparison_barchart.png` / `.svg`

Ranking oficial dos modelos ordenados pelo **GreenML Score médio**, com barras de erro representando o desvio padrão (σ) entre as sementes aleatórias.

### 2. Trade-off de Pareto — Gráfico de Dispersão

**Arquivo:** `pareto_tradeoff_scatter.png` / `.svg`

Gráfico de dispersão cruzando **Acurácia Preditiva** (eixo X) com **GreenML Score** (eixo Y), evidenciando o quadrante ótimo de *Green AI* e a fronteira de Pareto. Modelos no quadrante superior direito representam o equilíbrio ideal entre performance e sustentabilidade.

### 3. Perfil Multidimensional — Radar Chart

**Arquivo:** `radar_multidimensional_chart.png` / `.svg`

Gráfico de radar (Spider Chart) com 5 dimensões normalizadas:
- Acurácia
- F1-Score
- Eficiência Energética
- Baixo Carbono
- Baixa Pegada Hídrica

### 4. Consumo de Energia e Tempo — Comparativo

**Arquivo:** `energy_and_time_comparison.png` / `.svg`

Análise comparativa direta entre o gasto energético total em micro-watt-hora (μWh) e o tempo computacional em segundos.

### 5. Tabela LaTeX

**Arquivo:** `summary_table.tex`

Tabela formal formatada em LaTeX com o pacote `booktabs`, pronta para importação direta no texto do TCC via `\input{summary_table.tex}`.

---

## Resultados Consolidados

| Ranking | Modelo | Acurácia | Tempo (s) | Energia (kWh) | GreenML Score | Categoria |
|:---:|---|:---:|:---:|:---:|:---:|:---:|
| 1º | **Regressão Logística** | 0.9268 | 2.42s | 0.000010 | **92.70 ± 2.14** | *Green AI Dominante* |
| 2º | **Random Forest** | 0.8788 | 2.95s | 0.000023 | **82.29 ± 7.28** | *Intermediário Equilibrado* |
| 3º | **Rede Neural (MLP)** | 0.9175 | 5.78s | 0.000042 | **68.22 ± 5.34** | *Alta Precisão / Custo Elevado* |
| 4º | **XGBoost** | 0.8611 | 6.48s | 0.000102 | **21.83 ± 20.58** | *Red AI (Alto Overhead)* | ---

## Análise e Conclusões Científicas

### Hipótese H3 — Eficiência de Modelos Clássicos (Confirmada )

A Regressão Logística provou que um modelo linear simples, bem parametrizado com TF-IDF, é capaz de atingir **92.68% de acurácia** gastando **10× menos energia** que ensembles iterativos pesados, liderando com folga o GreenML Score (**92.70**).

### Hipótese H1 — Tensão Red AI vs. Green AI (Confirmada )

O XGBoost e a Rede Neural MLP consumiram ordens de magnitude a mais de energia devido à complexidade computacional iterativa. No caso do XGBoost em matrizes esparsas de texto, o tempo de construção de árvores consecutivas elevou o consumo para 0.000102 kWh, resultando no menor GMS (**21.83**).

### Fronteira de Pareto e Tomada de Decisão ESG

O GreenML Score oferece uma **régua objetiva** para times de MLOps identificarem que o ganho de acurácia marginal muitas vezes **não justifica o custo ecológico e financeiro** do modelo em produção. A Regressão Logística domina a fronteira de Pareto, sendo simultaneamente a mais precisa e a mais sustentável.

---

## Reprodução dos Resultados

```bash
# 1. Executar o experimento comparativo
python -m experiments.comparative_experiment

# 2. Gerar visualizações e tabelas
python -m experiments.generate_results
```

Os dados brutos ficam em `experiments/results/` e os gráficos são salvos neste diretório (`docs/Results/`).
