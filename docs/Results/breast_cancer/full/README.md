# Resultados: breast_cancer (full)

Gerado por `experiments/generate_results.py` a partir de `comparative_results.csv`. Energia de treino por execução.

| Modelo              |   N |   F1 (média) |   Energia J (mediana) |   Líquida J (mediana) |   Tempo s (mediana) |   GMS (mediana) |   E/E_ref (mediana) |   J/ponto F1 (mediana) |   Dominado (fração) |   Repetições de treino (mediana) |
|:--------------------|----:|-------------:|----------------------:|----------------------:|--------------------:|----------------:|--------------------:|-----------------------:|--------------------:|---------------------------------:|
| Logistic_Regression |  10 |       0.9698 |                0.0645 |              0.001721 |            0.003896 |           98.75 |                1    |               nan      |                 0   |                           7702   |
| MLP_Neural_Network  |  10 |       0.9225 |                1.104  |              0.2903   |            0.05175  |           78.62 |               16.18 |               nan      |                 1   |                            580.5 |
| XGBoost             |  10 |       0.9605 |                2.778  |              0.7016   |            0.1363   |           46.19 |               50.85 |                 1.169  |                 0.8 |                            220.5 |
| Random_Forest       |  10 |       0.9556 |                3.143  |              0.7723   |            0.15     |           39.12 |               52.35 |                 0.9414 |                 0.9 |                            200.5 |

Figuras: `energy_time`, `pareto_energy_f1`, `gms_barchart` (PNG e SVG); tabela: `summary_table.tex`. Testes de hipótese: `experiments/statistical_analysis.py`; contextos: `experiments/context_analysis.py`.
