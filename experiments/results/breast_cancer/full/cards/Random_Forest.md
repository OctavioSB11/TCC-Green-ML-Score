# Cartão ambiental — Random_Forest

Dataset: **breast_cancer** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.9588 ± 0.0124 |
| F1 macro | 0.9556 ± 0.0133 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 3.143 J (IQR 0.57 J) |
| Energia líquida de repouso (E − P₀·t) | 0.7723 J |
| Potência ociosa P₀ | 15.1 W |
| Tempo de parede | 0.15 s |
| Carbono (IC = 120 gCO₂e/kWh) | 0.0001048 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 0.000454 mL |
| Inferência | 0.9541 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 39.12 |

## Comparação com a referência (Logistic_Regression)

| Métrica | Mediana |
|---|---|
| Razão de energia E / E_ref | 52.4 × |
| Custo marginal | 0.9414 J por ponto de F1 |
| Dominado (Pareto F1 × energia) | 90% das sementes |

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 71.5 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 80 de 81 medições (máx. 72%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
