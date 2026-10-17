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
- **D4. Operacionalização de H2. DECIDIDO (17/10/2026):** como o custo marginal não é
  definido para a referência (ΔF1 = 0), um modelo dominado é compatível com H2 e um
  não dominado só o é se E/E_ref ≥ 10 ("uma ordem de grandeza" da redação original).
  Registrada na 5.6 (item 4) e citada na síntese 8.6 (item 8.4).

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
> marginal superior ao da referência em ao menos uma ordem de grandeza. Como o custo
> marginal, (E − E_ref) / ΔF1, não é definido para a própria referência, que tem
> ΔF1 = 0, a comparação com ela é feita pela razão de energia: H2 é testada, em cada
> dataset e semente, classificando cada modelo alternativo segundo a dominância de
> Pareto entre F1-Score e energia. Um modelo dominado é compatível com H2; um modelo
> não dominado só é compatível com H2 se E/E_ref ≥ 10. A hipótese é refutada em um
> dataset quando algum modelo integra a fronteira com razão de energia mediana
> inferior a 10.
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

**Operacionalização de H2 registrada pela dupla em 17/10/2026 (decisão D4).** A
redação original comparava o custo marginal do modelo com o "da referência", que não
existe: com ΔF1 = 0, o quociente (E − E_ref) / ΔF1 não é definido. A regra acima
substitui essa comparação pela razão de energia E/E_ref, sem alterar o conteúdo da
hipótese. O limiar de 10 foi escolhido por três motivos: (i) é a tradução literal de
"uma ordem de grandeza", já presente na redação original, e não um valor ajustado aos
resultados; (ii) é da mesma ordem que a amplitude das intensidades de carbono entre
regiões (item 3.1; razão máxima de 17,4 entre os contextos adotados), de modo que um
modelo dez vezes mais custoso dificilmente é compensado pela escolha da região; (iii)
depende apenas de uma razão de energias, que a validação pela bateria indica ser
confiável mesmo quando os valores absolutos não o são. Registra-se, por transparência,
que a regra foi explicitada após a execução; por isso, reporta-se também sua
sensibilidade: com as razões medianas, qualquer limiar entre 5,2 e 35,9 produz os
mesmos vereditos nos três datasets (o XGBoost no Covertype tem E/E_ref mediano de 5,1;
o modelo não dominado seguinte, o Random Forest no mesmo dataset, 35,9). Por semente,
a razão do XGBoost no Covertype variou de 3,4 a 9,8, abaixo de 10 em todas as dez.

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
> estimativas: a razão entre a energia incremental estimada e a medida foi de
> 0,071 ± 0,068 (três tentativas), isto é, o CodeCarbon capturou cerca de 7 % do
> acréscimo de consumo provocado pela carga, e a energia estimada se comporta como
> potência quase constante multiplicada pelo tempo; a ordenação dos modelos é
> confiável, mas os valores absolutos e a energia líquida de repouso não. Quarto, o
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
2. ~~Validação pela bateria e execução completa~~ feitas (commit d50ff51); análise
   completa da Seção 8 e conclusões nos itens 9 e 10 (17/10).
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
simplex) em vez de p-valor. H1 e H2 vêm de `stats_report.md` (Friedman e
Wilcoxon-Holm sobre a energia de treino; score relativo e dominância de Pareto, D2).
H2 segue a regra registrada na 5.6 (decisão D4): em cada dataset, um modelo dominado
é compatível com a hipótese, e um não dominado só o é se E/E_ref ≥ 10, porque o
custo marginal não é definido para a referência (ΔF1 = 0). Os vereditos são os mesmos
para qualquer limiar entre 5,2 e 35,9.

