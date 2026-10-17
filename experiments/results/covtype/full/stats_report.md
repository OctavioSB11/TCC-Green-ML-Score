# Relatório estatístico

## Estatística descritiva

| model_name          |   gms [mean] |   gms [std] |   gms [median] |   gms [iqr] |   energy_mwh [mean] |   energy_mwh [std] |   energy_mwh [median] |   energy_mwh [iqr] |   train_wall_time_s [mean] |   train_wall_time_s [std] |   train_wall_time_s [median] |   train_wall_time_s [iqr] |
|:--------------------|-------------:|------------:|---------------:|------------:|--------------------:|-------------------:|----------------------:|-------------------:|---------------------------:|--------------------------:|-----------------------------:|--------------------------:|
| Logistic_Regression |      99.197  |      0.1632 |        99.1845 |      0.2138 |              1.0381 |             0.2109 |                1.0543 |             0.2764 |                     0.1576 |                    0.0257 |                       0.1625 |                    0.041  |
| MLP_Neural_Network  |      38.8355 |     25.6312 |        29.4749 |     34.2567 |             79.0698 |            33.1344 |               91.1706 |            44.285  |                    15.3172 |                    5.5165 |                      17.3005 |                    5.9446 |
| Random_Forest       |      70.4627 |      9.3774 |        71.708  |     16.5137 |             38.184  |            12.1226 |               36.5742 |            21.3479 |                     7.5989 |                    1.8058 |                       7.4373 |                    3.2658 |
| XGBoost             |      95.3593 |      1.8152 |        95.519  |      2.6188 |              5.9992 |             2.3466 |                5.7927 |             3.3855 |                     1.0279 |                    0.2727 |                       0.9907 |                    0.472  |

## Testes de hipótese (GMS)

Friedman: χ²_F = 30.0000; p = 1.38e-06 (n = 10 sementes)

Kruskal-Wallis (sem pareamento): H = 35.0400; p = 1.195e-07

Pós-teste: Wilcoxon pareado com correção de Holm

| A                   | B                  |   mediana(A−B) |     p |   p_holm |
|:--------------------|:-------------------|---------------:|------:|---------:|
| Logistic_Regression | MLP_Neural_Network |        69.6676 | 0.002 |   0.0117 |
| Logistic_Regression | Random_Forest      |        27.5217 | 0.002 |   0.0117 |
| Logistic_Regression | XGBoost            |         3.7162 | 0.002 |   0.0117 |
| MLP_Neural_Network  | Random_Forest      |       -31.7731 | 0.002 |   0.0117 |
| MLP_Neural_Network  | XGBoost            |       -64.3328 | 0.002 |   0.0117 |
| Random_Forest       | XGBoost            |       -22.4694 | 0.002 |   0.0117 |

## Testes de hipótese (energia de treino)

Com IC e WUE constantes, o GMS é função monotônica da energia; o teste sobre a energia é o que sustenta diferenças entre modelos.

Friedman: χ²_F = 30.0000; p = 1.38e-06 (n = 10 sementes)

Pós-teste: Wilcoxon pareado com correção de Holm

| A                   | B                  |   mediana(A−B) |        p |   p_holm |
|:--------------------|:-------------------|---------------:|---------:|---------:|
| Logistic_Regression | MLP_Neural_Network |     -9.006e-05 | 0.001953 |  0.01172 |
| Logistic_Regression | Random_Forest      |     -3.558e-05 | 0.001953 |  0.01172 |
| Logistic_Regression | XGBoost            |     -4.804e-06 | 0.001953 |  0.01172 |
| MLP_Neural_Network  | Random_Forest      |      4.107e-05 | 0.001953 |  0.01172 |
| MLP_Neural_Network  | XGBoost            |      8.317e-05 | 0.001953 |  0.01172 |
| Random_Forest       | XGBoost            |      2.905e-05 | 0.001953 |  0.01172 |

## Score relativo à referência (Logistic_Regression)

| model_name          |   E/E_ref (mediana) |   ΔF1 pontos (mediana) |   J por ponto de F1 (mediana) |   dominado (fração) |
|:--------------------|--------------------:|-----------------------:|------------------------------:|--------------------:|
| Logistic_Regression |              1      |                 0      |                      nan      |                   0 |
| MLP_Neural_Network  |             77.9087 |                 9.2177 |                       34.0023 |                   1 |
| Random_Forest       |             35.9142 |                13.5767 |                        9.3203 |                   0 |
| XGBoost             |              5.1364 |                10.3552 |                        1.6436 |                   0 |

## Medição: energia líquida e repetições

| model_name          |   Energia líquida mWh (mediana) |   Repetições de treino (mediana) |   Repetições de inferência (mediana) |   Sessão de treino s (mediana) |   Energia líquida < 0 (fração) |
|:--------------------|--------------------------------:|---------------------------------:|-------------------------------------:|-------------------------------:|-------------------------------:|
| Logistic_Regression |                          0.2547 |                              185 |                              36318   |                        31.5997 |                            0   |
| MLP_Neural_Network  |                          6.7208 |                               10 |                               2481   |                       174.51   |                            0.4 |
| Random_Forest       |                          1.014  |                               10 |                                127   |                        75.8788 |                            0.4 |
| XGBoost             |                          0.8195 |                               32 |                               1221.5 |                        32.0637 |                            0.3 |

- P₀ = 16.87 W (repouso de 62 s); janela mínima por fase: 30.0 s

## O GMS carrega informação além de energia e tempo?

- Spearman GMS × energia: ρ = -1.0000 (p = 0)
- Spearman GMS × tempo de parede: ρ = -0.9944 (p = 1.16e-38)
- Spearman GMS × tempo de CPU: ρ = -0.9944 (p = 1.16e-38)

- max |GMS − 100·(1 − E/E_max)| = 2.62e-11 (≈ 0 ⇒ o GMS é função exclusiva da energia neste cenário)

## Procedência da medição

- Modo(s) do CodeCarbon: ['machine']
- Potência de RAM (W): [10.0]
- Fração da energia atribuída à RAM: média 58.1%, mín 46.8%, máx 70.3%

Avisos registrados na execução:

- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 71 de 81 medições (máx. 70%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
