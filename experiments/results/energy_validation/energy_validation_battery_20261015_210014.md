# Validação física das estimativas do CodeCarbon

Fonte: `experiments/results/energy_validation/energy_validation_battery_20261015_210014.csv` · referência: **battery** · tentativas: 3

## Resumo (média ± desvio entre tentativas)

| Grandeza | CodeCarbon | Referência |
|---|---|---|
| Potência em repouso (W) | 15.65 ± 0.43 | 8.37 ± 0.52 |
| Potência em carga (W) | 15.91 ± 0.21 | 12.24 ± 1.40 |
| Energia incremental da carga ΔE (Wh) | 0.044 ± 0.045 | 0.645 ± 0.151 |

- Razão CodeCarbon / referência, energia absoluta na carga: 1.310 ± 0.133
- Razão CodeCarbon / referência, energia incremental ΔE: 0.071 ± 0.068

Interpretação: a razão absoluta é afetada por componentes que o CodeCarbon não vê (tela, Wi-Fi, placa-mãe); a razão incremental indica se o CodeCarbon captura o custo da CARGA, que é o que o GMS compara entre modelos. Razão incremental próxima de 1 com baixa dispersão sustenta o uso das estimativas; caso contrário, o texto deve reportar o fator observado ou tratar a energia como indicador relativo.

## Por tentativa

|   trial |   cc_idle_w |   ref_idle_w |   cc_load_w |   ref_load_w |   cc_delta_wh |   ref_delta_wh |   ratio_load |   ratio_delta |
|--------:|------------:|-------------:|------------:|-------------:|--------------:|---------------:|-------------:|--------------:|
|       1 |     16.1014 |       8.9653 |     16.1459 |      13.7171 |        0.0074 |         0.7921 |       1.1771 |        0.0094 |
|       2 |     15.2384 |       8.1443 |     15.8022 |      12.0559 |        0.094  |         0.6522 |       1.3107 |        0.1441 |
|       3 |     15.5994 |       7.9984 |     15.7773 |      10.9397 |        0.0297 |         0.4904 |       1.4422 |        0.0605 |