| Hipótese | 20 Newsgroups (principal) | Breast Cancer (robustez) | Covertype (robustez) |
|---|---|---|---|
| H1 | Confirmada: Friedman χ²_F = 28,08, p = 3,5 × 10⁻⁶; LR × cada modelo, Wilcoxon-Holm p = 0,0117 (piso com n = 10); sem a semente 42, χ²_F = 25,93, p = 9,8 × 10⁻⁶, Holm p = 0,023 | Confirmada: χ²_F = 27,48, p = 4,7 × 10⁻⁶; LR × cada modelo, Holm p = 0,0117 (RF × XGB não difere, p = 0,32) | Confirmada: χ²_F = 30,0, p = 1,4 × 10⁻⁶; todos os contrastes com Holm p = 0,0117 |
| H2 | Confirmada: RF e XGB dominados em 100 % das sementes (E/E_ref 99 e 218; ΔF1 −3,8 e −6,8); MLP dominada em 70 %, não dominada com 208 a 439 × E_ref | Confirmada: MLP, RF e XGB dominados em 100 %, 90 % e 80 %; não dominados com 41 a 61 × E_ref | Refutada: XGB na fronteira em 100 % das sementes com E/E_ref = 5,1 (< 10) e +10,4 pontos de F1 (1,6 J/ponto); RF na fronteira com 35,9 × E_ref (9,3 J/ponto); MLP dominada em 100 % |
| H3 | Confirmada: τ_b = 0,798 com pesos iguais (patamar 0,882); mín. 0,582; 14 pares invertidos; Spearman(w_E, τ_b) = 0,955 | Confirmada: τ_b = 0,786; mín. 0,576; 16 pares; Spearman 0,939 | Confirmada só com w_E < 0,4: τ_b = 0,882 (no patamar) com pesos iguais; mín. 0,696; Spearman 0,874 |
| H4 | Não confirmada: razão mínima de energia contra a LR de 92,9, acima da razão máxima de k (17,4); LR melhor em 100 % do simplex | Não confirmada: razão de 17,1 superada só no vértice w_C = 1 (0,4 % do simplex) | Parcialmente confirmada: XGB (F1 0,862, 5,49 × E) supera a LR de outro contexto em 11,3 % do simplex (w_C ≥ 0,90 ou w_W ≥ 0,95); nunca com pesos iguais (razão de k = 1,77) |

> Em síntese, a Regressão Logística foi a mais econômica em todos os conjuntos (H1);
> os modelos mais custosos não compensaram o consumo no 20 Newsgroups e no Breast
> Cancer, mas o XGBoost o fez no Covertype (H2, refutada nesse conjunto); a
> contextualização por região alterou a ordenação das configurações
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
- Validação pela bateria (`energy_validation_battery_20261015_210014.csv`): CodeCarbon
  em repouso 15,65 ± 0,43 W contra 8,37 ± 0,52 W da bateria; em carga 15,91 ± 0,21 W
  contra 12,24 ± 1,40 W; razão incremental 0,071 ± 0,068. A energia estimada é,
  aproximadamente, potência quase constante × tempo: a ordenação dos modelos é
  confiável (diferenças de tempo de uma a duas ordens de grandeza), os valores
  absolutos e a energia líquida não. A energia líquida negativa nos modelos pesados
  do Covertype (30 % a 40 % das sementes, com P₀ = 16,87 W) é o mesmo efeito.
- Como C e W são proporcionais à energia estimada, os valores absolutos de carbono e
  água herdam essa limitação; as razões entre contextos (k_r/k_s) não dependem dela.
- Fontes de contexto: IC média anual da Ember (2025), baseada na geração; fator
  hídrico do WRI (2020), com dados de tecnologia anteriores a 2020; PUE e WUE
  autodeclarados pela AWS, sem auditoria independente. WUE indisponível para Paris e
  Mumbai.
- Variação do equipamento ao longo da execução do Covertype (tempos de 1,5 a 2 vezes
  maiores nos modelos de maior custo a partir das sementes 314 e 1001) e semente 42
  anômala no 20 Newsgroups (item 9).

---

## 9. Seção 8 completa: RESULTADOS E DISCUSSÃO (texto para colar)

Fontes dos números: `experiments/results/<dataset>/full/stats_report.md`,
`comparative_results.csv`, `context_report.md` e
`experiments/results/energy_validation/energy_validation_battery_20261015_210014.md`.
Valores em média ± desvio padrão das dez sementes, salvo quando indicada a mediana.
Este item segue a estrutura do item 6 e incorpora os textos de contexto do item 8.

### 9.0 Avaliação crítica do orientador

1. **H1 confirmada nos três datasets, mas com p-valor no piso do teste.** Com dez
   sementes, o menor p bilateral possível do Wilcoxon pareado é 2/2¹⁰ = 0,00195; com a
   correção de Holm sobre seis comparações, 0,0117. Todos os contrastes da LR atingem
   esse piso: a LR foi a mais econômica em todas as sementes. Convém dizer isso no
   texto, para que a banca não leia "p = 0,0117" como evidência fraca.
2. **H2 precisa de operacionalização explícita.** A 5.6 diz "custo marginal superior
   ao da referência em ao menos uma ordem de grandeza", mas a referência não tem custo
   marginal (ΔF1 = 0). A leitura coerente com o protocolo é: um modelo não dominado só
   é compatível com H2 se custar ao menos dez vezes a energia da referência
   (E/E_ref ≥ 10). Usou-se essa leitura abaixo. **Registrada na 5.6 em 17/10/2026
   (decisão D4, item 4), com o limiar justificado e a análise de sensibilidade.**
