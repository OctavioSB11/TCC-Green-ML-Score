# Revisão do texto — semana 5 (rascunho para a dupla)

Base: `docs/TCC_GreenML_Score.docx` (versão de 05/10/2026). Este documento **não**
altera o `.docx`; ele lista o que precisa mudar e propõe redação pronta para colar.
Os números da Seção 8 só podem ser escritos depois da execução completa
(`python experiments/run_analysis.py`); aqui ficam a estrutura e os textos que não
dependem deles.

Legenda: **[OBRIGATÓRIO]** = o texto hoje contradiz o código ou o protocolo;
**[RECOMENDADO]** = melhora o rigor perante a banca; **[DECISÃO]** = depende da dupla.

---

## 0. Estado das correções da semana 1

A versão de 05/10 já incorporou: Strubell em libras (≈ 652 kg); 20 Newsgroups com
duas categorias; quatro modelos; remoção de BERT/DistilBERT/LSTM/GPU do escopo
experimental (permanecem apenas no referencial teórico, o que é adequado); mWh;
8.2 sem "superioridade comprovada"; 8.3 reescrita; tabelas A/B/C removidas;
demonstração GMS = E_norm (4.3). **Nada pendente desta lista.**

---

## 1. Inconsistências entre texto e implementação

| # | Seção | Texto atual | Correção | Tipo |
|---|---|---|---|---|
| 1 | 3.5 e 5.4 | "CPU Intel Core i5-1235U (10 núcleos, 12 threads)" | "CPU Intel Core i5-1335U (10 núcleos, 12 threads), 16 GB de RAM" | [OBRIGATÓRIO] |
| 2 | 5.4 | "potência nominal padrão de 48 W (4 W por thread), atribuída porque o modelo de processador não consta de sua base de dados" | "potência de referência de 55 W, atribuída ao i5-1335U pela base de dados do CodeCarbon e correspondente à potência máxima em turbo do processador (a potência base é de 15 W)" | [OBRIGATÓRIO] |
| 3 | 5.4 | "a potência da memória RAM é considerada constante (20 W)" | "(10 W)" | [OBRIGATÓRIO] |
| 4 | 5.4 | "scikit-learn 1.6" | "scikit-learn 1.9" (versão instalada: 1.9.1; XGBoost 3.4.1; Python 3.13.2; CodeCarbon 3.2.6) | [OBRIGATÓRIO] |
| 5 | 5.4 | "a fase é repetida dez vezes (...) de modo a elevar a energia acumulada acima do ruído de medição" | substituir pelo parágrafo do item 3.2 abaixo (janela mínima, repouso, aquecimento) | [OBRIGATÓRIO] |
| 6 | 9 (4ª limitação) | "esse custo é diluído pelas dez repetições de cada fase" | "esse custo é diluído pela janela mínima de 30 s por fase (seção 5.4)" | [OBRIGATÓRIO] |
| 7 | 5.6 | H3 é consequência analítica, não hipótese empírica | substituir pelas hipóteses do item 4 | [OBRIGATÓRIO] |
| 8 | Resumo, 1.4, 3.2, 3.5, 5.2, 8 | Estudo de caso só com 20 Newsgroups | Incluir Breast Cancer e Covertype como verificação de robustez (decisão D1, item 3.5 abaixo); título inalterado | [OBRIGATÓRIO] |
| 9 | 1.4.1 | Objetivo geral não menciona a pergunta de pesquisa revisada (modelo × região × horário) | redação do item 2 | [OBRIGATÓRIO] |
| 10 | 3.6 | Validação só analítica + estudo de caso | incluir a validação física pela bateria (item 3.3) | [RECOMENDADO] |
| 11 | 5.5 | Métricas sem energia líquida, score relativo e repetições efetivas | redação do item 3.4 | [RECOMENDADO] |
| 12 | 6.4 | "fronteiras de Pareto entre F1-Score e GMS" | "entre F1-Score e energia" (com IC e WUE constantes, GMS e energia dão a mesma fronteira; a energia é mais interpretável) | [RECOMENDADO] |
| 13 | 4.4 | idem: "fronteira de Pareto bidimensional entre F1-Score e GMS" | manter, mas acrescentar: "em cenário de contexto único, equivalente à fronteira entre F1-Score e energia (seção 4.3)" | [RECOMENDADO] |

### Decisões da dupla

- **D1 — Datasets. DECIDIDO (15/10/2026):** manter os três datasets; o 20 Newsgroups
  é o estudo de caso principal e Breast Cancer Wisconsin e Covertype são verificação
  de robustez em dados tabulares. Título inalterado. Trechos de texto no item 3.5.
