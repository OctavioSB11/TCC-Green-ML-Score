# Relatório estatístico

## Estatística descritiva

| model_name          |   gms [mean] |   gms [std] |   gms [median] |   gms [iqr] |   energy_mwh [mean] |   energy_mwh [std] |   energy_mwh [median] |   energy_mwh [iqr] |   train_wall_time_s [mean] |   train_wall_time_s [std] |   train_wall_time_s [median] |   train_wall_time_s [iqr] |
|:--------------------|-------------:|------------:|---------------:|------------:|--------------------:|-------------------:|----------------------:|-------------------:|---------------------------:|--------------------------:|-----------------------------:|--------------------------:|
| Logistic_Regression |      99.7622 |      0.0494 |        99.7575 |      0.0682 |              0.101  |             0.021  |                0.103  |             0.029  |                     0.0153 |                    0.002  |                       0.0149 |                    0.0019 |
| MLP_Neural_Network  |      39.5339 |     20.8795 |        41.9362 |     12.3804 |             25.6899 |             8.871  |               24.6692 |             5.26   |                     4.2888 |                    1.1788 |                       4.2331 |                    1.042  |
| Random_Forest       |      78.4956 |      6.0067 |        77.4619 |      6.0005 |              9.1365 |             2.552  |                9.5756 |             2.5494 |                     1.2769 |                    0.2286 |                       1.3438 |                    0.1404 |
| XGBoost             |      52.0634 |     12.0175 |        52.3581 |     13.6446 |             20.3665 |             5.1058 |               20.2413 |             5.7971 |                     3.5733 |                    0.6431 |                       3.6533 |                    0.6666 |

## Testes de hipótese (GMS)

Friedman: χ²_F = 28.0800; p = 3.494e-06 (n = 10 sementes)

Kruskal-Wallis (sem pareamento): H = 31.5498; p = 6.511e-07

Pós-teste: Wilcoxon pareado com correção de Holm

| A                   | B                  |   mediana(A−B) |      p |   p_holm |
|:--------------------|:-------------------|---------------:|-------:|---------:|
| Logistic_Regression | MLP_Neural_Network |        57.8068 | 0.002  |   0.0117 |
| Logistic_Regression | Random_Forest      |        22.3199 | 0.002  |   0.0117 |
| Logistic_Regression | XGBoost            |        47.4207 | 0.002  |   0.0117 |
| MLP_Neural_Network  | Random_Forest      |       -33.9069 | 0.002  |   0.0117 |
| MLP_Neural_Network  | XGBoost            |       -10.9665 | 0.0098 |   0.0117 |
| Random_Forest       | XGBoost            |        26.2703 | 0.002  |   0.0117 |

## Testes de hipótese (energia de treino)

Com IC e WUE constantes, o GMS é função monotônica da energia; o teste sobre a energia é o que sustenta diferenças entre modelos.

Friedman: χ²_F = 28.0800; p = 3.494e-06 (n = 10 sementes)

Pós-teste: Wilcoxon pareado com correção de Holm

| A                   | B                  |   mediana(A−B) |        p |   p_holm |
|:--------------------|:-------------------|---------------:|---------:|---------:|
| Logistic_Regression | MLP_Neural_Network |     -2.456e-05 | 0.001953 |  0.01172 |
| Logistic_Regression | Random_Forest      |     -9.483e-06 | 0.001953 |  0.01172 |
| Logistic_Regression | XGBoost            |     -2.015e-05 | 0.001953 |  0.01172 |
| MLP_Neural_Network  | Random_Forest      |      1.441e-05 | 0.001953 |  0.01172 |
| MLP_Neural_Network  | XGBoost            |      4.659e-06 | 0.009766 |  0.01172 |
| Random_Forest       | XGBoost            |     -1.116e-05 | 0.001953 |  0.01172 |

## Score relativo à referência (Logistic_Regression)

| model_name          |   E/E_ref (mediana) |   ΔF1 pontos (mediana) |   J por ponto de F1 (mediana) |   dominado (fração) |
|:--------------------|--------------------:|-----------------------:|------------------------------:|--------------------:|
| Logistic_Regression |              1      |                 0      |                      nan      |                 0   |
| MLP_Neural_Network  |            248.029  |                -0.1318 |                       87.3038 |                 0.7 |
| Random_Forest       |             99.0382 |                -3.8149 |                      nan      |                 1   |
| XGBoost             |            218.05   |                -6.8163 |                      nan      |                 1   |

## Medição: energia líquida e repetições

| model_name          |   Energia líquida mWh (mediana) |   Repetições de treino (mediana) |   Repetições de inferência (mediana) |   Sessão de treino s (mediana) |   Energia líquida < 0 (fração) |
|:--------------------|--------------------------------:|---------------------------------:|-------------------------------------:|-------------------------------:|-------------------------------:|
| Logistic_Regression |                          0.0265 |                           2015.5 |                              83464.5 |                        31.5171 |                              0 |
| MLP_Neural_Network  |                          6.3946 |                             10   |                              15120.5 |                        43.8406 |                              0 |
| Random_Forest       |                          4.0978 |                             22.5 |                                524.5 |                        31.8944 |                              0 |
| XGBoost             |                          4.5219 |                             10   |                               6155.5 |                        38.0403 |                              0 |

- P₀ = 15.11 W (repouso de 62 s); janela mínima por fase: 30.0 s

## O GMS carrega informação além de energia e tempo?

- Spearman GMS × energia: ρ = -1.0000 (p = 0)
- Spearman GMS × tempo de parede: ρ = -0.9600 (p = 1.29e-22)
- Spearman GMS × tempo de CPU: ρ = -0.9585 (p = 2.56e-22)

- max |GMS − 100·(1 − E/E_max)| = 2.84e-14 (≈ 0 ⇒ o GMS é função exclusiva da energia neste cenário)

## Procedência da medição

- Modo(s) do CodeCarbon: ['machine']
- Potência de RAM (W): [10.0]
- Fração da energia atribuída à RAM: média 49.5%, mín 38.5%, máx 62.2%

Avisos registrados na execução:

- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 39 de 81 medições (máx. 64%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
