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
- ~~Comprar o medidor de consumo de tomada~~ — descartado (sem custo); substituído pela validação via bateria (14/10).
- Registrar por escrito a mudança de objetivo com o orientador.

## Semana 2 (05/10 – 11/10): status (implementada em 14/10 e versionada)

| Item | Onde | Estado |
|---|---|---|
| 1. Aquecimento | `warm_up()` em `experiments/comparative_experiment.py`; `config.WARMUP`, `--no-warmup` | Feito |
| 2. Baseline de repouso | `measure_idle()`; `config.IDLE_BASELINE_S` (60 s; 10 s no quick-run), `--idle-seconds`; colunas `energy_net_kwh`, `energy_net_j`, `infer_energy_net_kwh`, `idle_power_w`, `train_session_s` | Feito |
| 3. Avisos de procedência | `provenance_warnings_for()` e `ProvenanceWarning` em `green_ml_score/collectors/codecarbon.py`; gravados em `run_metadata.json` e nos cartões | Feito |
| 4. Score relativo | `green_ml_score/scoring/relative.py`; `add_relative_scores()` pareado por semente; colunas `energy_ratio_ref`, `delta_f1_points`, `marginal_cost_j_per_f1_point`, `dominated` | Feito |
| 5. Módulo `contexts` | `green_ml_score/contexts/` (`ExecutionContext`, `load_contexts_csv`, `evaluate_configurations`, `kendall_tau_b`, `simplex_grid`); script `experiments/context_analysis.py` | Feito; `experiments/contexts/contexts.csv` preenchido em 17/10 (sete contextos, ver Semana 5, etapa 1) |
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
| Script de validação física sem custo (`experiments/energy_validation.py`): descarga da bateria via WMI; análise da energia incremental ΔE = E_carga − E_repouso | Feito; teste de 60 s funcionou nesta máquina |
| `--quick-run` em breast_cancer, newsgroups e covtype com CodeCarbon real (14/10, notebook do Danilo) | Feito: os três concluídos sem erro; P₀ entre 15,3 e 16,7 W; a Regressão Logística foi a mais econômica nos três (0,4–0,6 J por treino) |
| Escolher a máquina de medição | Feito (14/10): notebook do Danilo (i5-1335U); `docs/ambiente_medicao.md` atualizado, com a configuração anterior (i5-1235U do Octávio) como histórico |
| Preencher `experiments/contexts/contexts.csv` com fontes | Feito em 17/10 (sete contextos; ver Semana 5, etapa 1) |
| Validação física pela bateria e execução completa (3 datasets) | **Dupla**, seguindo o roteiro |

## Semana 4 (19/10 – 25/10) — código de análise pronto (14/10)

Validado sobre os quick-runs; quando a execução completa existir, basta
`python experiments/run_analysis.py`.

| Item | Onde |
|---|---|
| Orquestração (estatística + figuras + contextos, por dataset) | `experiments/run_analysis.py` |
| Estatística: Friedman/Wilcoxon-Holm também sobre a energia; score relativo; energia líquida e repetições; avisos de procedência | `experiments/statistical_analysis.py` → `stats_report.md` |
| Figuras: energia (bruta e líquida, log) e tempo; F1 × energia com fronteira de Pareto; GMS com nota de degeneração | `experiments/generate_results.py` → `docs/Results/<dataset>/<modo>/` |
| Tabela booktabs com N de sementes, IQR, E/E_ref e J por ponto de F1 | `summary_table.tex` |
| Figuras da pergunta de pesquisa: GMS modelo × contexto; τ_b e configuração vencedora no simplex de pesos | `experiments/context_analysis.py` (exige `contexts.csv` preenchido) |
| `sensitivity_analysis.py` removido (substituído pelo módulo `contexts`) | — |
| Gráfico de radar removido: com IC e WUE constantes, carbono e água repetiam o eixo de energia | — |

Observação da análise dos quick-runs: com contextos fictícios de teste, a
Regressão Logística venceu em todo o simplex, pois sua energia é 15–55× menor
que a dos demais modelos. Diferenças de IC entre regiões (até ~10×) só alteram a
seleção entre modelos de energia próxima; o efeito do contexto aparece sobretudo
na escolha da região/horário para um mesmo modelo. Isso deve orientar a redação
das novas hipóteses (semana 5).

