# Cartão ambiental — MLP_Neural_Network

Dataset: **newsgroups** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.9336 ± 0.0134 |
| F1 macro | 0.9335 ± 0.0135 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 88.81 J (IQR 18.9 J) |
| Energia líquida de repouso (E − P₀·t) | 23.02 J |
| Potência ociosa P₀ | 15.1 W |
| Tempo de parede | 4.233 s |
| Carbono (IC = 120 gCO₂e/kWh) | 0.00296 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 0.01283 mL |
| Inferência | 0.1082 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 41.94 |

## Comparação com a referência (Logistic_Regression)

| Métrica | Mediana |
|---|---|
| Razão de energia E / E_ref | 248 × |
| Custo marginal | 87.3 J por ponto de F1 |
| Dominado (Pareto F1 × energia) | 70% das sementes |

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 47.8 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 39 de 81 medições (máx. 64%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