- **D2 — Definição de "dominado". DECIDIDO (15/10/2026):** dominância de Pareto nos
  eixos F1 × energia, entre todos os modelos do mesmo dataset e semente: um modelo é
  dominado se outro tem F1 maior ou igual e energia menor ou igual, sendo
  estritamente melhor em ao menos um dos dois. Coincide com a fronteira de Pareto
  das figuras; um modelo menos preciso porém mais econômico não é dominado (é um
  compromisso). Implementado em `pareto_dominated()` (`green_ml_score/scoring/relative.py`).
  Texto no item 3.4.
- **D3. Redação de H3 e H4. DECIDIDO (17/10/2026):** adotar a redação reformulada
  (item 8.1): H3 mede τ_b abaixo do patamar de desempate entre contextos de um mesmo
  modelo; H4 compara a razão de energia entre modelos competitivos com a razão dos
  fatores contextuais k. Já aplicada à 5.6 (item 4) e aos textos das 8.4 a 8.6 (item 8).

---

## 2. Objetivos (1.4)

**Avaliação crítica.** O objetivo geral atual descreve a métrica, mas não a pergunta
que o experimento responde. Como a seção 4.3 demonstra que, em contexto único, o GMS
se reduz à energia, a contribuição empírica do trabalho passa a ser a avaliação
contextualizada; o objetivo precisa dizê-lo.

**Proposta — 1.4.1 Objetivo Geral:**

> Propor, formular e avaliar o GreenML Score (GMS), métrica ambiental composta que
> integra consumo energético, emissões de carbono e pegada hídrica, e investigar em
> que medida a contextualização das emissões e do consumo hídrico pela região e pelo
> horário de execução altera a seleção de configurações (modelo × região × horário)
> em relação a critérios baseados apenas em energia ou tempo, por meio de um estudo
> de caso de classificação de textos com quatro modelos de famílias algorítmicas
> distintas.

**Proposta — acrescentar aos objetivos específicos (após o 4º):**

> Avaliar o conjunto de configurações modelo × contexto de execução, medindo a
> concordância entre as ordenações pelo GMS e pelo consumo energético (τ_b de
> Kendall) e a estabilidade da configuração selecionada sob diferentes pesos;
>
> Confrontar as estimativas de energia do CodeCarbon com uma referência física
> (descarga da bateria do equipamento de medição), quantificando sua fidelidade.

**Justificativa.** A banca avaliará se as conclusões respondem aos objetivos; um
objetivo que mencione apenas "demonstrar aplicabilidade" não sustenta resultado
empírico algum, porque a aplicabilidade é trivial.

---

## 3. Metodologia e protocolo

### 3.1 Nova proposição analítica (seção 4.3, após a demonstração existente)

**Avaliação crítica.** A seção 4.3 cobre o caso de contexto único. Falta caracterizar
o caso com contextos distintos, que é justamente o da pergunta de pesquisa. A
proposição abaixo foi verificada numericamente
(`tests/test_contexts.py::test_gms_order_equals_order_of_energy_times_context_factor`).

**Proposta de texto:**

> Considere agora um conjunto de configurações (i, r), em que o modelo i, com
> consumo E_i, é executado no contexto r, caracterizado por PUE_r, IC_r, WUE_r e pelo
> fator hídrico de geração EWIF_r, de modo que C_ir = E_i · PUE_r · IC_r e
> W_ir = E_i · (WUE_r + PUE_r · EWIF_r). Com limites de normalização tomados sobre
> todas as configurações, substituindo na definição do GMS:
>
> GMS_ir = 1 − E_i · k_r,  com  k_r = w_E / E_max + w_C · PUE_r · IC_r / C_max + w_W · (WUE_r + PUE_r · EWIF_r) / W_max.
>
> O fator k_r depende apenas do contexto e dos pesos. Decorrem duas consequências.
> (i) Para um mesmo modelo, o GMS ordena os contextos por k_r, isto é, a escolha da
> região e do horário é determinada pelos fatores ambientais ponderados. (ii) A
> configuração (j, s) supera (i, r) se e somente se E_j / E_i < k_r / k_s; portanto,
> o modelo selecionado só se altera em relação ao critério energético quando a razão
> entre os consumos dos modelos é menor que a razão entre os fatores contextuais.

**Justificativa.** Transforma a pergunta de pesquisa em condição verificável e
explica, de antemão, por que um modelo dezenas de vezes mais econômico continuará
vencendo em qualquer contexto realista (razões de IC entre regiões ficam em torno de
uma ordem de grandeza). Evita que a banca interprete esse resultado como falha da
métrica.

### 3.2 Protocolo de medição (substitui o 3º parágrafo de 5.4)

