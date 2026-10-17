# Cartão ambiental — Logistic_Regression

Dataset: **newsgroups** · execuções (sementes): **10**

## Desempenho

| Métrica | Valor (média ± desvio) |
|---|---|
| Acurácia | 0.9356 ± 0.0114 |
| F1 macro | 0.9356 ± 0.0114 |

## Custo ambiental (treino, por execução)

| Métrica | Mediana |
|---|---|
| Energia bruta | 0.371 J (IQR 0.104 J) |
| Energia líquida de repouso (E − P₀·t) | 0.09523 J |
| Potência ociosa P₀ | 15.1 W |
| Tempo de parede | 0.01489 s |
| Carbono (IC = 120 gCO₂e/kWh) | 1.237e-05 g CO₂e |
| Água (WUE = 0.52 L/kWh) | 5.358e-05 mL |
| Inferência | 0.01835 J / 1.000 amostras |
| GreenML Score (0–100, relativo ao conjunto) | 99.76 |

## Comparação com a referência

Este é o modelo de referência do dataset.

## Procedência da medição

- Modo do CodeCarbon: machine
- Fração da energia atribuída à RAM (mediana): 48.4 %
- ⚠ tracking_mode = machine: a energia inclui todos os processos da máquina, não apenas o processo medido.
- ⚠ A RAM responde por mais de 50% da energia em 39 de 81 medições (máx. 64%); diferenças entre modelos refletem sobretudo o tempo de execução.
- ⚠ Potência de RAM constante (10.000 W) em 81 medições: valor estimado pelo CodeCarbon, não medido.