3. **O GMS de contexto único põe a LR em 1º no Covertype com 10 pontos de F1 a menos.**
   Isso é coerente com a definição (o GMS é métrica ambiental, não de qualidade), mas
   o texto precisa apresentar o custo marginal (J por ponto de F1) como contraponto,
   para que a recomendação não seja "use sempre a LR".
4. **A validação pela bateria muda o estatuto dos números absolutos.** O CodeCarbon
   capturou 7 % do incremento de energia da carga; os valores em mWh devem ser lidos
   como indicador relativo, não como medida física.

### 9.1 Seção 8.1: Validação da medição

> Antes da execução completa, as estimativas do CodeCarbon foram confrontadas com a
> descarga da bateria do equipamento de medição, em três tentativas de 10 min de
> repouso seguidas de 10 min de carga. Em repouso, o CodeCarbon estimou
> 15,65 ± 0,43 W, contra 8,37 ± 0,52 W medidos pela bateria; em carga, 15,91 ± 0,21 W,
> contra 12,24 ± 1,40 W. A razão entre as energias absolutas na carga foi de
> 1,31 ± 0,13, efeito esperado da potência de referência da CPU e da potência
> constante atribuída à RAM. A razão entre as energias incrementais (carga menos
> repouso), que isola o custo da carga computacional, foi de apenas 0,071 ± 0,068: o
> CodeCarbon registrou um acréscimo de 0,26 W, enquanto a bateria registrou 3,87 W.
>
> Conclui-se que, neste ambiente, a energia estimada pelo CodeCarbon se comporta
> aproximadamente como uma potência quase constante multiplicada pelo tempo de
> execução. A memória RAM, com potência fixa de 10 W, respondeu em média por 49,5 %
> (20 Newsgroups), 66,9 % (Breast Cancer) e 58,1 % (Covertype) da energia estimada, e a
> correlação de Spearman entre GMS e tempo de parede foi de −0,960, −0,986 e −0,994,
> respectivamente. Por isso, a ordenação dos modelos por energia é interpretada como
> confiável, pois decorre de diferenças de tempo de uma a duas ordens de grandeza,
> medidas com precisão; os valores absolutos e a energia líquida de repouso, não.
>
> A potência ociosa P₀, medida por 60 s antes de cada dataset, foi de 15,11 W
> (20 Newsgroups), 15,05 W (Breast Cancer) e 16,87 W (Covertype). Como a potência
> estimada durante a carga difere pouco de P₀, a energia líquida E − P₀ · t fica na
> ordem do erro: no Covertype, ela resultou negativa em 40 % das sementes da MLP e do
> Random Forest e em 30 % das do XGBoost, o que é consequência direta da limitação
> acima, e não consumo negativo.

### 9.2 Seção 8.2: Desempenho e consumo no 20 Newsgroups (H1)

| Modelo | F1 macro | Energia de treino (mWh) | Tempo de treino (s) | GMS (contexto único) |
|---|---|---|---|---|
| Regressão Logística | 0,936 ± 0,011 | 0,101 ± 0,021 | 0,015 ± 0,002 | 99,76 ± 0,05 |
| Random Forest | 0,894 ± 0,013 | 9,14 ± 2,55 | 1,28 ± 0,23 | 78,5 ± 6,0 |
| XGBoost | 0,869 ± 0,012 | 20,37 ± 5,11 | 3,57 ± 0,64 | 52,1 ± 12,0 |
| MLP | 0,934 ± 0,014 | 25,69 ± 8,87 | 4,29 ± 1,18 | 39,5 ± 20,9 |

