# Plano de revisão do TCC — GreenML Score

Defesa: 23 a 27/11/2026. Meta de texto pronto: até 01/11/2026.

## Semana 1 (28/09 – 04/10) — status

### Concluído (branch `revisao/semana-1`)
| Commit | Conteúdo |
|---|---|
| `fix(collector)` | Falha de leitura não vira mais consumo zero (`MeasurementError`); energia lida de `final_emissions_data`; `MeasurementDetails` com procedência |
| `fix(mlflow)` | GMS só é registrado com limites de normalização definidos |
| `fix(experimento)` | Treino e inferência medidos separadamente, por repetição; clones idênticos; `N_JOBS` e threads BLAS iguais para todos; semente controla a divisão; ordem dos modelos sorteada; sem dados sintéticos; saídas por dataset/modo; `run_metadata.json`; 10 sementes |
| `fix(resultados)` | μWh → mWh; README de resultados gerado a partir dos dados; sensibilidade no novo layout |
| `feat(análise)` | `statistical_analysis.py` e `test_gms_properties.py` |
| `chore(resultados)` | Resultados e figuras da v0.1 isolados em `_legacy_v0.1/` |

Validação feita fora da máquina de vocês: suíte de testes (40 testes) e
experimento em `breast_cancer` executados com *stubs* do CodeCarbon e do MLflow.
**Ainda não foram executados com as bibliotecas reais.**

### Tarefas para o Claude Code (integrante A)
1. ~~`pip install -e .[dev,experiments]`; `black`, `ruff` e `pytest`~~ — feito (`f721c37`).
2. ~~Confirmar `final_emissions_data` no CodeCarbon 3.2.6~~ — feito (`docs/ambiente_medicao.md`).
3. ~~`--quick-run` nos três datasets~~ — feito (14/10).
4. ~~Registrar o backend de medição da CPU~~ — feito (`84afad6`).
5. ~~Merge da branch na `main`~~ — feito (`b4ec4fb`).

### Pendente — correções de integridade no texto (integrante B)
Corrigir agora apenas o que é **falso**; os números da Seção 8 serão substituídos
na semana 4.

| Seção (.docx) | Correção |
|---|---|
| Resumo / Abstract | Strubell et al. (2019): 1.438 **lbs** CO₂e (≈ 652 kg), não kg. Remover "resultados parciais" se o texto for a versão final |
| 3.3 e 4.7 | Remover "dimensões ortogonais"; inserir a demonstração de que, com IC e WUE constantes, GMS = E_norm para quaisquer pesos |
| 3.5 e 5 | IMDB/sentimentos → 20 Newsgroups, 2 categorias (rec.autos × sci.med), classificação de tópico; 6 → 4 modelos; remover BERT, DistilBERT, LSTM e GPU; hardware real (i5-1335U, 16 GB, Windows 11 — ver `docs/ambiente_medicao.md`); CodeCarbon 3.2.6; divisão 80/20 |
| 5.6 (hipóteses) | Serão reescritas com a nova pergunta (semana 5). Registrar desde já que a H3 original foi refutada (XGBoost teve o menor GMS) |
| 8.1, Tabela 1 | "μWh" → "mWh" (1,8 × 10⁻⁵ kWh = 18 mWh) |
| 8.2 | Remover "superioridade estatisticamente comprovada"; com n = 3, testes par a par não têm poder |
| 8.3 | Substituir: as colunas BR e US são idênticas no CSV; o cenário "Alemanha" nunca foi calculado |
| 8.5 | A tabela hipotética usa razões C/E diferentes por modelo, o que contradiz C = E × IC com IC fixo; remover ou justificar explicitamente |
| Após 8.4 | Remover as tabelas A/B/C sem legenda |
| Conclusão | Remover "seis arquiteturas" |

### Pendente — dupla
- Comprar o medidor de consumo de tomada.
- Registrar por escrito a mudança de objetivo com o orientador.

## Semana 2 (05/10 – 11/10) — status (implementada em 14/10, não versionada)

| Item | Onde | Estado |
|---|---|---|
| 1. Aquecimento | `warm_up()` em `experiments/comparative_experiment.py`; `config.WARMUP`, `--no-warmup` | Feito |
| 2. Baseline de repouso | `measure_idle()`; `config.IDLE_BASELINE_S` (60 s; 10 s no quick-run), `--idle-seconds`; colunas `energy_net_kwh`, `energy_net_j`, `infer_energy_net_kwh`, `idle_power_w`, `train_session_s` | Feito |
| 3. Avisos de procedência | `provenance_warnings_for()` e `ProvenanceWarning` em `green_ml_score/collectors/codecarbon.py`; gravados em `run_metadata.json` e nos cartões | Feito |
| 4. Score relativo | `green_ml_score/scoring/relative.py`; `add_relative_scores()` pareado por semente; colunas `energy_ratio_ref`, `delta_f1_points`, `marginal_cost_j_per_f1_point`, `dominated` | Feito |
| 5. Módulo `contexts` | `green_ml_score/contexts/` (`ExecutionContext`, `load_contexts_csv`, `evaluate_configurations`, `kendall_tau_b`, `simplex_grid`); script `experiments/context_analysis.py` | Feito; **falta preencher `experiments/contexts/contexts.csv`** (integrante B) |
| 6. Cartão ambiental | `green_ml_score/reporting/card.py`; gravado em `results/<dataset>/<modo>/cards/<modelo>.md` | Feito |

