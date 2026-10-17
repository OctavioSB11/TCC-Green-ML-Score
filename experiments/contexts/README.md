# Contextos de execução

`contexts.csv` define os contextos (região × horário) avaliados por
`experiments/context_analysis.py`. Preenchido em 17/10/2026 com
sete contextos (ver "Contextos adotados" abaixo); cada linha cita a própria fonte. O
script falha se não houver nenhuma linha.

| Coluna | Obrigatória | Unidade | Descrição |
|---|---|---|---|
| `name` | sim | — | Região ou provedor (ex.: `BR-SE`, `DE`, `US-CA`) |
| `hour` | não | 0–23 | Hora a que a IC se refere; vazio = média anual |
| `carbon_intensity_g_per_kwh` | sim | gCO₂e/kWh | IC da rede (ONS, Electricity Maps, EEA, EPA eGRID) |
| `pue` | não (padrão 1) | — | PUE do data center; 1 para execução local |
| `wue_onsite_l_per_kwh` | sim | L/kWh | WUE do data center (relatórios de sustentabilidade); 0 para execução local |
| `offsite_water_l_per_kwh` | sim | L/kWh | Água consumida na geração elétrica da região (Macknick et al., 2012) |
| `source` | não | — | Referência dos valores da linha |
| `accessed` | não | AAAA-MM-DD | Data de acesso às fontes (não é lida pelo código) |

Modelo de cálculo (`green_ml_score/contexts/execution_context.py`):

- C = E × PUE × IC
- W = E × WUE_on-site + E × PUE × fator off-site

Cada combinação `name` + `hour` deve ser única.

## Contextos adotados (17/10/2026)

Dois grupos. **Local** (`*-local`): o próprio notebook de medição ligado à rede de cada
país, com PUE = 1 e WUE on-site = 0 por definição; isola o efeito da rede elétrica.
**Nuvem** (`AWS-*`): regiões da AWS com PUE e WUE de 2025 publicados nas fichas de
sustentabilidade da empresa; acrescenta o efeito do data center. Um único provedor e
um único ano mantêm os valores comparáveis entre si.

| Contexto | IC (gCO2e/kWh) | PUE | WUE on-site (L/kWh) | Off-site (L/kWh) |
|---|---|---|---|---|
| BR-local | 109,95 | 1 | 0 | 18,584 |
| FR-local | 41,45 | 1 | 0 | 3,671 |
| IN-local | 670,55 | 1 | 0 | 3,444 |
| AWS-SaoPaulo | 109,95 | 1,14 | 0,09 | 18,584 |
| AWS-Virginia | 356,592 | 1,15 | 0,06 | 2,385 |
| AWS-Frankfurt | 329,65 | 1,24 | 0,17 | 1,930 |
| AWS-Stockholm | 35,35 | 1,09 | 0,02 | 6,018 |

Fontes (acesso em 17/10/2026; todas gratuitas, referências completas na coluna `source`):

- IC: Ember, *Yearly electricity data*, variável "CO2 intensity", 2025 (países);
  Ember, *US electricity data*, Virginia, 2025 (estado). Licença CC-BY-4.0.
- Fator off-site: Reig et al. (WRI, 2020), Apêndice 2 (países) e Apêndice 1
  (subregião eGRID SRVC para a Virgínia), em gal/kWh, convertidos por 3,785 L/gal.
  O WRI compila fatores por tecnologia da literatura revisada por Macknick et al.
  (2012). Os valores dos EUA (3,14), da SRVC (2,385), da Suécia (6,02) e da Índia (3,44)
  coincidem com a Tabela 1 de Li et al. (2025, *Making AI Less "Thirsty"*), que usa a
  mesma fonte.
- PUE e WUE da nuvem: AWS Sustainability Fact Sheets (Brazil, Virginia, Germany,
  Sweden), ano 2025.

## Valores não confirmados (`contexts_pendentes.csv`)

Linhas que não entram na análise porque falta um valor obrigatório numa fonte pública:

- **AWS-Paris** e **AWS-Mumbai**: a AWS publica o PUE (1,35 e 1,40 em 2025), mas não
  o WUE. França e Índia entram apenas como contextos locais.
- **Brasil por horário (pico e vale)**: não há fator de emissão horário oficial do SIN
  (o MCTI publica fatores mensais). Exigiria a série horária da Electricity Maps
  (portal de dados, gratuito para uso não comercial) ou um cálculo próprio a partir da
  geração horária por fonte do ONS (dados abertos), com fatores por tecnologia
  escolhidos e justificados pela dupla.
