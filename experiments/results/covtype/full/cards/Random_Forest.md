# Cartão ambiental — Random_Forest

Dataset: **covtype** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.8934 ± 0.0041 |
| F1 macro | 0.8934 ± 0.0041 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 131.7 J (IQR 76.9 J) |
| Energia líquida de repouso (E − P₀·t) | 3.65 J |
| Potência ociosa P₀ | 16.9 W |
| Tempo de parede | 7.437 s |
| Carbono (IC = 120 gCO₂e/kWh) | 0.004389 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 0.01902 mL |
| Inferência | 0.562 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 71.71 |

## Comparação com a referência (Logistic_Regression)

| Métrica | Mediana |
|---|---|
| Razão de energia E / E_ref | 35.9 × |
| Custo marginal | 9.32 J por ponto de F1 |
| Dominado (Pareto F1 × energia) | 0% das sementes |

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 55.7 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 71 de 81 medições (máx. 70%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
