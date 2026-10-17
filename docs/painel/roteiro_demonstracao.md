# Roteiro de demonstração do GreenML Dashboard (cerca de 3 min)

Conjunto de dados usado na demonstração: **Covertype**, o único com compromisso real
entre qualidade e custo. Todos os números abaixo aparecem na tela e batem com o
artigo. As capturas de cada passo estão em [`slides/`](slides/), numeradas na ordem
do roteiro.

## Antes da apresentação

- [ ] Notebook na tomada, com a suspensão e o descanso de tela desligados.
- [ ] Abrir o painel uns 5 min antes, já no Prompt de Comando, na pasta do projeto:
  `.venv\Scripts\python.exe -m streamlit run app\Home.py --client.toolbarMode viewer`
  (a opção do final esconde o botão "Deploy").
- [ ] Passar uma vez por todas as telas para aquecer o cache (a primeira abertura de
  cada uma demora alguns segundos).
- [ ] Deixar na barra lateral o conjunto **Covertype** e voltar para **Início**.
- [ ] Zoom do navegador entre 100% e 125%, conforme o projetor; fechar outras abas.
- [ ] Internet só é necessária para o fundo do mapa do simulador. Sem conexão, os
  pontos das regiões continuam aparecendo.
- [ ] Ter a pasta `docs/painel/slides` aberta numa janela à parte (plano B).

## Roteiro

| Tempo | Tela | O que fazer | O que falar |
|---|---|---|---|
| 0:00 a 0:20 | Início | Mostrar a página inicial. | "Este é o painel do GreenML Score. Ele lê os resultados da execução completa: quatro modelos, três conjuntos de dados, dez sementes e sete contextos. Nada é recalculado à mão; tudo vem dos CSVs do experimento." |
| 0:20 a 0:55 | Visão geral | Clicar em **Visão geral**. Mostrar os cartões e descer até **Rankings por critério**. | "No Covertype, o modelo mais preciso é o Random Forest, mas ele é só o terceiro em energia e em GMS. As linhas se cruzam: cada critério aponta para um modelo diferente. Com o mesmo contexto para todos, o GMS segue exatamente a energia, como a formulação prevê." |
| 0:55 a 1:35 | Qualidade × custo | Clicar em **Qualidade × custo**. Passar o mouse no XGBoost e mostrar a tabela de custo. | "Aqui está a fronteira de Pareto. A MLP é dominada em todas as sementes. O XGBoost ganha 10,4 pontos de F1 com 5,1 vezes a energia da Regressão Logística, ou seja, 1,64 J por ponto de F1. O Random Forest ganha 13,6 pontos, mas a 9,32 J por ponto. É por isso que H2 é refutada no Covertype." |
| 1:35 a 2:30 | Simulador de contexto | Clicar em **Simulador de contexto** e escolher o perfil **Só carbono**. Mostrar o aviso amarelo, os indicadores e descer até o mapa e o mapa de calor. | "Agora entra o contexto. Com todo o peso no carbono, o XGBoost treinado em Estocolmo fica com 99,6 e passa a Regressão Logística treinada na Índia, com 98,8, mesmo gastando mais energia. Isso acontece porque o fator de carbono varia 17,4 vezes entre as regiões. O τ_b cai para 0,696, abaixo do patamar de 0,882, e aparecem 31 pares invertidos. Com pesos iguais, nada disso acontece." |
| 2:30 a 2:50 | Cartão ambiental | Clicar em **Cartão ambiental**, escolher **AWS-Stockholm** e **Só carbono**. Mostrar o botão de baixar o PNG. | "Para cada escolha, o painel gera um cartão com F1, energia, carbono, água, posição no GMS e as fontes dos fatores. Um treino do XGBoost em Estocolmo emite 0,223 mg de CO₂e. O cartão pode ser baixado em PNG, Markdown ou CSV." |
| 2:50 a 3:00 | Avalie seu modelo | Clicar em **Avalie seu modelo** e mostrar o resultado com os dados de exemplo. | "Por fim, qualquer pessoa pode enviar um CSV com os próprios resultados e ver o GMS, a fronteira e a regra D4 com as mesmas fórmulas. Obrigado." |