## Semana 5 (26/10 – 01/11) — rascunho de revisão do texto (14/10)

`docs/revisao_texto_semana5.md`: inconsistências entre o `.docx` (05/10) e o código
(hardware, versões, protocolo de medição), objetivo geral alinhado à pergunta de
pesquisa, nova proposição analítica para contextos distintos (GMS = 1 − E·k,
verificada em `tests/test_contexts.py`), hipóteses H1–H4 refutáveis, limitações e
estrutura da Seção 8.

Decisões:
- **D1 — Datasets (decidido em 15/10/2026):** manter os três datasets; 20 Newsgroups
  é o estudo de caso principal, e Breast Cancer Wisconsin e Covertype são verificação
  de robustez em dados tabulares (título inalterado). A execução completa cobre os
  três; os trechos de texto estão no item 3.5 de `revisao_texto_semana5.md`.
- **D2 — Definição de "dominado" (decidido em 15/10/2026):** dominância de Pareto
  nos eixos F1 × energia, entre todos os modelos do mesmo dataset e semente (um
  modelo é dominado se outro tem F1 ≥ e energia ≤, com ao menos uma desigualdade
  estrita). Justificativa: coerência com a fronteira de Pareto das figuras e porque
  ΔF1 ≤ 0 com menor energia é compromisso, não dominância. A posição em relação à
  referência passa a ser registrada à parte (`position_vs_ref`).

### Etapa 1: análise de contextos, H3 e H4 (17/10/2026)

| Item | Estado |
|---|---|
| `contexts.csv` com 7 contextos: BR, FR e IN locais (PUE 1, WUE 0) e AWS São Paulo, Virgínia, Frankfurt e Estocolmo | Feito. IC: Ember 2025; água off-site: Reig et al. (WRI, 2020); PUE/WUE: fichas AWS 2025. Fonte e data de acesso por linha |
| Valores não confirmados | WUE de AWS Paris e Mumbai; IC horária do SIN (pico e vale). Em `contexts_pendentes.csv`, fora da análise |
| `run_analysis.py` nos 3 datasets | Feito; figuras `context_gms_heatmap` e `context_simplex` em `docs/Results/<dataset>/full/` |
| Correção: `generate_results.py` não achava `green_ml_score` fora de instalação editável | Feito (mesmo `sys.path.insert` dos demais scripts) |
| Interpretação de H3 e H4 e rascunho das Seções 8.4 e 8.5 | `revisao_texto_semana5.md`, item 8 |

Achados principais:
- τ_b tem patamar de 0,8819 só pelo desempate entre contextos de um mesmo modelo; "τ_b < 1"
  é verdadeiro por construção. Abaixo do patamar: 20 Newsgroups 0,798 e Breast Cancer
  0,786 com pesos 1/3 (14 e 16 pares invertidos entre modelos); Covertype fica no
  patamar (0,882) com pesos 1/3 e cai a 0,696 só com carbono. τ_b decresce com w_E nos
  três (Spearman 0,87 a 0,96). H3 confirmada no sentido reformulado.
- A Regressão Logística é a melhor configuração em 100 % do simplex nos três datasets,
  o que decorre de GMS = 1 − E·k (corolário, não hipótese). A condição
  E_j/E_i < k_r/k_s foi verificada sem violações em 203.742 comparações.
- Razão máxima de k entre contextos: 17,4 (só carbono), 8,3 (só água), 1,77 (pesos
  iguais); carbono e água ordenam os contextos em sentidos quase opostos (Brasil: IC
  baixa, água off-site de 18,6 L/kWh).
- Covertype: XGBoost (F1 0,862, 5,49 × energia da LR) supera a LR em outro contexto só
  com w_C ≥ 0,90 ou w_W ≥ 0,95 (11,3 % do simplex). H4 parcialmente confirmada; nos
  outros dois datasets a LR domina e H4 não se confirma.
