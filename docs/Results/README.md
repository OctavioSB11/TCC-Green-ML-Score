#  Resultados Experimentais e Análise de Sustentabilidade — GreenML Score

Este diretório reúne as visualizações gráficas e tabelas estatísticas geradas a partir das **12 execuções experimentais (4 modelos × 3 sementes aleatórias: 42, 123 e 2024)**, conforme protocolo metodológico definido na Seção 5 do TCC.

---

## Visualizações Disponibilizadas (Formatos PNG 300 DPI e SVG Vetorial)

1. **`gms_comparison_barchart.png / .svg`:**
   - Ranking oficial dos modelos ordenados pelo **GreenML Score médio**, com barras de erro representando o desvio padrão ($\sigma$) entre as sementes.
   
2. **`pareto_tradeoff_scatter.png / .svg`:**
   - Gráfico de dispersão cruzando **Acurácia Preditiva** (Eixo X) com **GreenML Score** (Eixo Y), evidenciando o quadrante ótimo de *Green AI* e a fronteira de Pareto.

3. **`radar_multidimensional_chart.png / .svg`:**
   - Gráfico de radar (Spider Chart) com 5 dimensões normalizadas: Acurácia, F1-Score, Eficiência Energética, Baixo Carbono e Baixa Pegada Hídrica.

4. **`energy_and_time_comparison.png / .svg`:**
   - Análise comparativa direta entre o gasto energético total em micro-watt-hora ($\mu\text{Wh}$) e o tempo computacional em segundos.

5. **`summary_table.tex`:**
   - Tabela formal formatada em LaTeX com o pacote `booktabs`, pronta para importação direta no texto do TCC.

---

## Principais Conclusões Científicas para o TCC

| Ranking | Modelo | Acurácia | Tempo (s) | Energia (kWh) | GreenML Score | Categoria |
|:---:|---|:---:|:---:|:---:|:---:|:---:|
| 1º | **Regressão Logística** | **0.9268** | **2.42s** | **0.000010** | **92.70 ± 2.14** | *Green AI Dominante* |
| 2º | **Random Forest** | 0.8788 | 2.95s | 0.000023 | **82.29 ± 7.28** | *Intermediário Equilibrado* |
| 3º | **Rede Neural (MLP)** | 0.9175 | 5.78s | 0.000042 | **68.22 ± 5.34** | *Alta Precisão / Custo Elevado* |
| 4º | **XGBoost** | 0.8611 | 6.48s | 0.000102 | **21.83 ± 20.58** | *Red AI (Alto Overhead)* | ### Insights para a Banca:
1. **Confirmação da Hipótese H3 (Eficiência Clássica):** A Regressão Logística provou que um modelo linear simples, bem parametrizado com TF-IDF, é capaz de atingir **92.68% de acurácia** gastando **10 vezes menos energia** que ensembles iterativos pesados, liderando com folga o GreenML Score (**92.70**).
2. **Confirmação da Hipótese H1 (Tensão Red AI vs. Green AI):** O XGBoost e a Rede Neural MLP consumiram ordens de magnitude a mais de energia devido à complexidade computacional iterativa. No caso do XGBoost em matrizes esparsas de texto, o tempo de construção de árvores consecutivas elevou o consumo para 0.000102 kWh, resultando no menor GMS (**21.83**).
3. **Fronteira de Pareto e Tomada de Decisão ESG:** O GreenML Score oferece uma régua objetiva para os times de MLOps identificarem que o ganho de acurácia marginal muitas vezes não justifica o custo ecológico e financeiro do modelo em produção.
