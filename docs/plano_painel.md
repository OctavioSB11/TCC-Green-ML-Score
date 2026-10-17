# Plano de execução: GreenML Dashboard (painel interativo)

Decisão (17/10/2026): painel em Streamlit, rodando local, sobre a biblioteca
`green_ml_score` e os resultados já existentes em `experiments/results/*/full`.
Corresponde à camada 5 do framework (visualização e integração), descrita no artigo
como especificada. Nada do experimento é refeito e nenhum resultado é alterado.

Regras para todas as tarefas: código em `app/`, Python tipado, docstrings em
português, `ruff`, `black` e `pytest` passando antes de cada commit, um commit por
tarefa, nenhum número digitado à mão (tudo lido dos CSVs ou calculado pela
biblioteca).

## Visão geral

| # | Tarefa | Entrega | Depende de |
|---|---|---|---|
| T1 | Fundação | `app/` com esqueleto, camada de dados, extra `app` no `pyproject.toml`, teste da camada de dados | nada |
| T2 | Visão geral | página com cartões por modelo e rankings lado a lado | T1 |
| T3 | Qualidade × custo | gráfico F1 × energia interativo com fronteira de Pareto e custo marginal | T1 |
| T4 | Simulador de contexto | pesos ajustáveis, mapa das 7 regiões, GMS recalculado ao vivo, configuração vencedora | T1 |
| T5 | Cartão ambiental | ficha de um modelo com download | T1 |
| T6 | Avalie seu modelo (opcional) | upload de CSV e cálculo do GMS | T1, T3 |
| T7 | Qualidade e CI | testes de fumaça das páginas, README, CI cobrindo o `app/` | T2 a T5 |
| T8 | Apresentação | roteiro de demonstração de 3 min e capturas para os slides | T7 |

## Tarefas

### T1. Fundação
- Estrutura: `app/Home.py` (entrada), `app/views/` (uma página por tela),
  `app/data.py` (leitura e cache dos CSVs e do `contexts.csv`), `app/charts.py`
  (gráficos Plotly reutilizáveis), `app/theme.py` (cores e rótulos, reaproveitando
  `experiments/labels.py`).
- Dependências: novo extra `app = ["streamlit", "plotly"]` no `pyproject.toml`
  (sem pacotes de mapa extras: o mapa usa `plotly` `scatter_geo`).
- Teste: `tests/test_app_data.py` verifica que a camada de dados encontra os 3
  datasets, as 4 médias por modelo e os 7 contextos.
- Aceite: `streamlit run app/Home.py` abre a página inicial com o seletor de
  dataset; testes passando.

### T2. Visão geral
- Seletor de dataset (20 Newsgroups, Breast Cancer, Covertype).
- Cartões por modelo: F1, energia (mWh), carbono e água no contexto BR-local, GMS.
- Tabela de rankings por F1, energia e GMS lado a lado, destacando quando divergem
  (caso do Covertype).
- Aceite: os números batem com a Tabela 2 do artigo.

### T3. Qualidade × custo
- Gráfico F1 × energia (escala log), com barras de dispersão das 10 sementes,
  fronteira de Pareto e modelos dominados marcados.
- Ao passar o mouse: razão de energia frente à RL e custo marginal (J por ponto de F1).
- Opção de mostrar cada semente como ponto.
- Aceite: confere com a Tabela 3 e as Figuras 2 e 3 do artigo.

### T4. Simulador de contexto (ponto alto da demonstração)
- Três controles de peso (energia, carbono, água), normalizados para somar 1, e
  atalhos para os perfis do artigo (iguais, só carbono, só água, carbono priorizado
  0,2/0,5/0,3, água priorizada 0,3/0,2/0,5).
- Mapa-múndi com as 7 regiões coloridas pelo fator k; tamanho do marcador pelo GMS.
- Mapa de calor modelo × contexto atualizado ao vivo, τ_b frente à energia, número
  de pares invertidos e a configuração vencedora; aviso quando um modelo mais caro
  passa à frente de um mais econômico (condição E_j/E_i < k_r/k_s).
- Aceite: com peso total no carbono, no Covertype, o painel mostra o XGBoost em
  Estocolmo à frente da RL na Índia (99,6 contra 98,8), como na Figura 4.

