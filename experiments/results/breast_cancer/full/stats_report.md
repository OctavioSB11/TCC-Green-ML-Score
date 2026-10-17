# Relatório estatístico

## Estatística descritiva

| model_name          |   gms [mean] |   gms [std] |   gms [median] |   gms [iqr] |   energy_mwh [mean] |   energy_mwh [std] |   energy_mwh [median] |   energy_mwh [iqr] |   train_wall_time_s [mean] |   train_wall_time_s [std] |   train_wall_time_s [median] |   train_wall_time_s [iqr] |
|:--------------------|-------------:|------------:|---------------:|------------:|--------------------:|-------------------:|----------------------:|-------------------:|---------------------------:|--------------------------:|-----------------------------:|--------------------------:|
| Logistic_Regression |      98.3752 |      1.5215 |        98.7506 |      0.2423 |              0.0233 |             0.0218 |                0.0179 |             0.0035 |                     0.0041 |                    0.0017 |                       0.0039 |                    0.0008 |
| MLP_Neural_Network  |      78.2102 |      6.0419 |        78.6221 |      6.0148 |              0.3125 |             0.0866 |                0.3066 |             0.0863 |                     0.0553 |                    0.013  |                       0.0517 |                    0.012  |
| Random_Forest       |      34.587  |     14.2151 |        39.1184 |     11.0478 |              0.9381 |             0.2039 |                0.8731 |             0.1584 |                     0.1622 |                    0.0272 |                       0.15   |                    0.0245 |
| XGBoost             |      42.2363 |      9.374  |        46.1928 |     12.9801 |              0.8284 |             0.1344 |                0.7716 |             0.1861 |                     0.1441 |                    0.0182 |                       0.1363 |                    0.0303 |

## Testes de hipótese (GMS)

Friedman: χ²_F = 27.4800; p = 4.669e-06 (n = 10 sementes)

Kruskal-Wallis (sem pareamento): H = 33.3498; p = 2.717e-07

Pós-teste: Wilcoxon pareado com correção de Holm

| A                   | B                  |   mediana(A−B) |      p |   p_holm |
|:--------------------|:-------------------|---------------:|-------:|---------:|
| Logistic_Regression | MLP_Neural_Network |        20.2832 | 0.002  |   0.0117 |
| Logistic_Regression | Random_Forest      |        58.6248 | 0.002  |   0.0117 |
| Logistic_Regression | XGBoost            |        52.6092 | 0.002  |   0.0117 |
| MLP_Neural_Network  | Random_Forest      |        43.5581 | 0.002  |   0.0117 |
| MLP_Neural_Network  | XGBoost            |        37.1734 | 0.002  |   0.0117 |
| Random_Forest       | XGBoost            |        -6.2312 | 0.3223 |   0.3223 |

## Testes de hipótese (energia de treino)

Com IC e WUE constantes, o GMS é função monotônica da energia; o teste sobre a energia é o que sustenta diferenças entre modelos.

Friedman: χ²_F = 27.4800; p = 4.669e-06 (n = 10 sementes)

Pós-teste: Wilcoxon pareado com correção de Holm

| A                   | B                  |   mediana(A−B) |        p |   p_holm |
|:--------------------|:-------------------|---------------:|---------:|---------:|
| Logistic_Regression | MLP_Neural_Network |     -2.909e-07 | 0.001953 |  0.01172 |
| Logistic_Regression | Random_Forest      |     -8.407e-07 | 0.001953 |  0.01172 |
| Logistic_Regression | XGBoost            |     -7.544e-07 | 0.001953 |  0.01172 |
| MLP_Neural_Network  | Random_Forest      |     -6.246e-07 | 0.001953 |  0.01172 |
| MLP_Neural_Network  | XGBoost            |     -5.331e-07 | 0.001953 |  0.01172 |
| Random_Forest       | XGBoost            |      8.936e-08 | 0.3223   |  0.3223  |

## Score relativo à referência (Logistic_Regression)

| model_name          |   E/E_ref (mediana) |   ΔF1 pontos (mediana) |   J por ponto de F1 (mediana) |   dominado (fração) |
|:--------------------|--------------------:|-----------------------:|------------------------------:|--------------------:|
| Logistic_Regression |              1      |                 0      |                      nan      |                 0   |
| MLP_Neural_Network  |             16.1802 |                -4.7793 |                      nan      |                 1   |
| Random_Forest       |             52.354  |                -1.4592 |                        0.9414 |                 0.9 |
| XGBoost             |             50.8455 |                -0.9489 |                        1.1691 |                 0.8 |

## Medição: energia líquida e repetições

| model_name          |   Energia líquida mWh (mediana) |   Repetições de treino (mediana) |   Repetições de inferência (mediana) |   Sessão de treino s (mediana) |   Energia líquida < 0 (fração) |
|:--------------------|--------------------------------:|---------------------------------:|-------------------------------------:|-------------------------------:|-------------------------------:|
| Logistic_Regression |                          0.0005 |                           7702   |                             208519   |                        31.5061 |                              0 |
| MLP_Neural_Network  |                          0.0806 |                            580.5 |                             152926   |                        31.5349 |                              0 |
| Random_Forest       |                          0.2145 |                            200.5 |                               4600.5 |                        31.5865 |                              0 |
| XGBoost             |                          0.1949 |                            220.5 |                              40384.5 |                        31.5628 |                              0 |

- P₀ = 15.05 W (repouso de 62 s); janela mínima por fase: 30.0 s

## O GMS carrega informação além de energia e tempo?

- Spearman GMS × energia: ρ = -1.0000 (p = 0)
- Spearman GMS × tempo de parede: ρ = -0.9859 (p = 3.93e-31)
- Spearman GMS × tempo de CPU: ρ = -0.9820 (p = 4.14e-29)

- max |GMS − 100·(1 − E/E_max)| = 1.42e-14 (≈ 0 ⇒ o GMS é função exclusiva da energia neste cenário)

## Procedência da medição

- Modo(s) do CodeCarbon: ['machine']
- Potência de RAM (W): [10.0]
- Fração da energia atribuída à RAM: média 66.9%, mín 29.4%, máx 71.8%

Avisos registrados na execução:

- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 80 de 81 medições (máx. 72%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
