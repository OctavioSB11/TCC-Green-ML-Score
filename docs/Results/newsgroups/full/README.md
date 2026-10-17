# Resultados: newsgroups (full)

Gerado por `experiments/generate_results.py` a partir de `comparative_results.csv`. Energia de treino por execução.

| Modelo              |   N |   F1 (média) |   Energia J (mediana) |   Líquida J (mediana) |   Tempo s (mediana) |   GMS (mediana) |   E/E_ref (mediana) |   J/ponto F1 (mediana) |   Dominado (fração) |   Repetições de treino (mediana) |
|:--------------------|----:|-------------:|----------------------:|----------------------:|--------------------:|----------------:|--------------------:|-----------------------:|--------------------:|---------------------------------:|
| Logistic_Regression |  10 |       0.9356 |                 0.371 |               0.09523 |             0.01489 |           99.76 |                1    |                  nan   |                 0   |                           2016   |
| Random_Forest       |  10 |       0.8944 |                34.47  |              14.75    |             1.344   |           77.46 |               99.04 |                  nan   |                 1   |                             22.5 |
| XGBoost             |  10 |       0.8691 |                72.87  |              16.28    |             3.653   |           52.36 |              218.1  |                  nan   |                 1   |                             10   |
| MLP_Neural_Network  |  10 |       0.9335 |                88.81  |              23.02    |             4.233   |           41.94 |              248    |                   87.3 |                 0.7 |                             10   |

Figuras: `energy_time`, `pareto_energy_f1`, `gms_barchart` (PNG e SVG); tabela: `summary_table.tex`. Testes de hipótese: `experiments/statistical_analysis.py`; contextos: `experiments/context_analysis.py`.