> Cada modelo é avaliado com dez sementes (42, 123, 2024, 7, 314, 1001, 2718, 4242,
> 8080 e 9999). Antes da primeira semente de cada dataset, mede-se o equipamento em
> repouso por 60 s para estimar a potência ociosa P₀, e cada modelo executa um
> treinamento e uma inferência não medidos (aquecimento), descartados. Para cada
> semente, a ordem dos modelos é sorteada, e as fases de treinamento e de inferência
> são medidas separadamente, cada uma em sua própria sessão do CodeCarbon. Em cada
> sessão, a fase é repetida ao menos dez vezes e até ocupar uma janela mínima de 30 s
> (no treinamento, sempre a partir de uma cópia não treinada do mesmo estimador), e
> reporta-se a energia por repetição. A janela mínima foi adotada após a execução de
> validação mostrar que sessões de 1 a 2 s são dominadas pelo custo fixo de
> inicialização e encerramento do CodeCarbon: com uma única repetição, o treinamento
> da Regressão Logística registrava cerca de 17 J; com a janela mínima, 0,4 J. Além da
> energia bruta, reporta-se a energia líquida de repouso, E − P₀ · t, em que t é a
> duração da sessão. As métricas são reportadas por mediana e intervalo interquartil,
> além de média e desvio padrão; a comparação entre modelos utiliza o teste de
> Friedman, com execuções pareadas por semente, seguido de testes de Wilcoxon
> pareados com correção de Holm, aplicados à energia de treinamento.

### 3.3 Validação física (acrescentar ao final de 3.6)

> Como o ambiente de medição não dispõe de contadores de energia do hardware, as
> estimativas do CodeCarbon são confrontadas com uma referência física: a descarga
> da bateria do próprio equipamento, lida pela interface WMI do sistema operacional
> (potência de descarga, em mW, e carga restante, em mWh). Com o carregador
> desconectado, alternam-se fases de repouso e de carga de 10 min, em três
> tentativas, e compara-se a energia incremental da carga (carga − repouso), na qual
> se cancelam componentes que o CodeCarbon não observa, como tela e rede. A razão
> entre a energia incremental estimada e a medida indica se o CodeCarbon captura o
> custo da carga computacional, que é o que o GMS compara entre modelos.

### 3.4 Métricas (acrescentar a 5.5)

> (d) Métricas relativas à referência: para cada semente, a razão de energia
> E / E_ref e o custo marginal (E − E_ref) / ΔF1, em joules por ponto percentual de
> F1, tomando a Regressão Logística como referência; o custo marginal só é definido
> quando o modelo é mais preciso que a referência (ΔF1 > 0). Adicionalmente, em cada
> semente, um modelo é considerado dominado, no sentido de Pareto, quando outro
> modelo apresenta F1-Score maior ou igual e consumo energético menor ou igual, sendo
> estritamente melhor em ao menos um dos critérios; reporta-se a fração das sementes
> em que cada modelo é dominado. Um modelo menos preciso porém mais econômico que os
> demais não é dominado, pois representa um compromisso legítimo entre qualidade
> preditiva e custo ambiental.
>
> (e) Métricas de medição: energia líquida de repouso, número efetivo de repetições
> por fase e avisos de procedência (modo de rastreamento da máquina inteira, potência
> de RAM constante e fração da energia atribuída à RAM superior a 50 %).

### 3.5 Datasets: estudo de caso principal e verificação de robustez (decisão D1)

**Avaliação crítica.** Um único dataset de texto, pequeno e esparso, limita a
validade externa: a ordenação energética dos modelos pode depender da
representação (TF-IDF esparso) e do tamanho da amostra. Dois datasets tabulares de
escalas distintas permitem verificar se as conclusões de H1–H4 se mantêm quando
muda a natureza dos dados, sem desviar o foco do estudo de caso de texto. Os números
abaixo foram conferidos nos dados carregados pelo código (`experiments/dataset.py`).

**Resumo (após "...estudo de caso de classificação de textos (20 Newsgroups)"):**

> ..., complementado por dois conjuntos tabulares (Breast Cancer Wisconsin e
> Covertype) utilizados como verificação de robustez, ...

Abstract: "..., complemented by two tabular datasets (Breast Cancer Wisconsin and
Covertype) used as a robustness check, ...".

**1.4.2, 4º objetivo específico — nova redação:**

> Aplicar o GMS em um estudo de caso de classificação de textos (20 Newsgroups),
> comparando quatro modelos representativos (Regressão Logística, Random Forest,
> XGBoost e rede neural MLP) sob protocolo experimental padronizado, e verificar a
> robustez dos resultados em dois conjuntos de dados tabulares de escalas distintas
> (Breast Cancer Wisconsin e Covertype);

**3.2, acrescentar ao final do último parágrafo:**

> Para verificar se as conclusões dependem da natureza dos dados, o mesmo protocolo
> é aplicado, como verificação de robustez, a dois conjuntos tabulares de escalas
> distintas, descritos na seção 5.2.

**3.5, 1º parágrafo — substituir "no dataset 20 Newsgroups, restrito a duas categorias (rec.autos e sci.med)" por:**

> no dataset 20 Newsgroups, restrito a duas categorias (rec.autos e sci.med), e, como
> verificação de robustez, nos conjuntos tabulares Breast Cancer Wisconsin e
> Covertype (seção 5.2),

