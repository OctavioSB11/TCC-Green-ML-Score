# Cartão ambiental — XGBoost

Dataset: **newsgroups** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.8692 ± 0.0115 |
| F1 macro | 0.8691 ± 0.0115 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 72.87 J (IQR 20.9 J) |
| Energia líquida de repouso (E − P₀·t) | 16.28 J |
| Potência ociosa P₀ | 15.1 W |
| Tempo de parede | 3.653 s |
| Carbono (IC = 120 gCO₂e/kWh) | 0.002429 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 0.01053 mL |
| Inferência | 0.2552 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 52.36 |

## Comparação com a referência (Logistic_Regression)

| Métrica | Mediana |
|---|---|
| Razão de energia E / E_ref | 218 × |
| Custo marginal | — |
| Dominado (Pareto F1 × energia) | 100% das sementes |

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 49.3 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 39 de 81 medições (máx. 64%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
