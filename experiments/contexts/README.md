# Contextos de execução

`contexts.csv` define os contextos (região × horário) avaliados por
`experiments/context_analysis.py`. O arquivo está **vazio de propósito**: os valores
devem ser coletados e citados pela dupla (integrante B). O script falha se não houver
nenhuma linha.

| Coluna | Obrigatória | Unidade | Descrição |
|---|---|---|---|
| `name` | sim | — | Região ou provedor (ex.: `BR-SE`, `DE`, `US-CA`) |
| `hour` | não | 0–23 | Hora a que a IC se refere; vazio = média anual |
| `carbon_intensity_g_per_kwh` | sim | gCO₂e/kWh | IC da rede (ONS, Electricity Maps, EEA, EPA eGRID) |
| `pue` | não (padrão 1) | — | PUE do data center; 1 para execução local |
| `wue_onsite_l_per_kwh` | sim | L/kWh | WUE do data center (relatórios de sustentabilidade); 0 para execução local |
| `offsite_water_l_per_kwh` | sim | L/kWh | Água consumida na geração elétrica da região (Macknick et al., 2012) |
| `source` | não | — | Referência dos valores da linha |

Modelo de cálculo (`green_ml_score/contexts/execution_context.py`):

- C = E × PUE × IC
- W = E × WUE_on-site + E × PUE × fator off-site

Cada combinação `name` + `hour` deve ser única.
