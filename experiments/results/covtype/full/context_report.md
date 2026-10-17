# Avaliação modelo × contexto de execução

Contextos: `experiments/contexts/contexts.csv` · modelos: 4 · contextos: 7 · configurações: 28

## Concordância com o critério só-energia

- τ_b de Kendall (GMS com pesos 1/3 × energia): 0.8819
- τ_b no simplex de pesos: mín 0.6959, mediana 0.8819, máx 1.0000
- Modelo de menor energia: Logistic_Regression
- Fração do simplex em que o melhor GMS usa outro modelo: 0.0%

Observação: o critério só-energia não distingue contextos (a energia de TI não depende da região); empates de energia entre contextos de um mesmo modelo são tratados pelo τ_b.

## Configurações (pesos 1/3)

| model               | context       | region        | hour   |   energy_kwh |   carbon_kg |    water_l |     gms |   rank_gms |   rank_energy |
|:--------------------|:--------------|:--------------|:-------|-------------:|------------:|-----------:|--------:|-----------:|--------------:|
| Logistic_Regression | FR-local      | FR-local      |        |    1.05e-06  |   4e-08     | 3.87e-06   | 99.5242 |          1 |             1 |
| Logistic_Regression | AWS-Stockholm | AWS-Stockholm |        |    1.05e-06  |   4e-08     | 6.94e-06   | 99.4732 |          2 |             1 |
| Logistic_Regression | AWS-Frankfurt | AWS-Frankfurt |        |    1.05e-06  |   4.3e-07   | 2.7e-06    | 99.3331 |          3 |             1 |
| Logistic_Regression | AWS-Virginia  | AWS-Virginia  |        |    1.05e-06  |   4.3e-07   | 2.95e-06   | 99.328  |          4 |             1 |
| Logistic_Regression | BR-local      | BR-local      |        |    1.05e-06  |   1.2e-07   | 1.959e-05  | 99.2146 |          5 |             1 |
| Logistic_Regression | IN-local      | IN-local      |        |    1.05e-06  |   7.1e-07   | 3.63e-06   | 99.1667 |          6 |             1 |
| Logistic_Regression | AWS-SaoPaulo  | AWS-SaoPaulo  |        |    1.05e-06  |   1.3e-07   | 2.243e-05  | 99.157  |          7 |             1 |
| XGBoost             | FR-local      | FR-local      |        |    5.79e-06  |   2.4e-07   | 2.127e-05  | 97.3857 |          8 |             8 |
| XGBoost             | AWS-Stockholm | AWS-Stockholm |        |    5.79e-06  |   2.2e-07   | 3.811e-05  | 97.1054 |          9 |             8 |
| XGBoost             | AWS-Frankfurt | AWS-Frankfurt |        |    5.79e-06  |   2.37e-06  | 1.485e-05  | 96.3358 |         10 |             8 |
| XGBoost             | AWS-Virginia  | AWS-Virginia  |        |    5.79e-06  |   2.38e-06  | 1.623e-05  | 96.3079 |         11 |             8 |
| XGBoost             | BR-local      | BR-local      |        |    5.79e-06  |   6.4e-07   | 0.00010765 | 95.6849 |         12 |             8 |
| XGBoost             | IN-local      | IN-local      |        |    5.79e-06  |   3.88e-06  | 1.995e-05  | 95.4213 |         13 |             8 |
| XGBoost             | AWS-SaoPaulo  | AWS-SaoPaulo  |        |    5.79e-06  |   7.3e-07   | 0.00012325 | 95.3683 |         14 |             8 |
| Random_Forest       | FR-local      | FR-local      |        |    3.657e-05 |   1.52e-06  | 0.00013428 | 83.4938 |         15 |            15 |
| Random_Forest       | AWS-Stockholm | AWS-Stockholm |        |    3.657e-05 |   1.41e-06  | 0.00024065 | 81.7241 |         16 |            15 |
| Random_Forest       | AWS-Frankfurt | AWS-Frankfurt |        |    3.657e-05 |   1.495e-05 | 9.376e-05  | 76.8651 |         17 |            15 |
| Random_Forest       | AWS-Virginia  | AWS-Virginia  |        |    3.657e-05 |   1.5e-05   | 0.00010249 | 76.6889 |         18 |            15 |
| Random_Forest       | BR-local      | BR-local      |        |    3.657e-05 |   4.02e-06  | 0.00067971 | 72.755  |         19 |            15 |
| Random_Forest       | IN-local      | IN-local      |        |    3.657e-05 |   2.452e-05 | 0.00012597 | 71.0911 |         20 |            15 |
| Random_Forest       | AWS-SaoPaulo  | AWS-SaoPaulo  |        |    3.657e-05 |   4.58e-06  | 0.00077816 | 70.7563 |         21 |            15 |
| MLP_Neural_Network  | FR-local      | FR-local      |        |    9.117e-05 |   3.78e-06  | 0.00033473 | 58.8541 |         22 |            22 |
| MLP_Neural_Network  | AWS-Stockholm | AWS-Stockholm |        |    9.117e-05 |   3.51e-06  | 0.00059988 | 54.4427 |         23 |            22 |
| MLP_Neural_Network  | AWS-Frankfurt | AWS-Frankfurt |        |    9.117e-05 |   3.727e-05 | 0.00023373 | 42.3303 |         24 |            22 |
| MLP_Neural_Network  | AWS-Virginia  | AWS-Virginia  |        |    9.117e-05 |   3.739e-05 | 0.00025548 | 41.8911 |         25 |            22 |
| MLP_Neural_Network  | BR-local      | BR-local      |        |    9.117e-05 |   1.002e-05 | 0.00169435 | 32.0849 |         26 |            22 |
| MLP_Neural_Network  | IN-local      | IN-local      |        |    9.117e-05 |   6.113e-05 | 0.00031402 | 27.9371 |         27 |            22 |
| MLP_Neural_Network  | AWS-SaoPaulo  | AWS-SaoPaulo  |        |    9.117e-05 |   1.143e-05 | 0.00193976 | 27.1025 |         28 |            22 |
