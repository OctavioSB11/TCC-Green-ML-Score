# Experimento Comparativo — GreenML Score (Seção 5 do TCC)

## Protocolo de medição (revisão semana 1)

Para cada combinação (dataset, semente, modelo):

1. A semente define a divisão treino/teste (estratificada, 80/20) e a inicialização
   do modelo. O pré-processamento (TF-IDF ou StandardScaler) é ajustado só no treino
   e fica **fora** da janela de medição.
2. **Treino** e **inferência** são medidos em janelas separadas do CodeCarbon. Cada
   fase é repetida `WORKLOAD_REPETITIONS` vezes com clones idênticos do estimador,
   e os valores são reportados **por repetição**.
3. Todos os modelos usam o mesmo paralelismo (`N_JOBS`), inclusive BLAS/OpenMP.
4. A ordem dos modelos é sorteada a cada semente.
5. O GMS é calculado ao final, por dataset, sobre a energia de treino por repetição.

Pendente (semana 2): execução de aquecimento descartada, baseline de potência em
repouso, módulo de contextos de execução e score relativo a um modelo de referência.

## Como executar

```bash
pip install -e .[experiments]

# Validação rápida (500 amostras, 1 semente, 1 repetição)
python experiments/comparative_experiment.py --quick-run --dataset breast_cancer

# Execução completa de um dataset (10 sementes, 10 repetições)
python experiments/comparative_experiment.py --dataset newsgroups

# Análise estatística, figuras e tabelas
python experiments/statistical_analysis.py experiments/results/newsgroups/full
python experiments/generate_results.py
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
├── run_metadata.json         # commit, plataforma, configuração, horários
├── stats_report.md           # gerado por statistical_analysis.py
└── codecarbon/emissions.csv  # log bruto do CodeCarbon (versionado como evidência)
```

Resultados anteriores à revisão estão em `experiments/results/_legacy_v0.1/` e não
devem ser usados no texto final.
