# GreenML Score — contexto para o Claude Code

TCC em Ciência da Computação. O GreenML Score (GMS) é um framework de avaliação
ambiental de modelos de ML (energia, carbono, água). Pergunta de pesquisa revisada:
em que medida carbono e água, contextualizados por local e horário de execução,
alteram a seleção de configurações (modelo × região × horário) em relação a
critérios baseados só em energia ou tempo.

Plano de trabalho e status: `docs/revisao.md` (ler antes de qualquer tarefa).

## Painel interativo
`app/` (Streamlit, Python 3.11+): `app/Home.py` é a entrada, `app/views/` tem uma
página por tela e `app/core/` concentra dados, gráficos, cartão e envio de CSV sem
depender do Streamlit (testável na CI). Plano e decisões: `docs/plano_painel.md`.

## Ambiente de medição
Notebook do Danilo: Intel i5-1335U, 16 GB, Windows 11, CodeCarbon 3.2.6
(tracking_mode = machine). Detalhes e configuração anterior (i5-1235U do Octávio):
`docs/ambiente_medicao.md`.

## Regras
- Nunca editar à mão arquivos em `experiments/results/` nem logs do CodeCarbon;
  resultados só são produzidos pelos scripts.
- Nenhum fallback silencioso: falha de download, leitura ou medição lança exceção.
- Energia nos artefatos finais em J ou mWh; nunca arredondar kWh nos CSVs brutos.
- Mesmo paralelismo para todos os modelos (`config.N_JOBS`).
- Não executar o experimento completo: apenas `--quick-run` para validação.
  Execuções completas são feitas pela dupla, com a máquina dedicada.
- Antes de concluir qualquer tarefa: `black .`, `ruff check .` e `pytest` passando.
- Tipagem estática, PEP 8, docstrings em português, commits pequenos e descritivos.
- Painel: nenhum número digitado à mão; tudo é lido de `experiments/results/*/full`
  e `experiments/contexts/contexts.csv` ou calculado pela biblioteca `green_ml_score`.
- `tests/test_gms_properties.py` especifica propriedades matemáticas do GMS:
  não alterar esses testes para "fazer passar" uma mudança no scoring.
