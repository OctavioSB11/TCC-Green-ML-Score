# Cartão ambiental — Random_Forest

Dataset: **newsgroups** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.8947 ± 0.0125 |
| F1 macro | 0.8944 ± 0.0127 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 34.47 J (IQR 9.18 J) |
| Energia líquida de repouso (E − P₀·t) | 14.75 J |
| Potência ociosa P₀ | 15.1 W |
| Tempo de parede | 1.344 s |
| Carbono (IC = 120 gCO₂e/kWh) | 0.001149 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 0.004979 mL |
| Inferência | 3.681 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 77.46 |

## Comparação com a referência (Logistic_Regression)

| Métrica | Mediana |
|---|---|
| Razão de energia E / E_ref | 99 × |
| Custo marginal | — |
| Dominado (Pareto F1 × energia) | 100% das sementes |

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 51.9 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 39 de 81 medições (máx. 64%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
