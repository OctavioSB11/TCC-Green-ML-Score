# Cartão ambiental — MLP_Neural_Network

Dataset: **breast_cancer** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.9272 ± 0.0265 |
| F1 macro | 0.9225 ± 0.0276 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 1.104 J (IQR 0.311 J) |
| Energia líquida de repouso (E − P₀·t) | 0.2903 J |
| Potência ociosa P₀ | 15.1 W |
| Tempo de parede | 0.05175 s |
| Carbono (IC = 120 gCO₂e/kWh) | 3.679e-05 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 0.0001594 mL |
| Inferência | 0.02854 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 78.62 |

## Comparação com a referência (Logistic_Regression)

| Métrica | Mediana |
|---|---|
| Razão de energia E / E_ref | 16.2 × |
| Custo marginal | — |
| Dominado (Pareto F1 × energia) | 100% das sementes |

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 70.7 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 80 de 81 medições (máx. 72%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