- **D3. Redação de H3 e H4 (decidido em 17/10/2026):** adotada a redação
  reformulada (`revisao_texto_semana5.md`, item 8.1). H3: τ_b abaixo do patamar
  τ_b* = √(P_E/P) de desempate entre contextos de um mesmo modelo, decrescente com
  w_E. H4: a razão de fatores contextuais k_r/k_s supera a razão de energia entre
  modelos com F1 distinto. Justificativa: a redação anterior era verdadeira por
  construção (GMS = 1 − E·k) e não podia ser refutada. Aplicada à 5.6 (item 4) e aos
  rascunhos das 8.4, 8.5 e 8.6 (item 8), cuja síntese registra H3 confirmada nos três
  datasets (no Covertype, só com w_E < 0,4) e H4 parcialmente confirmada só no
  Covertype. O `.docx` ainda não foi alterado.

### Etapa 2: Seção 8 completa e conclusões (17/10/2026), FEITA

| Item | Estado |
|---|---|
| H1 e H2 na síntese 8.6 com números reais (Friedman, Wilcoxon-Holm, score relativo, Pareto D2) | Feito (`revisao_texto_semana5.md`, item 8.4) |
| Texto das Seções 8.1 a 8.6: médias ± desvios das 10 sementes, P₀, dominância, E/E_ref, J por ponto de F1 | Feito (item 9) |
| 20 Newsgroups: semente 42 anômala e análise de sensibilidade sem ela | Feito: conclusões inalteradas (Friedman χ²_F = 25,93, p = 9,8 × 10⁻⁶; Holm p = 0,023) |
| Covertype: lentidão a partir da semente 314 (MLP) e 1001 (RF, XGB), de 1,5 a 2 vezes | Verificado nos dados e tratado como limitação |
| Limitações: validação pela bateria (razão incremental 0,071 ± 0,068), energia líquida negativa, fontes de contexto, falta de IC horária | Feito (itens 5 e 8.5) |
| Seção 9 (Conclusões) | Feito (item 10) |

Vereditos: H1 confirmada nos três datasets; H2 confirmada no 20 Newsgroups e no Breast
Cancer e refutada no Covertype (XGBoost na fronteira com 5,1 × E_ref e +10,4 pontos
de F1); H3 confirmada nos três (no Covertype, só com w_E < 0,4); H4 parcialmente
confirmada, só no Covertype.

Pendente da dupla:
- ~~Registrar na 5.6 a operacionalização de H2~~ feito em 17/10 (decisão D4, abaixo).
- Passar os textos dos itens 4, 5, 8, 9 e 10 para o `.docx`.

- **D4. Operacionalização de H2 (decidido em 17/10/2026):** o custo marginal
  (E − E_ref) / ΔF1 não é definido para a referência, que tem ΔF1 = 0. H2 é testada
  pela dominância de Pareto (D2): um modelo dominado é compatível com H2; um não
  dominado só é compatível se E/E_ref ≥ 10. O limiar traduz "uma ordem de grandeza" da
  redação original, é da ordem da amplitude de IC entre regiões (17,4) e depende só de
  razões de energia, que a validação pela bateria indica serem confiáveis. Os
  vereditos não mudam para limiares entre 5,2 e 35,9. Registrada na 5.6 e citada na
  8.6 (`revisao_texto_semana5.md`, itens 4 e 8.4).
- Registrar com o orientador a mudança de objetivo (item 7 de `revisao_texto_semana5.md`).

## Painel interativo e artigo final (17/10/2026)

| Item | Estado |
|---|---|
| Painel interativo (GreenML Dashboard, Streamlit) em `app/` | Feito: tarefas T1 a T8 de `docs/plano_painel.md` (seis telas, testes de fumaça na CI, roteiro de demonstração e capturas em `docs/painel/`) |
| Artigo final no template da FAJ em `docs/artigo_final/` | `.docx` atualizado com a seção do painel (Figura 7); `.pdf` e `.doc` ainda são da versão anterior e precisam ser reexportados |

## Semanas seguintes
- Semana 5 (26/10 – 01/11): reescrita do texto.
- Folga (02/11 – 08/11): revisão final e entrega.