Validação: `black`, `ruff` e `pytest` (80 testes) passando; `--quick-run` em
`breast_cancer` executado com CodeCarbon 3.2.6 real.

**Achado do quick-run (14/10) e correção:** com 1 repetição, cada fase durava
1,5–2,2 s e a energia de sessão (17–28 J) era dominada pelo overhead fixo do
CodeCarbon; a energia líquida (E − P₀·t) saiu **negativa** para todos os modelos
(a Regressão Logística "custava" 17 J por treino de 0,02 s).

Correção adotada: **janela mínima de medição** (`MIN_MEASUREMENT_WINDOW_S` = 30 s;
5 s no quick-run; `--min-window`). Cada fase é repetida, além do mínimo de
repetições, até ocupar a janela; o número efetivo de repetições é registrado
(`train_repetitions`, `infer_repetitions`). No mesmo quick-run, a energia por treino
da Regressão Logística caiu de 17 J para 0,39 J (273 repetições) e a potência
média implícita (E/t ≈ 19–25 W) ficou coerente entre os modelos. As energias
líquidas ficaram próximas de zero (−0,5 a +1,8 J), compatíveis com o ruído de um
P₀ medido por apenas 10 s; na execução completa P₀ é medido por 60 s.

## Semana 2 — especificação original

1. **Aquecimento:** uma execução descartada por modelo, antes da primeira semente.
2. **Baseline de repouso:** no início de cada dataset, medir ~60 s sem carga e obter
   a potência ociosa P₀. Reportar energia bruta e líquida (E − P₀·t).
3. **Avisos de procedência:** alertar quando `tracking_mode = machine`, quando a
   potência de RAM for constante ou quando a RAM responder por > 50 % da energia.
4. **Score relativo à referência:** modelo de referência por dataset (Regressão
   Logística). Reportar a razão E_modelo / E_ref e o custo marginal da acurácia,
   (E_modelo − E_ref) / (F1_modelo − F1_ref) em J por ponto de F1; se ΔF1 ≤ 0, o
   modelo é marcado como dominado.
5. **Módulo `green_ml_score/contexts`:** `ExecutionContext` (nome, IC, WUE on-site,
   fator hídrico off-site, horário opcional) e uma função que avalia o conjunto
   modelo × contexto: GMS com limites sobre todas as configurações, τ de Kendall
   entre o ranking do GMS e o ranking por energia, e sensibilidade no simplex de pesos.
6. **Relatório por modelo** ("cartão ambiental") em Markdown.

Dados de contexto (integrante B escolhe e cita as fontes): IC por região e por hora
(ONS, Electricity Maps, EEA, EPA eGRID), WUE por provedor (relatórios de
sustentabilidade) e consumo hídrico por fonte de geração (Macknick et al., 2012).

## Semana 3 (12/10 – 18/10) — preparação concluída em 14/10

| Item | Estado |
|---|---|
| Roteiro da execução completa (`docs/execucao_completa.md`) | Feito |
| Script de validação com medidor (`experiments/meter_validation.py`), com análise da energia incremental ΔE = E_carga − E_repouso | Feito |
| `--quick-run` em breast_cancer, newsgroups e covtype com CodeCarbon real (14/10, notebook do Danilo) | Feito: os três concluídos sem erro; P₀ entre 15,3 e 16,7 W; a Regressão Logística foi a mais econômica nos três (0,4–0,6 J por treino) |
| Escolher a máquina de medição | Feito (14/10): notebook do Danilo (i5-1335U); `docs/ambiente_medicao.md` atualizado, com a configuração anterior (i5-1235U do Octávio) como histórico |
| Preencher `experiments/contexts/contexts.csv` com fontes | **Integrante B** |
| Validação com o medidor e execução completa (3 datasets) | **Dupla**, seguindo o roteiro |

## Semanas seguintes
- Semana 4 (19/10 – 25/10): análise, figuras e tabelas.
- Semana 5 (26/10 – 01/11): reescrita do texto.
- Folga (02/11 – 08/11): revisão final e entrega.