### T5. Cartão ambiental
- Seleção de dataset, modelo e contexto; ficha com energia, CO₂, água, GMS, posição na
  fronteira e fontes dos fatores.
- Download em Markdown e CSV (PNG opcional, se não exigir dependência pesada).
- Aceite: o cartão gerado traz as fontes (Ember, WRI, AWS) e os mesmos números do
  painel.

### T6. Avalie seu modelo (opcional)
- Upload de um CSV com `modelo, energia_kwh, f1` (modelo baixável no próprio painel).
- O painel calcula o GMS junto com os modelos do estudo e mostra a posição na
  fronteira e no simulador de contexto.
- Aceite: um CSV de exemplo funciona e erros de formato geram mensagem clara.

### T7. Qualidade e CI
- Testes de fumaça das páginas com `streamlit.testing.v1.AppTest`.
- README com a seção "Painel interativo" (instalação com `pip install -e .[app]` e
  execução).
- CI instalando o extra `app` e rodando os testes do painel.

### T8. Apresentação
- Roteiro de 3 min: visão geral (rankings discordam no Covertype), qualidade × custo
  (custo marginal do XGBoost), simulador (peso no carbono troca o vencedor).
- Capturas de tela em alta resolução para os slides, como plano B.

## Decisões (17/10/2026)
1. T6 (Avalie seu modelo) **entra** no escopo.
2. Paleta: verde do GMS (#1B7F3B), com alto contraste para projetor; as cores dos
   modelos são as mesmas das figuras do artigo.
3. O painel roda **local** (`streamlit run app/Home.py`); publicar no Streamlit
   Community Cloud fica como opção avaliada na T8.

## Andamento
| Tarefa | Estado |
|---|---|
| T1 Fundação | Feita (17/10): `app/Home.py` com navegação e página inicial, `app/views/` (uma página por tarefa; o nome evita a detecção automática de `pages/` pelo Streamlit), `app/core/data.py` (dados sem Streamlit, testável na CI), `app/core/state.py` (cache), `app/core/theme.py`, `.streamlit/config.toml`, extra `app` no `pyproject.toml` e `tests/test_app_data.py` conferindo as Tabelas 2 a 5 e a Figura 4 do artigo |
| T2 Visão geral | Feita (17/10): página `app/views/1_visao_geral.py` com achados gerados dos dados, cartões por modelo (F1, energia, carbono, água e GMS, com selos de referência, fronteira de Pareto e dominância), seletor do contexto para carbono e água, abas de rankings por critério, energia por semente, comparação de métricas e tabela completa com download; `app/core/charts.py` (gráficos Plotly); testes `tests/test_app_charts.py` e novos casos em `tests/test_app_data.py`; CI instalando o extra `app` |
| T3 Qualidade × custo | Feita (17/10): página `app/views/2_qualidade_custo.py` com gráfico F1 × energia (sementes, medianas, fronteira de Pareto, dominados vazados e custo frente à RL ao passar o mouse), tabela de custo relativo (Tabela 3 do artigo), tabela do que cada critério escolheria (Tabela 4) e comparador de dois modelos; tabelas com vírgula decimal (`theme.br_table`); testes de fumaça de todas as páginas em `tests/test_app_pages.py` |
| T4 Simulador de contexto | Feita (17/10): página `app/views/3_simulador.py` com perfis de peso e controles deslizantes normalizados, aviso quando um modelo mais caro passa à frente da RL e quando a configuração vencedora muda, cartões de indicadores (vencedora, melhor e pior região, τ_b e pares invertidos frente aos pesos iguais), mapa-múndi com k relativo ao melhor, mapa de calor modelo × região, ranking das 28 configurações, pares invertidos, triângulo de pesos (como a Figura 5) e fatores das regiões; `data.simulate`, `data.tau_plateau` e `data.map_table`; aceite verificado em teste (Covertype, só carbono: XGBoost em Estocolmo 99,6 contra RL na Índia 98,8). O mapa de fundo do Plotly precisa de internet; os pontos aparecem sem conexão |
| T5 a T8 | Pendentes |
