# Cartão ambiental — Logistic_Regression

Dataset: **covtype** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.7587 ± 0.0031 |
| F1 macro | 0.7586 ± 0.0031 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 3.795 J (IQR 0.995 J) |
| Energia líquida de repouso (E − P₀·t) | 0.9168 J |
| Potência ociosa P₀ | 16.9 W |
| Tempo de parede | 0.1625 s |
| Carbono (IC = 120 gCO₂e/kWh) | 0.0001265 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 0.0005482 mL |
| Inferência | 0.001552 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 99.18 |

## Comparação com a referência

Este é o modelo de referência do dataset.

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 63.5 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 71 de 81 medições (máx. 70%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
