# Roteiro da execução completa (semana 3)

Executado **pela dupla**, na máquina de medição escolhida. Nenhum agente de
programação, IDE ou navegador aberto durante as medições: qualquer processo entra
na medição (`tracking_mode = machine`).

## 0. Máquina de medição

**Notebook do Danilo** (i5-1335U, 16 GB, Windows 11, CodeCarbon 3.2.6), decidido
pela dupla em 14/10/2026. A validação com o medidor e **todas** as execuções
completas devem ser feitas nele; resultados de outra máquina não são comparáveis
(o CodeCarbon usa modelos de potência diferentes). Detalhes em
`docs/ambiente_medicao.md`.

## 1. Preparação da máquina

- [ ] Notebook **na tomada**, ligado pelo **medidor**, bateria acima de 80 %.
- [ ] Plano de energia do Windows fixo (ex.: "Equilibrado") e anotado; brilho fixo.
- [ ] Windows Update pausado; antivírus sem varredura agendada; OneDrive pausado.
- [ ] Fechar navegador, IDE, Claude/agentes, Teams/Discord etc.
- [ ] Wi-Fi ligado apenas se os datasets ainda não estiverem em cache
  (`~/scikit_learn_data`); depois pode ser desligado.
  O primeiro download do 20 Newsgroups extrai ~19 mil arquivos e levou ~11 min
  no notebook do Danilo; faça-o antes, com `--quick-run`, e não durante a medição.
- [ ] Registrar data, hora de início e temperatura ambiente aproximada.

## 2. Validação com o medidor (antes do experimento)

```powershell
cd "<pasta do repositório>"
.venv\Scripts\activate
python experiments/meter_validation.py --trials 3 --duration 600
```

O script pede a leitura acumulada do medidor (Wh) no início e no fim de cada fase
(repouso e carga, 10 min cada, 3 tentativas ≈ 1 h). Se o medidor só mostrar
potência instantânea, use `--meter-mode power` e digite a potência média observada.
Saída: `experiments/results/meter_validation/*.csv` e `*.md`.

## 3. Experimento completo

Um dataset por vez, sem usar o computador durante a execução:

```powershell
python experiments/comparative_experiment.py --dataset breast_cancer --no-mlflow
python experiments/comparative_experiment.py --dataset newsgroups --no-mlflow
python experiments/comparative_experiment.py --dataset covtype --no-mlflow
```

Protocolo aplicado automaticamente por dataset: repouso de 60 s (P₀), aquecimento
por modelo, 10 sementes × 4 modelos × (treino + inferência), cada fase com ≥ 10
repetições **e** janela mínima de 30 s.

Tempo estimado (piso; o real depende do tempo de treino de cada modelo):

| Dataset | Estimativa |
|---|---|
| breast_cancer | ≈ 45 min (todas as fases ficam no piso de 30 s) |
| newsgroups | ≈ 45–60 min |
| covtype (50 mil amostras) | 2–4 h (Random Forest e MLP: 10 repetições de dezenas de segundos por fase) |

Remova `--no-mlflow` se quiser os registros no MLflow (`mlruns/` não é versionado).

## 4. Análise

```powershell
python experiments/statistical_analysis.py experiments/results/breast_cancer/full
python experiments/statistical_analysis.py experiments/results/newsgroups/full
python experiments/statistical_analysis.py experiments/results/covtype/full
# após preencher experiments/contexts/contexts.csv:
python experiments/context_analysis.py experiments/results/newsgroups/full --contexts experiments/contexts/contexts.csv
```

## 5. Versionamento

Os resultados `full/` são versionados (os `quick_run/` não):

```powershell
git add experiments/results docs/ambiente_medicao.md
git commit -m "resultados: execução completa e validação com medidor"
git push -u origin main
```

## Critérios para descartar e repetir uma execução

- Aviso de `MeasurementError` ou interrupção.
- P₀ muito diferente entre datasets (> 20 %) sem explicação.
- Uso do computador, suspensão de tela ou troca do plano de energia durante a execução.
