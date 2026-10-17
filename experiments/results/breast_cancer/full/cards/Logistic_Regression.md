# Cartão ambiental — Logistic_Regression

Dataset: **breast_cancer** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.9719 ± 0.0108 |
| F1 macro | 0.9698 ± 0.0115 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 0.0645 J (IQR 0.0125 J) |
| Energia líquida de repouso (E − P₀·t) | 0.001721 J |
| Potência ociosa P₀ | 15.1 W |
| Tempo de parede | 0.003896 s |
| Carbono (IC = 120 gCO₂e/kWh) | 2.15e-06 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 9.317e-06 mL |
| Inferência | 0.0205 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 98.75 |

## Comparação com a referência

Este é o modelo de referência do dataset.

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 62.4 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 80 de 81 medições (máx. 72%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