e "(todos sobre representação TF-IDF)" por "(sobre representação TF-IDF no caso
textual e sobre atributos padronizados nos casos tabulares)".

**5.2, acrescentar após o 2º parágrafo (novo subtítulo opcional "Conjuntos de verificação de robustez"):**

> Para a verificação de robustez, utilizam-se dois conjuntos tabulares de
> classificação binária, também obtidos pelo scikit-learn. O Breast Cancer Wisconsin
> (Diagnostic) contém 569 amostras com 30 atributos numéricos extraídos de imagens de
> punção aspirativa, rotuladas como malignas (212) ou benignas (357). O Covertype
> descreve 581.012 parcelas de terreno por 54 atributos cartográficos; o problema é
> binarizado como "Lodgepole Pine" (classe 2) contra as demais espécies, e uma
> subamostra estratificada de 50.000 parcelas é extraída com semente fixa (42),
> resultando em 24.380 exemplos positivos e 25.620 negativos. Os dois conjuntos
> diferem do estudo de caso principal em natureza (atributos densos em vez de texto
> esparso) e cobrem escalas distintas, de algumas centenas a dezenas de milhares de
> amostras. Em ambos, a divisão treino-teste (80-20, estratificada) e as sementes são
> as mesmas do estudo principal, e os atributos são padronizados (média zero e
> variância unitária) com parâmetros estimados exclusivamente no conjunto de
> treinamento.

**5.3, 1º parágrafo — substituir "Todos utilizam a mesma representação TF-IDF" por:**

> Em cada dataset, todos utilizam a mesma representação de entrada (TF-IDF no caso
> textual; atributos padronizados nos casos tabulares)

**Justificativa.** A banca tende a questionar a generalização de conclusões obtidas
em um único conjunto. Apresentar os tabulares explicitamente como verificação de
robustez, e não como estudos de caso paralelos, preserva o foco (e o título) do
trabalho e transforma a eventual concordância entre datasets em evidência adicional
para H1–H4; uma eventual discordância deve ser reportada como resultado, não omitida.

---

## 4. Hipóteses (substitui 5.6)

**Avaliação crítica.** A H3 atual é teorema (seção 4.3), não hipótese: não pode ser
refutada pelos dados. As hipóteses devem (i) ser refutáveis, (ii) ter teste
estatístico definido antes da execução e (iii) responder à pergunta de pesquisa.
Os limiares abaixo derivam da literatura (perfis algorítmicos da seção 2.3) e da
proposição do item 3.1 — **não** dos quick-runs, que servem apenas de validação
técnica e não devem ser citados como evidência.

**Proposta:**

> Com base na literatura revisada e na análise da seção 4.3, formulam-se quatro
> hipóteses, avaliadas com nível de significância de 5 %:
>
> **H1 (eficiência da referência):** em cada dataset, a Regressão Logística
> apresenta energia de treinamento inferior à de cada um dos demais modelos (teste
> de Friedman seguido de Wilcoxon pareado com correção de Holm).
>
> **H2 (retorno decrescente):** os modelos de maior custo computacional não
> apresentam ganho de F1-Score proporcional ao consumo: nenhum deles integra a
> fronteira de Pareto entre F1-Score e energia, ou, se a integra, o faz com custo
> marginal superior ao da referência em ao menos uma ordem de grandeza.
>
> **H3 (contexto e ordenação):** no conjunto de configurações modelo × contexto, há
> pares de configurações de modelos distintos em que o modelo de maior consumo
> energético obtém GMS superior, isto é, τ_b fica abaixo do valor que se obtém apenas
> com o desempate entre contextos de um mesmo modelo, τ_b* = √(P_E / P), em que P é o
> número de pares de configurações e P_E o número de pares não empatados na energia
> (0,8819 com quatro modelos e sete contextos), e a quantidade desses pares cresce à
> medida que o peso da energia diminui.
>
> **H4 (contexto e seleção):** para pares de modelos com F1-Score distinto, a razão
> entre os fatores contextuais de regiões reais (k_r/k_s) supera a razão entre seus
> consumos energéticos, de modo que a seleção do modelo passa a depender da região e
> do horário em que cada um seria executado.
>
> Registra-se que a versão anterior deste trabalho previa o XGBoost entre os modelos
> de maior GMS; a execução exploratória (seção 8.1) refutou essa expectativa.

