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

### Pendente — tarefas para o Claude Code (integrante A)
1. `pip install -e .[dev,experiments]`; rodar `black .` e `ruff check --fix .`
   (o código novo não passou pelo black) e depois `pytest`. Corrigir falhas.
2. Confirmar que o CodeCarbon 3.2.6 preenche `final_emissions_data` ao final de
   `stop()`. Se não preencher, o fallback via CSV assume, mas registre o fato.
3. `--quick-run` nos três datasets (newsgroups e covtype exigem download).
4. Copiar do log de inicialização do CodeCarbon qual backend mede a CPU (RAPL,
   Intel Power Gadget ou estimativa por TDP) para `docs/ambiente_medicao.md`.
5. Revisar o diff da branch e fazer merge na `main`.

### Pendente — correções de integridade no texto (integrante B)
Corrigir agora apenas o que é **falso**; os números da Seção 8 serão substituídos
na semana 4.

| Seção (.docx) | Correção |
|---|---|
| Resumo / Abstract | Strubell et al. (2019): 1.438 **lbs** CO₂e (≈ 652 kg), não kg. Remover "resultados parciais" se o texto for a versão final |
| 3.3 e 4.7 | Remover "dimensões ortogonais"; inserir a demonstração de que, com IC e WUE constantes, GMS = E_norm para quaisquer pesos |
| 3.5 e 5 | IMDB/sentimentos → 20 Newsgroups, 2 categorias (rec.autos × sci.med), classificação de tópico; 6 → 4 modelos; remover BERT, DistilBERT, LSTM e GPU; hardware real (i5-1235U, Windows 11); CodeCarbon 3.2.6; divisão 80/20 |
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

## Semana 2 (05/10 – 11/10) — especificação

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

## Semanas seguintes
- Semana 3 (12/10 – 18/10): execução completa pela dupla + validação com o medidor.
- Semana 4 (19/10 – 25/10): análise, figuras e tabelas.
- Semana 5 (26/10 – 01/11): reescrita do texto.
- Folga (02/11 – 08/11): revisão final e entrega.