> A Regressão Logística obteve o maior F1-Score (0,936) com a menor energia de
> treinamento (0,101 mWh), de 90 a 250 vezes inferior à dos demais modelos. O teste de
> Friedman sobre a energia de treinamento rejeitou a igualdade entre os modelos
> (χ²_F = 28,08; p = 3,5 × 10⁻⁶; n = 10 sementes), e os testes de Wilcoxon pareados,
> com correção de Holm, indicaram diferença entre a Regressão Logística e cada um dos
> demais modelos (p ajustado = 0,0117 em todos os casos, o menor valor atingível com
> dez sementes e seis comparações, pois a Regressão Logística foi a mais econômica em
> todas as sementes). H1 é confirmada.
>
> A semente 42, a primeira executada, apresentou energia anômala nos modelos de maior
> custo: 0,30 (Random Forest), 0,36 (MLP) e 0,49 (XGBoost) vezes a mediana das demais
> sementes, com tempos de treino proporcionalmente menores (0,45 a 0,61 vezes). Nessa
> semente, o F1-Score também foi menor em todos os modelos, inclusive na Regressão
> Logística (de 0,9 a 2,7 pontos abaixo da média das demais), efeito da partição de
> dados; a redução de energia, porém, não atingiu a referência (1,29 vez a mediana) e
> não é explicada pela partição. A causa não foi identificada; uma hipótese é a maior
> frequência de turbo do processador em estado térmico inicial. A análise de
> sensibilidade sem essa semente (n = 9) manteve todas as conclusões: Friedman
> χ²_F = 25,93 (p = 9,8 × 10⁻⁶), todos os contrastes de Wilcoxon-Holm com
> p ajustado = 0,023 (novamente o piso para nove sementes), razões E/E_ref de 99,7 (RF),
> 223 (XGBoost) e 256 (MLP), MLP dominada em 67 % das sementes (contra 70 %) e τ_b do
> GMS contextual inalterado com pesos iguais (0,798; mediana no simplex de 0,774,
> contra 0,786).

### 9.3 Seção 8.3: Custo marginal e Pareto no 20 Newsgroups (H2)

> Na fronteira de Pareto entre F1-Score e energia (definição D2), o Random Forest e o
> XGBoost foram dominados pela Regressão Logística em todas as sementes: consumiram 99
> e 218 vezes mais energia (medianas de E/E_ref) para F1-Scores 3,8 e 6,8 pontos
> inferiores. A MLP foi dominada em 70 % das sementes; nas outras três, superou a
> referência por 0,8 a 1,0 ponto de F1, a um custo mediano de 87 J por ponto e com 208
> a 439 vezes a energia da referência. Nenhum modelo de maior custo
> integra a fronteira com custo inferior a dez vezes o da referência, o que confirma
> H2 no estudo de caso principal.

### 9.4 Seção 8.4: Contextos de execução no 20 Newsgroups (H3, H4)

Usar o texto do item 8.3 (dois primeiros parágrafos e o parágrafo de conclusão),
com as figuras `context_gms_heatmap.png` e `context_simplex.png` de
`docs/Results/newsgroups/full/`, e a tabela de contextos do README de
`experiments/contexts/`. Na legenda do simplex, registrar que, no vértice w_E = 1,
todos os contextos empatam e a configuração indicada é apenas a primeira da lista.

### 9.5 Seção 8.5: Verificação de robustez (Breast Cancer e Covertype)

| Dataset | Modelo | F1 macro | Energia (mWh) | E/E_ref (med.) | ΔF1 (pontos, med.) | J por ponto de F1 | Dominado |
|---|---|---|---|---|---|---|---|
| Breast Cancer | LR | 0,970 ± 0,012 | 0,023 ± 0,022 | 1 | 0 | n/a | 0 % |
| Breast Cancer | MLP | 0,923 ± 0,028 | 0,31 ± 0,09 | 16,2 | −4,8 | n/a | 100 % |
| Breast Cancer | XGBoost | 0,961 ± 0,017 | 0,83 ± 0,13 | 50,8 | −0,9 | 1,17 | 80 % |
| Breast Cancer | RF | 0,956 ± 0,013 | 0,94 ± 0,20 | 52,4 | −1,5 | 0,94 | 90 % |
| Covertype | LR | 0,759 ± 0,003 | 1,04 ± 0,21 | 1 | 0 | n/a | 0 % |
| Covertype | XGBoost | 0,862 ± 0,004 | 6,00 ± 2,35 | 5,14 | +10,4 | 1,64 | 0 % |
| Covertype | RF | 0,893 ± 0,004 | 38,2 ± 12,1 | 35,9 | +13,6 | 9,32 | 0 % |
| Covertype | MLP | 0,851 ± 0,006 | 79,1 ± 33,1 | 77,9 | +9,2 | 34,0 | 100 % |

Nota: o J por ponto de F1 é a mediana entre as sementes em que o modelo supera a
referência (ΔF1 > 0); no Breast Cancer, isso ocorre em poucas sementes, e a mediana
de ΔF1 é negativa.

