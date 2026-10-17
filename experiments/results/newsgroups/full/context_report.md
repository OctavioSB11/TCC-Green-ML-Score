# Avaliação modelo × contexto de execução

Contextos: `experiments/contexts/contexts.csv` · modelos: 4 · contextos: 7 · configurações: 28

## Concordância com o critério só-energia

- τ_b de Kendall (GMS com pesos 1/3 × energia): 0.7979
- τ_b no simplex de pesos: mín 0.5819, mediana 0.7859, máx 1.0000
- Modelo de menor energia: Logistic_Regression
- Fração do simplex em que o melhor GMS usa outro modelo: 0.0%

Observação: o critério só-energia não distingue contextos (a energia de TI não depende da região); empates de energia entre contextos de um mesmo modelo são tratados pelo τ_b.

## Configurações (pesos 1/3)

| model               | context       | region        | hour   |   energy_kwh |   carbon_kg |    water_l |     gms |   rank_gms |   rank_energy |
|:--------------------|:--------------|:--------------|:-------|-------------:|------------:|-----------:|--------:|-----------:|--------------:|
| Logistic_Regression | FR-local      | FR-local      |        |    1e-07     |   0         | 3.8e-07    | 99.8281 |          1 |             1 |
| Logistic_Regression | AWS-Stockholm | AWS-Stockholm |        |    1e-07     |   0         | 6.8e-07    | 99.8097 |          2 |             1 |
| Logistic_Regression | AWS-Frankfurt | AWS-Frankfurt |        |    1e-07     |   4e-08     | 2.6e-07    | 99.7591 |          3 |             1 |
| Logistic_Regression | AWS-Virginia  | AWS-Virginia  |        |    1e-07     |   4e-08     | 2.9e-07    | 99.7573 |          4 |             1 |
| Logistic_Regression | BR-local      | BR-local      |        |    1e-07     |   1e-08     | 1.92e-06   | 99.7163 |          5 |             1 |
| Logistic_Regression | IN-local      | IN-local      |        |    1e-07     |   7e-08     | 3.5e-07    | 99.699  |          6 |             1 |
| Logistic_Regression | AWS-SaoPaulo  | AWS-SaoPaulo  |        |    1e-07     |   1e-08     | 2.19e-06   | 99.6955 |          7 |             1 |
| Random_Forest       | FR-local      | FR-local      |        |    9.58e-06  |   4e-07     | 3.516e-05  | 84.0287 |          8 |             8 |
| Random_Forest       | AWS-Stockholm | AWS-Stockholm |        |    9.58e-06  |   3.7e-07   | 6.301e-05  | 82.3164 |          9 |             8 |
| Random_Forest       | AWS-Frankfurt | AWS-Frankfurt |        |    9.58e-06  |   3.91e-06  | 2.455e-05  | 77.6148 |         10 |             8 |
| Random_Forest       | AWS-Virginia  | AWS-Virginia  |        |    9.58e-06  |   3.93e-06  | 2.683e-05  | 77.4444 |         11 |             8 |
| Random_Forest       | BR-local      | BR-local      |        |    9.58e-06  |   1.05e-06  | 0.00017796 | 73.638  |         12 |             8 |
| Random_Forest       | IN-local      | IN-local      |        |    9.58e-06  |   6.42e-06  | 3.298e-05  | 72.0279 |         13 |             8 |
| Random_Forest       | AWS-SaoPaulo  | AWS-SaoPaulo  |        |    9.58e-06  |   1.2e-06   | 0.00020373 | 71.704  |         14 |             8 |
| XGBoost             | FR-local      | FR-local      |        |    2.024e-05 |   8.4e-07   | 7.432e-05  | 66.2394 |         15 |            15 |
| XGBoost             | AWS-Stockholm | AWS-Stockholm |        |    2.024e-05 |   7.8e-07   | 0.00013318 | 62.6198 |         16 |            15 |
| MLP_Neural_Network  | FR-local      | FR-local      |        |    2.467e-05 |   1.02e-06  | 9.057e-05  | 58.8541 |         17 |            22 |
| MLP_Neural_Network  | AWS-Stockholm | AWS-Stockholm |        |    2.467e-05 |   9.5e-07   | 0.00016232 | 54.4427 |         18 |            22 |
| XGBoost             | AWS-Frankfurt | AWS-Frankfurt |        |    2.024e-05 |   8.27e-06  | 5.189e-05  | 52.6814 |         19 |            15 |
| XGBoost             | AWS-Virginia  | AWS-Virginia  |        |    2.024e-05 |   8.3e-06   | 5.672e-05  | 52.3211 |         20 |            15 |
| XGBoost             | BR-local      | BR-local      |        |    2.024e-05 |   2.23e-06  | 0.00037617 | 44.275  |         21 |            15 |
| MLP_Neural_Network  | AWS-Frankfurt | AWS-Frankfurt |        |    2.467e-05 |   1.008e-05 | 6.324e-05  | 42.3303 |         22 |            22 |
| MLP_Neural_Network  | AWS-Virginia  | AWS-Virginia  |        |    2.467e-05 |   1.012e-05 | 6.913e-05  | 41.8911 |         23 |            22 |
| XGBoost             | IN-local      | IN-local      |        |    2.024e-05 |   1.357e-05 | 6.972e-05  | 40.8717 |         24 |            15 |
| XGBoost             | AWS-SaoPaulo  | AWS-SaoPaulo  |        |    2.024e-05 |   2.54e-06  | 0.00043066 | 40.1869 |         25 |            15 |
| MLP_Neural_Network  | BR-local      | BR-local      |        |    2.467e-05 |   2.71e-06  | 0.00045846 | 32.0849 |         26 |            22 |
| MLP_Neural_Network  | IN-local      | IN-local      |        |    2.467e-05 |   1.654e-05 | 8.497e-05  | 27.9371 |         27 |            22 |
| MLP_Neural_Network  | AWS-SaoPaulo  | AWS-SaoPaulo  |        |    2.467e-05 |   3.09e-06  | 0.00052487 | 27.1025 |         28 |            22 |
