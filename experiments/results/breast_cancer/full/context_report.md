# Avaliação modelo × contexto de execução

Contextos: `experiments/contexts/contexts.csv` · modelos: 4 · contextos: 7 · configurações: 28

## Concordância com o critério só-energia

- τ_b de Kendall (GMS com pesos 1/3 × energia): 0.7859
- τ_b no simplex de pesos: mín 0.5759, mediana 0.7799, máx 1.0000
- Modelo de menor energia: Logistic_Regression
- Fração do simplex em que o melhor GMS usa outro modelo: 0.0%

Observação: o critério só-energia não distingue contextos (a energia de TI não depende da região); empates de energia entre contextos de um mesmo modelo são tratados pelo τ_b.

## Configurações (pesos 1/3)

| model               | context       | region        | hour   |   energy_kwh |   carbon_kg |   water_l |     gms |   rank_gms |   rank_energy |
|:--------------------|:--------------|:--------------|:-------|-------------:|------------:|----------:|--------:|-----------:|--------------:|
| Logistic_Regression | FR-local      | FR-local      |        |      2e-08   |     0       | 7e-08     | 99.1556 |          1 |             1 |
| Logistic_Regression | AWS-Stockholm | AWS-Stockholm |        |      2e-08   |     0       | 1.2e-07   | 99.0651 |          2 |             1 |
| Logistic_Regression | AWS-Frankfurt | AWS-Frankfurt |        |      2e-08   |     1e-08   | 5e-08     | 98.8165 |          3 |             1 |
| Logistic_Regression | AWS-Virginia  | AWS-Virginia  |        |      2e-08   |     1e-08   | 5e-08     | 98.8075 |          4 |             1 |
| Logistic_Regression | BR-local      | BR-local      |        |      2e-08   |     0       | 3.3e-07   | 98.6063 |          5 |             1 |
| Logistic_Regression | IN-local      | IN-local      |        |      2e-08   |     1e-08   | 6e-08     | 98.5211 |          6 |             1 |
| Logistic_Regression | AWS-SaoPaulo  | AWS-SaoPaulo  |        |      2e-08   |     0       | 3.8e-07   | 98.504  |          7 |             1 |
| MLP_Neural_Network  | FR-local      | FR-local      |        |      3.1e-07 |     1e-08   | 1.13e-06  | 85.5521 |          8 |             8 |
| MLP_Neural_Network  | AWS-Stockholm | AWS-Stockholm |        |      3.1e-07 |     1e-08   | 2.02e-06  | 84.0031 |          9 |             8 |
| MLP_Neural_Network  | AWS-Frankfurt | AWS-Frankfurt |        |      3.1e-07 |     1.3e-07 | 7.9e-07   | 79.7499 |         10 |             8 |
| MLP_Neural_Network  | AWS-Virginia  | AWS-Virginia  |        |      3.1e-07 |     1.3e-07 | 8.6e-07   | 79.5957 |         11 |             8 |
| MLP_Neural_Network  | BR-local      | BR-local      |        |      3.1e-07 |     3e-08   | 5.7e-06   | 76.1524 |         12 |             8 |
| MLP_Neural_Network  | IN-local      | IN-local      |        |      3.1e-07 |     2.1e-07 | 1.06e-06  | 74.6959 |         13 |             8 |
| MLP_Neural_Network  | AWS-SaoPaulo  | AWS-SaoPaulo  |        |      3.1e-07 |     4e-08   | 6.52e-06  | 74.4028 |         14 |             8 |
| XGBoost             | FR-local      | FR-local      |        |      7.7e-07 |     3e-08   | 2.83e-06  | 63.6353 |         15 |            15 |
| XGBoost             | AWS-Stockholm | AWS-Stockholm |        |      7.7e-07 |     3e-08   | 5.08e-06  | 59.7365 |         16 |            15 |
| Random_Forest       | FR-local      | FR-local      |        |      8.7e-07 |     4e-08   | 3.21e-06  | 58.8541 |         17 |            22 |
| Random_Forest       | AWS-Stockholm | AWS-Stockholm |        |      8.7e-07 |     3e-08   | 5.74e-06  | 54.4427 |         18 |            22 |
| XGBoost             | AWS-Frankfurt | AWS-Frankfurt |        |      7.7e-07 |     3.2e-07 | 1.98e-06  | 49.0315 |         19 |            15 |
| XGBoost             | AWS-Virginia  | AWS-Virginia  |        |      7.7e-07 |     3.2e-07 | 2.16e-06  | 48.6434 |         20 |            15 |
| Random_Forest       | AWS-Frankfurt | AWS-Frankfurt |        |      8.7e-07 |     3.6e-07 | 2.24e-06  | 42.3303 |         21 |            22 |
| Random_Forest       | AWS-Virginia  | AWS-Virginia  |        |      8.7e-07 |     3.6e-07 | 2.45e-06  | 41.8911 |         22 |            22 |
| XGBoost             | BR-local      | BR-local      |        |      7.7e-07 |     8e-08   | 1.434e-05 | 39.9766 |         23 |            15 |
| XGBoost             | IN-local      | IN-local      |        |      7.7e-07 |     5.2e-07 | 2.66e-06  | 36.3108 |         24 |            15 |
| XGBoost             | AWS-SaoPaulo  | AWS-SaoPaulo  |        |      7.7e-07 |     1e-07   | 1.642e-05 | 35.5732 |         25 |            15 |
| Random_Forest       | BR-local      | BR-local      |        |      8.7e-07 |     1e-07   | 1.623e-05 | 32.0849 |         26 |            22 |
| Random_Forest       | IN-local      | IN-local      |        |      8.7e-07 |     5.9e-07 | 3.01e-06  | 27.9371 |         27 |            22 |
| Random_Forest       | AWS-SaoPaulo  | AWS-SaoPaulo  |        |      8.7e-07 |     1.1e-07 | 1.858e-05 | 27.1025 |         28 |            22 |
