# Experimento Comparativo — GreenML Score (Seção 5 do TCC)

## Protocolo de medição (revisão semana 1)

Para cada combinação (dataset, semente, modelo):

1. A semente define a divisão treino/teste (estratificada, 80/20) e a inicialização
   do modelo. O pré-processamento (TF-IDF ou StandardScaler) é ajustado só no treino
   e fica **fora** da janela de medição.
2. **Treino** e **inferência** são medidos em janelas separadas do CodeCarbon. Cada
   fase é repetida ao menos `WORKLOAD_REPETITIONS` vezes com clones idênticos do
   estimador **e** até ocupar `MIN_MEASUREMENT_WINDOW_S` (30 s; 5 s no quick-run),
   para diluir o overhead fixo de start/stop do CodeCarbon. Os valores são
   reportados **por repetição**, com o número efetivo de repetições.
3. Todos os modelos usam o mesmo paralelismo (`N_JOBS`), inclusive BLAS/OpenMP.
4. A ordem dos modelos é sorteada a cada semente.
5. O GMS é calculado ao final, por dataset, sobre a energia de treino por repetição.

Acréscimos da semana 2, por dataset:

6. **Repouso:** antes de tudo, a máquina é medida sem carga por `IDLE_BASELINE_S`
   (60 s; 10 s no quick-run), obtendo a potência ociosa P₀. Cada fase reporta a
   energia bruta e a líquida, E − P₀·t, com t = duração da sessão do CodeCarbon.
   Valores líquidos negativos são mantidos (não truncados).
7. **Aquecimento:** uma execução (treino + inferência) não medida por modelo, antes
   da primeira semente.
8. **Score relativo:** por semente, cada modelo é comparado ao de referência
   (`REFERENCE_MODEL`, Regressão Logística): razão E/E_ref e custo marginal
   (E − E_ref) / ΔF1 em J por ponto de F1; com ΔF1 ≤ 0 o modelo é marcado como dominado.
9. **Procedência:** avisos (`ProvenanceWarning`) quando `tracking_mode = machine`,
   quando a potência de RAM é constante entre medições ou quando a RAM responde por
   mais de 50 % da energia.
10. **Cartão ambiental** em Markdown por modelo.

Avaliação modelo × contexto (região × horário), após o experimento:

```bash
python experiments/context_analysis.py experiments/results/newsgroups/full \
    --contexts experiments/contexts/contexts.csv
```

Os contextos são lidos de `experiments/contexts/contexts.csv` (ver o README da pasta).

Validação física pela bateria e roteiro da execução completa:
`experiments/energy_validation.py` e `docs/execucao_completa.md`.

## Como executar

```bash
pip install -e .[experiments]

# Validação rápida (500 amostras, 1 semente, 1 repetição)
python experiments/comparative_experiment.py --quick-run --dataset breast_cancer

# Execução completa de um dataset (10 sementes, 10 repetições)
python experiments/comparative_experiment.py --dataset newsgroups

# Análise estatística, figuras, tabelas e contextos (todas as execuções full)
python experiments/run_analysis.py
```

**Execuções completas que serão usadas no TCC** devem ser feitas com a máquina
dedicada: notebook na tomada, mesmo plano de energia do Windows, sem IDE, navegador
ou agentes de programação abertos. Qualquer processo concorrente entra na medição.

## Saídas

```
experiments/results/<dataset>/<full|quick_run>/
├── comparative_results.csv   # uma linha por (semente, modelo), precisão total
├── summary_metrics.csv       # resumo por modelo (média, desvio, mediana, IQR)
├── summary_table.md
├── run_metadata.json         # commit, plataforma, configuração, horários, P₀, avisos
├── cards/<modelo>.md         # cartão ambiental por modelo
├── stats_report.md           # gerado por statistical_analysis.py
├── context_*.csv / context_report.md  # gerados por context_analysis.py
└── codecarbon/emissions.csv  # log bruto do CodeCarbon (versionado como evidência)
```

Resultados anteriores à revisão estão em `experiments/results/_legacy_v0.1/` e não
devem ser usados no texto final.
