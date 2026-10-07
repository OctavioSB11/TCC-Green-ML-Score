# Ambiente de medição

Registro de como o CodeCarbon obtém energia na máquina de medição. Verificado em
01/10/2026 com o log de inicialização (`log_level="info"`) do `EmissionsTracker`.

## Máquina

| Item | Valor |
|---|---|
| CPU | 12th Gen Intel(R) Core(TM) i5-1235U (12 threads, 1 CPU física) |
| RAM disponível | 19,708 GB |
| GPU | nenhuma detectada |
| Sistema | Windows-11-10.0.26200-SP0 |
| Python | 3.13.2 |
| CodeCarbon | 3.2.6 (`tracking_mode = machine`) |

## Backend de medição

Trecho do log de inicialização do CodeCarbon:

```
We saw that you have a 12th Gen Intel(R) Core(TM) i5-1235U but we don't know it. Please contact us.
We will use the default power consumption of 4 W per thread for your 12 CPU, so 48W.
No CPU tracking mode found. Falling back on estimation based on TDP for CPU.
 Windows OS detected: Please install Intel Power Gadget to measure CPU
CPU Model on constant consumption mode: 12th Gen Intel(R) Core(TM) i5-1235U
No CPU tracking mode found. Falling back on CPU load mode.
The below tracking methods have been set up:
        RAM Tracking Method: RAM power estimation model
        CPU Tracking Method: cpu_load
        GPU Tracking Method: Unspecified
```

| Componente | Método | Consequência |
|---|---|---|
| CPU | **Estimativa** `cpu_load`: potência proporcional à carga da CPU sobre um TDP **presumido** de 48 W (4 W × 12 threads), pois o i5-1235U não consta da base do CodeCarbon. Não há RAPL nem Intel Power Gadget no Windows | A energia de CPU não é medida. O TDP base real do i5-1235U (15 W) é bem menor que os 48 W presumidos |
| RAM | **Estimativa** por modelo de potência: 20,0 W constantes | A energia de RAM é proporcional ao tempo de execução, independe da carga |
| GPU | não rastreada | — |

Em uma execução de teste de 3 s sem carga, a RAM respondeu por cerca de 79 % da
energia total (RAM 20,0 W; CPU ≈ 5,06 W).

## Implicações para o TCC

- Os valores de energia são **estimativas** do CodeCarbon, não medições de
  hardware. O texto deve dizer isso explicitamente.
- Como a RAM tem potência constante, a energia de RAM é tempo × 20 W; diferenças
  entre modelos refletem principalmente tempo de execução e carga da CPU.
- A validação com o medidor de tomada (semana 3) é a única medição física
  disponível; ela deve ser comparada com essas estimativas.
- O aviso de procedência da semana 2 (RAM > 50 % da energia, potência de RAM
  constante, `tracking_mode = machine`) será disparado em todas as execuções
  desta máquina.

## Verificação de `final_emissions_data`

No CodeCarbon 3.2.6, `EmissionsTracker.stop()` atribui
`self.final_emissions_data = emissions_data` antes de retornar
(`codecarbon/emissions_tracker.py`). Confirmado em execução real: após `stop()`,
o objeto é um `EmissionsData` com `energy_consumed`, `cpu_power`, `ram_power` e
`tracking_mode` preenchidos. O `GreenMLTracker` usa esse objeto como fonte
principal; o CSV só é lido como alternativa.