> **Breast Cancer Wisconsin.** A Regressão Logística repetiu o padrão do estudo
> principal: maior F1-Score (0,970) e menor energia (mediana de 0,018 mWh; a média de
> 0,023 ± 0,022 mWh é inflada pela semente 2024, com 0,085 mWh). Friedman rejeitou a
> igualdade (χ²_F = 27,48; p = 4,7 × 10⁻⁶), e a Regressão Logística diferiu de cada
> modelo (p ajustado = 0,0117); apenas o par Random Forest × XGBoost não diferiu
> (p ajustado = 0,32). Os três modelos alternativos foram dominados na maior parte das
> sementes (MLP 100 %, Random Forest 90 %, XGBoost 80 %); nas três ocorrências não
> dominadas, o ganho foi de 1,9 a 3,7 pontos de F1 com 41 a 61 vezes a energia da
> referência. H1 e H2 são confirmadas.
>
> **Covertype.** Foi o único conjunto com compromisso efetivo entre qualidade e
> consumo. A Regressão Logística permaneceu a mais econômica (1,04 mWh; Friedman
> χ²_F = 30,0, p = 1,4 × 10⁻⁶; todos os contrastes com p ajustado = 0,0117),
> confirmando H1, mas obteve o menor F1-Score (0,759). O XGBoost elevou o F1-Score em
> 10,4 pontos com 5,1 vezes a energia, a um custo marginal de 1,6 J por ponto; o Random
> Forest, em 13,6 pontos com 35,9 vezes a energia, a 9,3 J por ponto. Ambos integram a
> fronteira de Pareto em todas as sementes, ao passo que a MLP foi dominada em todas.
> Como o XGBoost integra a fronteira com custo inferior a uma ordem de grandeza em
> relação à referência, H2 é refutada neste conjunto.
>
> O GMS de contexto único ordenou a Regressão Logística em primeiro lugar
> (99,2 ± 0,2), à frente do XGBoost (95,4 ± 1,8), apesar da diferença de 10 pontos de
> F1-Score. O resultado é coerente com a definição do GMS, que mede apenas custo
> ambiental, e evidencia que a métrica não substitui o critério de qualidade: deve ser
> usada em conjunto com a fronteira de Pareto e com o custo marginal. Neste caso, os
> 10 pontos de F1 do XGBoost custaram cerca de 17 J por treinamento.
>
> Registra-se ainda que, no Covertype, os modelos de maior custo ficaram mais lentos a
> partir da metade da execução: em relação às quatro primeiras sementes executadas
> (42, 123, 2024 e 7), o tempo de treino médio das seis seguintes foi 1,98 vez maior na
> MLP, 1,54 no XGBoost, 1,50 no Random Forest e 1,25 na Regressão Logística. Na MLP, o
> aumento começou na semente 314; no Random Forest e no XGBoost, a partir da semente
> 1001. O F1-Score não se alterou (variação inferior a 0,6 ponto), o que indica efeito
> do equipamento (provavelmente térmico ou de gerenciamento de energia), e não dos
> modelos. Como todos os modelos são executados dentro de cada semente, em ordem
> sorteada, e os testes são pareados por semente, o efeito é absorvido pelo bloco e não
> altera as comparações; ele explica, porém, a dispersão elevada das energias
> (coeficientes de variação de 32 % a 42 % nos modelos de maior custo) e é tratado como
> limitação.
>
> Quanto aos contextos, H3 se repetiu nos dois conjuntos e H4 só se verificou,
> parcialmente, no Covertype (item 8.2 e item 8.3).

### 9.6 Seção 8.6: Síntese das hipóteses

Tabela do item 8.4 (já preenchida para H1 a H4).

---

## 10. Seção 9: CONCLUSÕES (texto para colar)

