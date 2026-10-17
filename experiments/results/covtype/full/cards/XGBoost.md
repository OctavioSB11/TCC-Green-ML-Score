# Cartão ambiental — XGBoost

Dataset: **covtype** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.8624 ± 0.0041 |
| F1 macro | 0.8624 ± 0.0040 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 20.85 J (IQR 12.2 J) |
| Energia líquida de repouso (E − P₀·t) | 2.95 J |
| Potência ociosa P₀ | 16.9 W |
| Tempo de parede | 0.9907 s |
| Carbono (IC = 120 gCO₂e/kWh) | 0.0006951 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 0.003012 mL |
| Inferência | 0.05887 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 95.52 |

## Comparação com a referência (Logistic_Regression)

| Métrica | Mediana |
|---|---|
| Razão de energia E / E_ref | 5.14 × |
| Custo marginal | 1.644 J por ponto de F1 |
| Dominado (Pareto F1 × energia) | 0% das sementes |

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 60.1 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 71 de 81 medições (máx. 70%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
