# Cartão ambiental — XGBoost

Dataset: **breast_cancer** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.9632 ± 0.0159 |
| F1 macro | 0.9605 ± 0.0170 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 2.778 J (IQR 0.67 J) |
| Energia líquida de repouso (E − P₀·t) | 0.7016 J |
| Potência ociosa P₀ | 15.1 W |
| Tempo de parede | 0.1363 s |
| Carbono (IC = 120 gCO₂e/kWh) | 9.26e-05 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 0.0004012 mL |
| Inferência | 0.1049 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 46.19 |

## Comparação com a referência (Logistic_Regression)

| Métrica | Mediana |
|---|---|
| Razão de energia E / E_ref | 50.8 × |
| Custo marginal | 1.169 J por ponto de F1 |
| Dominado (Pareto F1 × energia) | 80% das sementes |

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 70.9 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 80 de 81 medições (máx. 72%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