> Este trabalho propôs o GreenML Score (GMS), métrica composta que integra consumo
> energético, emissões de carbono e pegada hídrica de modelos de aprendizado de
> máquina, e investigou em que medida a contextualização das emissões e do consumo
> hídrico pela região de execução altera a seleção de configurações modelo × região
> em relação a um critério baseado apenas em energia. Para isso, quatro modelos de
> famílias distintas foram avaliados sob protocolo padronizado em um estudo de caso de
> classificação de textos (20 Newsgroups) e em dois conjuntos tabulares de verificação
> de robustez (Breast Cancer Wisconsin e Covertype), com dez sementes, e combinados com
> sete contextos de execução caracterizados por fontes públicas.
>
> A análise formal mostrou que, em contexto único, o GMS se reduz à energia
> normalizada e que, com contextos distintos, assume a forma GMS = 1 − E · k, em que k
> depende apenas do contexto e dos pesos; decorre que um modelo mais custoso só supera
> outro quando a razão entre seus consumos é menor que a razão entre os fatores
> contextuais. Os experimentos confirmaram essa estrutura e responderam às hipóteses
> da seguinte forma. A Regressão Logística apresentou a menor energia de treinamento
> em todos os conjuntos e em todas as sementes (H1 confirmada). Os modelos de maior
> custo não ofereceram ganho de F1-Score proporcional no 20 Newsgroups nem no Breast
> Cancer, mas o XGBoost integrou a fronteira de Pareto no Covertype com apenas 5,1
> vezes a energia da referência e 10,4 pontos de F1 a mais (H2 confirmada em dois
> conjuntos e refutada no Covertype). A contextualização alterou a ordenação das
> configurações em todos os conjuntos, com τ_b abaixo do patamar atribuível ao
> desempate entre contextos e decrescente com o peso da energia (H3 confirmada). A
> seleção do modelo, contudo, só se alterou no Covertype e sob ponderações
> concentradas em carbono (w_C ≥ 0,90) ou em água (w_W ≥ 0,95), pois as razões entre os
> fatores contextuais (até 17,4 em carbono, 8,3 em água e 1,77 com pesos iguais) só
> superaram as razões de energia entre modelos competitivos nesse caso (H4 confirmada
> parcialmente).
>
> Em resposta à pergunta de pesquisa, conclui-se que carbono e água contextualizados
> alteram de forma robusta a escolha da região de execução para um mesmo modelo, e de
> modo dependente dos pesos, já que os dois recursos ordenam as regiões em sentidos
> quase opostos (o Brasil, por exemplo, combina baixa intensidade de carbono e alto
> consumo hídrico por kWh); mas alteram a escolha do modelo apenas quando as
> diferenças de consumo entre alternativas competitivas são inferiores à amplitude dos
> fatores contextuais, o que ocorreu em um dos três conjuntos.
>
> As contribuições do trabalho são: (i) a formalização do GMS e a caracterização
> analítica de quando o contexto pode alterar a seleção (condição E_j/E_i < k_r/k_s);
> (ii) um framework aberto, com protocolo de medição que inclui janela mínima por fase,
> potência ociosa, ordem sorteada e avisos de procedência; (iii) um método de
> validação física sem custo, pela descarga da bateria; e (iv) evidência empírica em
> três conjuntos de dados e sete contextos com fontes públicas e citadas.
>
> As principais limitações decorrem da medição: a validação mostrou que o CodeCarbon,
> neste equipamento, captura cerca de 7 % do incremento de energia da carga
> (0,071 ± 0,068), de modo que a energia estimada equivale aproximadamente a uma
> potência quase constante multiplicada pelo tempo; a ordenação dos modelos é
> confiável, mas os valores absolutos e a energia líquida de repouso não. Somam-se a
> variação de desempenho do equipamento ao longo da execução do Covertype, a semente
> anômala do 20 Newsgroups (sem efeito nas conclusões), o uso de intensidades de
> carbono médias anuais sem resolução horária, a ausência de WUE publicado para parte
> das regiões e a restrição a modelos clássicos executados em CPU.
>
> Como trabalhos futuros, recomenda-se: medir a energia com contadores de hardware
> (RAPL, em Linux) ou medidor externo, para obter valores absolutos confiáveis;
> incorporar intensidade de carbono horária (séries da Electricity Maps ou cálculo a
> partir da geração horária do ONS), permitindo avaliar o deslocamento temporal da
> execução; estender o estudo a modelos de linguagem pré-treinados, como o
> DistilBERT, em GPU, cujas diferenças de consumo em relação a modelos clássicos podem
> ser inferiores à amplitude dos fatores contextuais; e incluir a fase de inferência
> no GMS contextual.
>
> Como recomendação prática, propõe-se que a seleção de modelos sob critério ambiental
> siga três passos: primeiro, restringir a escolha à fronteira de Pareto entre
> qualidade preditiva e energia, reportando o custo marginal em joules por ponto de
> F1-Score; segundo, escolher a região de execução pelo fator contextual k, com os
> pesos de carbono e água declarados, já que regiões de baixa emissão podem ter alto
> consumo hídrico; terceiro, reportar sempre a fonte e o ano dos fatores de contexto e
> a ferramenta de medição, com sua validação. O GMS é útil como síntese do custo
> ambiental, mas não deve ser usado isoladamente como critério de seleção, porque não
> considera a qualidade preditiva.
