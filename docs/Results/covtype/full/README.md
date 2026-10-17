# Resultados — covtype (full)

Gerado por `experiments/generate_results.py` a partir de `comparative_results.csv`. Energia de treino por execução.

| Modelo              |   N |   F1 (média) |   Energia J (mediana) |   Líquida J (mediana) |   Tempo s (mediana) |   GMS (mediana) |   E/E_ref (mediana) |   J/ponto F1 (mediana) |   Dominado (fração) |   Repetições de treino (mediana) |
|:--------------------|----:|-------------:|----------------------:|----------------------:|--------------------:|----------------:|--------------------:|-----------------------:|--------------------:|---------------------------------:|
| Logistic_Regression |  10 |       0.7586 |                 3.795 |                0.9168 |              0.1625 |           99.18 |               1     |                nan     |                   0 |                              185 |
| XGBoost             |  10 |       0.8624 |                20.85  |                2.95   |              0.9907 |           95.52 |               5.136 |                  1.644 |                   0 |                               32 |
| Random_Forest       |  10 |       0.8934 |               131.7   |                3.65   |              7.437  |           71.71 |              35.91  |                  9.32  |                   0 |                               10 |
| MLP_Neural_Network  |  10 |       0.8506 |               328.2   |               24.19   |             17.3    |           29.47 |              77.91  |                 34     |                   1 |                               10 |

Figuras: `energy_time`, `pareto_energy_f1`, `gms_barchart` (PNG e SVG); tabela: `summary_table.tex`. Testes de hipótese: `experiments/statistical_analysis.py`; contextos: `experiments/context_analysis.py`.