**Redação de H3 e H4 adotada pela dupla em 17/10/2026 (decisão D3, item 8.1).** A
redação anterior ("τ_b < 1" e "a configuração de maior GMS utiliza o modelo de menor
energia") era verdadeira por construção, pela proposição do item 3.1, e não podia ser
refutada pelos dados.

**Justificativa.** H1 e H2 respondem à dimensão Green AI clássica (custo × qualidade)
com testes já implementados (`statistical_analysis.py`). H3 e H4 respondem à pergunta
de pesquisa revisada e são produzidas por `context_analysis.py` (τ_b no simplex e
configurações) e pela contagem de pares invertidos entre modelos. Ambas são
refutáveis: H3 falha se τ_b permanecer no patamar τ_b* em todo o simplex; H4 falha se,
para os modelos competitivos, a razão de energia superar a maior razão de k entre os
contextos reais em todos os pesos.

---

## 5. Limitações (Seção 9) — redação proposta

Substituir o 3º e o 4º parágrafos de limitações por:

> Terceiro, no ambiente de medição deste trabalho, a energia é estimada pelo
> CodeCarbon a partir da carga da CPU, sobre uma potência de referência de 55 W
> (superior à potência base do processador, de 15 W), e a potência da memória RAM é
> tratada como constante (10 W); por isso, a energia de RAM é proporcional ao tempo
> de execução e responde por mais da metade da energia estimada nas fases curtas. A
> validação contra a descarga da bateria (seção 3.6) quantifica o desvio dessas
> estimativas, [inserir razão incremental média ± desvio após a validação]. Quarto, o
> CodeCarbon foi executado no modo de rastreamento da máquina inteira, de modo que
> processos concorrentes entram na medição; o protocolo mitiga esse efeito com
> equipamento dedicado, repouso medido (P₀) e ordem de execução sorteada, mas não o
> elimina. Quinto, cada sessão de medição inclui um custo fixo de inicialização e
> encerramento, diluído pela janela mínima de 30 s por fase.

---

## 6. Estrutura sugerida para a Seção 8 (após a execução completa)

Renomear para **"8 RESULTADOS E DISCUSSÃO"** e mover a execução exploratória para um
parágrafo curto em 8.1 (ou apêndice). Cada subseção aponta o artefato gerado.

| Subseção | Conteúdo | Artefato |
|---|---|---|
| 8.1 Validação da medição | P₀ (por dataset); razão CodeCarbon/bateria (absoluta e incremental); avisos de procedência | `experiments/results/energy_validation/*.md`; `stats_report.md` (seção "Medição") |
| 8.2 Desempenho e consumo no 20 Newsgroups (H1) | Tabela (acurácia, F1, energia bruta e líquida, tempo, GMS); Friedman/Wilcoxon sobre energia | `docs/Results/newsgroups/full/summary_table.tex`, `energy_time.png`, `stats_report.md` |
| 8.3 Custo marginal e Pareto no 20 Newsgroups (H2) | F1 × energia com fronteira; E/E_ref e J por ponto de F1 | `docs/Results/newsgroups/full/pareto_energy_f1.png`, `stats_report.md` (seção "Score relativo") |
| 8.4 Contextos de execução no 20 Newsgroups (H3, H4) | Heatmap GMS modelo × contexto; τ_b no simplex; configuração vencedora; verificação da condição E_j/E_i < k_r/k_s | `context_gms_heatmap.png`, `context_simplex.png`, `context_report.md` |
| 8.5 Verificação de robustez (Breast Cancer e Covertype) | Uma tabela compacta por dataset (F1, energia mediana, E/E_ref, resultado de Friedman) e uma tabela-síntese indicando, para H1–H4, se o resultado do 20 Newsgroups se repete; figuras detalhadas em apêndice | `docs/Results/breast_cancer/full/`, `docs/Results/covtype/full/` (`summary_table.tex`, `pareto_energy_f1.png`, `context_report.md`) |
| 8.6 Síntese | Tabela de hipóteses: confirmada/refutada no estudo principal e nos de robustez, estatística e p-valor | — |

Figura `gms_barchart.png`: usar só se necessário, com a nota de que, em contexto
único, ela reproduz o ranking de energia.

---

## 7. Pendências que bloqueiam o texto final

1. ~~`experiments/contexts/contexts.csv` preenchido com fontes~~ feito em 17/10
   (sete contextos; resultados no item 8). Pendentes: WUE de AWS Paris e Mumbai e IC
   horária do SIN (`experiments/contexts/contexts_pendentes.csv`).
2. Validação pela bateria (≈ 1 h) e execução completa (≈ 4–6 h), conforme
   `docs/execucao_completa.md`.
3. ~~Decisões D1 e D2~~ — ambas decididas em 15/10.
4. Registrar por escrito, com o orientador, a mudança de objetivo (item 2).

---

## 8. Contextos de execução: resultados de H3 e H4 (rascunho das 8.4, 8.5 e 8.6)

Base: `contexts.csv` de 17/10/2026 (sete contextos), energia de treinamento mediana
das dez sementes e `python experiments/run_analysis.py`. Artefatos por dataset:
`experiments/results/<dataset>/full/context_report.md`,
`context_configurations.csv`, `context_sensitivity.csv` e as figuras
`docs/Results/<dataset>/full/context_gms_heatmap.png` e `context_simplex.png`.

### 8.1 Avaliação crítica do orientador

1. **A primeira parte de H3 é verdadeira por construção.** O ranking por energia
   empata os sete contextos de um mesmo modelo (a energia de TI não depende da região),
   e o GMS desempata sempre que w_E < 1. Mesmo sem nenhuma inversão entre modelos,
   τ_b = √(294/378) = 0,8819 (28 configurações, 378 pares, 84 empatados na energia).
   Portanto "τ_b < 1" não testa nada; a quantidade informativa é τ_b **abaixo** desse
   patamar, isto é, a existência de pares discordantes entre modelos diferentes.
2. **H4, na redação atual, é corolário, não hipótese.** Como GMS_ir = 1 − E_i · k_r, a
   configuração de maior GMS é sempre (modelo de menor energia, contexto de menor k),
   quaisquer que sejam os fatores. Os dados confirmam (Regressão Logística em 100 % do
   simplex nos três datasets), mas não poderiam refutar. A verificação da condição
   E_j/E_i < k_r/k_s em todos os pares e pesos (294 pares × 231 pontos × 3 datasets,
   203.742 comparações, zero violações) atesta a implementação, não um fenômeno.
3. **O conteúdo empírico está na comparação de razões.** A pergunta refutável é se as
   razões de fatores entre contextos reais superam as razões de energia entre modelos
   competitivos. Com os contextos adotados, a razão máxima de k é 17,4 (só carbono,
   Índia local / AWS Estocolmo), 8,3 (só água, AWS São Paulo / AWS Frankfurt) e apenas
   1,77 com pesos iguais. A combinação reduz a amplitude porque carbono e água ordenam
   os contextos em sentidos quase opostos (os contextos brasileiros têm a 3ª e a 4ª
   menor IC e a maior água off-site, 18,6 L/kWh, por evaporação em reservatórios).
4. **Assimetria local × nuvem.** Os contextos locais têm PUE = 1 e WUE = 0 por
   definição, o que os favorece; FR-local vence em 78 % do simplex por isso. O texto
   deve apresentar os dois grupos separadamente ou declarar essa vantagem.
5. **Artefato no vértice w_E = 1.** Ali todos os contextos empatam; o "vencedor"
   BR-local da figura do simplex é apenas o primeiro da lista. Mencionar na legenda.

**Redação de H3 e H4 adotada em 17/10/2026 (decisão D3; já aplicada à 5.6, item 4):**

> **H3 (contexto e ordenação):** no conjunto de configurações modelo × contexto, há
> pares de configurações de modelos distintos em que o modelo de maior consumo
> energético obtém GMS superior, isto é, τ_b fica abaixo do valor que se obtém apenas
> com o desempate entre contextos de um mesmo modelo, τ_b* = √(P_E / P), em que P é o
> número de pares de configurações e P_E o número de pares não empatados na energia
> (0,8819 com quatro modelos e sete contextos), e a quantidade desses pares cresce à
> medida que o peso da energia diminui.
>
> **H4 (contexto e seleção):** para pares de modelos com F1-Score distinto, a razão
> entre os fatores contextuais de regiões reais (k_r/k_s) supera a razão entre seus
> consumos energéticos, de modo que a seleção do modelo passa a depender da região e
> do horário em que cada um seria executado.

### 8.2 Resultados por dataset

Energia mediana de treinamento (mWh) / F1 macro mediano:

| Dataset | LR | RF | XGB | MLP |
|---|---|---|---|---|
| 20 Newsgroups | 0,103 / 0,936 | 9,58 / 0,899 | 20,2 / 0,867 | 24,7 / 0,934 |
| Breast Cancer | 0,018 / 0,967 | 0,873 / 0,953 | 0,772 / 0,958 | 0,307 / 0,929 |
| Covertype | 1,05 / 0,759 | 36,6 / 0,893 | 5,79 / 0,862 | 91,2 / 0,850 |

| Indicador | 20 Newsgroups | Breast Cancer | Covertype |
|---|---|---|---|
| τ_b com pesos 1/3 | 0,798 | 0,786 | 0,882 (= patamar) |
| τ_b no simplex: mín / mediana | 0,582 / 0,786 | 0,576 / 0,780 | 0,696 / 0,882 |
| τ_b só carbono / só água | 0,582 / 0,642 | 0,576 / 0,648 | 0,696 / 0,756 |
| Spearman (w_E, τ_b) | 0,955 | 0,939 | 0,874 |
| Pares invertidos entre modelos, pesos 1/3 | 14 | 16 | 0 |
| Fração do simplex com ao menos uma inversão | 92,2 % | 96,1 % | 45,0 % |
| Melhor configuração | LR em 100 % do simplex | LR em 100 % | LR em 100 % |
| Menor razão de energia contra a LR | 92,9 (RF) | 17,1 (MLP) | 5,49 (XGB) |
| A LR é superada em algum par? | nunca | só no vértice w_C = 1 (0,4 %) | sim, em 11,3 % do simplex (XGB) |

**H3.** Confirmada nos três datasets, na redação adotada (D3): τ_b cai abaixo do patamar
de 0,8819 e decresce monotonicamente com o peso da energia (Spearman de 0,87 a 0,96),
com o mínimo no vértice só carbono. A intensidade do efeito depende das razões de
energia entre modelos adjacentes: no 20 Newsgroups (MLP/XGB = 1,22) e no Breast Cancer
(RF/XGB = 1,13) há inversões já com pesos iguais; no Covertype, cujas razões adjacentes
são maiores (5,49; 6,31; 2,49), τ_b permanece no patamar para w_E ≥ 0,4 e só cai quando
carbono e água dominam.

**H4.** No 20 Newsgroups e no Breast Cancer, a Regressão Logística é simultaneamente o
modelo mais econômico e o de maior F1; nenhum contexto a supera (no Breast Cancer, a
MLP só a ultrapassa no vértice só carbono, porque 17,11 < 17,40). As inversões ocorrem
entre modelos já dominados, sem consequência prática para a seleção: H4 não se
confirma nesses dois datasets. No **Covertype** há compromisso real: o XGBoost ganha
10,4 pontos de F1 sobre a LR com 5,49 vezes a energia, e o Random Forest ganha 13,5
pontos com 34,7 vezes. A condição de razões é satisfeita para XGB × LR apenas quando
w_C ≥ 0,90 no eixo energia-carbono (ou w_W ≥ 0,95 no eixo energia-água), isto é, em
11,3 % do simplex. Em carbono: o XGBoost treinado em AWS Estocolmo emite 0,223 mg CO2e
por treinamento, contra 0,707 mg da LR na rede indiana; o Random Forest em Estocolmo
(1,41 mg) emite menos que o XGBoost na Índia (3,88 mg), pois 6,31 < 17,4. Em água, a
ordem se inverte: o XGBoost em Estocolmo consome 38 µL, contra 3,6 µL da LR na Índia.
H4 é, portanto, parcialmente confirmada: o contexto pode alterar a seleção somente
quando a diferença de energia entre modelos competitivos é inferior a cerca de uma
ordem de grandeza e quando o critério privilegia um único recurso (carbono ou água);
com pesos equilibrados (razão máxima de k = 1,77), a seleção não muda em nenhum
dataset.

**Escolha da região (mesmo modelo).** O contexto vencedor depende dos pesos: FR-local
em 78,4 % do simplex, AWS Estocolmo ao longo do eixo energia-carbono (8,7 %) e AWS
Frankfurt junto ao eixo energia-água (12,6 %). Esse é o efeito do contexto mais
robusto do estudo e independe do dataset, pois decorre só de k_r.

### 8.3 Proposta de texto para as Seções 8.4 (20 Newsgroups) e 8.5 (robustez)

> A avaliação contextualizada considerou sete contextos de execução: o próprio
> equipamento de medição conectado às redes do Brasil, da França e da Índia (PUE
> unitário e sem consumo hídrico local) e quatro regiões de nuvem com PUE e WUE
> publicados pelo provedor para 2025 (São Paulo, Virgínia do Norte, Frankfurt e
> Estocolmo). As intensidades de carbono provêm da Ember (2025) e os fatores hídricos
> de geração, de Reig et al. (2020). Entre esses contextos, o fator de carbono varia
> 17,4 vezes e o fator hídrico, 8,3 vezes, em sentidos quase opostos: os contextos
> brasileiros estão entre os de menor intensidade de carbono e são os de maior consumo
> hídrico por kWh.
>
> No 20 Newsgroups, a concordância entre o ranking do GMS e o ranking energético foi
> τ_b = 0,798 com pesos iguais, abaixo do valor de 0,882 atribuível apenas ao desempate
> entre contextos de um mesmo modelo, e caiu para 0,582 quando todo o peso recaiu
> sobre o carbono, o que confirma H3: há pares de configurações em que o modelo de
> maior consumo obtém GMS superior, e seu número cresce à medida que o peso da
> energia diminui (correlação de Spearman entre w_E e τ_b de 0,955). As inversões,
> contudo, envolveram apenas modelos de consumo próximo
> e desempenho inferior ao da referência (MLP e XGBoost, razão de energia de 1,22); a
> Regressão Logística, 93 vezes mais econômica que o modelo seguinte, permaneceu na
> configuração de maior GMS em todo o simplex de pesos. Como a razão de energia entre
> a referência e qualquer modelo alternativo (no mínimo 92,9) supera a maior razão
> entre fatores contextuais (17,4), H4 não se confirma neste conjunto. Resultado
> análogo foi observado no Breast Cancer Wisconsin (τ_b = 0,786 com pesos iguais;
> razão mínima de energia de 17,1, superada apenas no vértice de peso exclusivo no
> carbono, em que a razão de k é 17,4).
>
> O Covertype foi o único conjunto com compromisso efetivo entre qualidade preditiva e
> consumo: o XGBoost elevou o F1-Score de 0,759 para 0,862 com 5,5 vezes a energia da
> Regressão Logística. Nesse caso, o treinamento do XGBoost em Estocolmo emitiu cerca
> de um terço do carbono do treinamento da Regressão Logística na rede indiana, de modo
> que, sob critério exclusivamente de carbono, a escolha do modelo passa a depender de
> onde cada um é executado. Com pesos equilibrados, entretanto, a razão máxima entre
> fatores contextuais foi de 1,77, insuficiente para alterar a seleção, e τ_b
> permaneceu no patamar de 0,882; a condição de H4 só se verificou com peso do
> carbono de ao menos 0,90 ou peso da água de ao menos 0,95 (11,3 % do simplex).
> H3 confirmou-se também neste conjunto, porém apenas com w_E < 0,4 (mínimo de
> 0,696 no vértice do carbono), e H4 confirmou-se parcialmente. Conclui-se que
> o contexto de execução altera de forma robusta a escolha da região para um mesmo
> modelo, mas só altera a escolha do modelo quando as diferenças de consumo entre
> alternativas competitivas são inferiores à amplitude dos fatores contextuais, o que,
> neste estudo, ocorreu apenas no Covertype e sob ponderações extremas.

**Justificativa acadêmica.** A reformulação separa o que é consequência matemática
(desempate entre contextos, vencedor global) do que depende dos dados (razões de
energia entre modelos competitivos frente às razões de fatores de regiões reais). A
banca tende a perguntar por que τ_b < 1 "confirma" algo; o patamar de 0,8819 responde
de antemão. O Covertype passa a ser a evidência central de H4, e os outros dois
datasets mostram o caso, igualmente informativo, em que a referência domina.

### 8.4 Proposta para a Seção 8.6 (síntese das hipóteses)

H3 e H4 são avaliadas sobre as energias medianas das dez sementes e sobre todo o
simplex de pesos (passo 0,05, 231 pontos); por serem determinísticas dada a mediana,
reportam-se estatísticas descritivas (τ_b, número de pares invertidos, fração do
simplex) em vez de p-valor. H1 e H2 vêm de `stats_report.md` (Friedman/Wilcoxon-Holm
e Pareto) e devem ser preenchidas pela dupla.

| Hipótese | 20 Newsgroups (principal) | Breast Cancer (robustez) | Covertype (robustez) |
|---|---|---|---|
| H1 | [preencher: Friedman e Wilcoxon-Holm] | [preencher] | [preencher] |
| H2 | [preencher: fronteira e custo marginal] | [preencher] | [preencher] |
| H3 | Confirmada: τ_b = 0,798 com pesos iguais (patamar 0,882); mín. 0,582; 14 pares invertidos; Spearman(w_E, τ_b) = 0,955 | Confirmada: τ_b = 0,786; mín. 0,576; 16 pares; Spearman 0,939 | Confirmada só com w_E < 0,4: τ_b = 0,882 (no patamar) com pesos iguais; mín. 0,696; Spearman 0,874 |
| H4 | Não confirmada: razão mínima de energia contra a LR de 92,9, acima da razão máxima de k (17,4); LR melhor em 100 % do simplex | Não confirmada: razão de 17,1 superada só no vértice w_C = 1 (0,4 % do simplex) | Parcialmente confirmada: XGB (F1 0,862, 5,49 × E) supera a LR de outro contexto em 11,3 % do simplex (w_C ≥ 0,90 ou w_W ≥ 0,95); nunca com pesos iguais (razão de k = 1,77) |

> Em síntese, a contextualização por região alterou a ordenação das configurações
> nos três conjuntos de dados (H3), mas alterou a seleção do modelo apenas no
> Covertype, único caso com compromisso efetivo entre F1-Score e consumo, e apenas sob
> ponderações concentradas em carbono ou em água (H4, parcial). A escolha da região
> para um mesmo modelo, por sua vez, dependeu dos pesos em todos os casos.

### 8.5 Limitações específicas desta análise

- A energia é a de treinamento (mediana de dez sementes); a inferência não entra no
  GMS contextual.
- Os contextos locais de França e Índia são contrafactuais (o mesmo equipamento ligado
  a outra rede). AWS Paris e Mumbai ficaram de fora por falta de WUE publicado.
- A IC é média anual de 2025, baseada na geração; não considera importações entre
  regiões (relevante para a Virgínia, integrada à PJM) nem variação horária.
- O fator hídrico off-site do Brasil é dominado pela evaporação de reservatórios,
  cuja atribuição integral à geração é discutida na literatura (Macknick et al.,
  2012); recomenda-se registrar essa ressalva.
- Não há contexto horário: falta IC horária oficial do SIN (ver pendências).