Se o tempo apertar, o passo do cartão pode virar uma frase só, dita ainda no
simulador.

## Plano B

Se o painel não abrir ou travar, apresentar as capturas de `docs/painel/slides/`
na mesma ordem e com as mesmas falas:

| Arquivo | Passo |
|---|---|
| `00_inicio.png` | Início |
| `01_visao_geral_cartoes.png`, `02_visao_geral_rankings.png` | Visão geral |
| `03_qualidade_custo_pareto.png`, `04_qualidade_custo_custo_marginal.png` | Qualidade × custo |
| `05_simulador_so_carbono.png`, `06_simulador_mapa.png`, `07_simulador_mapa_de_calor.png` | Simulador (perfil Só carbono) |
| `08_cartao_ambiental.png`, `09_cartao_downloads.png`, `11_cartao_xgboost_estocolmo.png` | Cartão ambiental (o 11 é o PNG que o painel baixa) |
| `10_avalie_seu_modelo.png` | Avalie seu modelo |

As capturas têm 3200 × 1800 pixels (16:9) e cabem inteiras num slide. Para gerar de
novo, com o painel aberto, use `docs\painel\gerar_capturas.mjs` (instruções no
começo do arquivo).

## Perguntas prováveis da banca

**1. Se o CodeCarbon captou só cerca de 7% do aumento de consumo, os resultados valem?**
A comparação com a descarga da bateria mostrou que a ferramenta mede bem o tempo, mas
quase não percebe a carga. Por isso os valores absolutos de energia, carbono e água
são indicativos. As conclusões do trabalho dependem de razões entre modelos e entre
regiões, e essas razões se mantêm.

**2. Por que a ordem entre os modelos é confiável e o valor absoluto não?**
Porque a energia estimada acompanha o tempo de execução, e os modelos diferem em tempo
por uma a duas ordens de grandeza. Um erro de escala igual para todos não muda quem
gasta mais. A Regressão Logística foi a mais econômica em todas as sementes.

**3. No artigo o XGBoost gasta 5,1 vezes a energia da RL, mas o "Avalie seu modelo" mostra 5,5. Qual está certo?**
Os dois. O artigo usa a mediana das razões semente a semente (5,1). A tela de envio
de CSV não sabe se as sementes estão pareadas, então divide as medianas de energia de
cada modelo (5,5). A legenda da tela explica isso, e a conclusão é a mesma: abaixo de
10, na fronteira, H2 refutada.

**4. Por que o cartão mostra só uma equivalência (carga de smartphone)?**
Porque só ela tem fonte pública e verificável: a calculadora de equivalências da U.S.
EPA, com 0,019 kWh por carga. Preferimos não usar comparações sem fonte citável.

**5. Se o GMS segue a energia num contexto único, para que ele serve?**
Num contexto único, ele de fato equivale à energia normalizada; isso foi demonstrado.
O valor dele aparece quando o modelo pode rodar em lugares diferentes: aí carbono e
água mudam a ordem das configurações e, no Covertype, mudam até o modelo escolhido.

## Publicação no Streamlit Community Cloud (opcional, não feita)

O Streamlit Community Cloud é gratuito e publica o painel direto do GitHub. Como o
repositório é privado, seria preciso que o dono (Octávio) entrasse em
share.streamlit.io com a conta do GitHub, autorizasse o acesso ao repositório e
criasse o app apontando para `app/Home.py`, com Python 3.11 ou superior. Antes,
valeria conferir na documentação do serviço como ele instala as dependências; o mais
provável é precisar de um `requirements.txt` com o pacote e o extra `app`. O painel
continuaria lendo só os CSVs do repositório. Para a banca, a execução local mais as
capturas do plano B já bastam.
