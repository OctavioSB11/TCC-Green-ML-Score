# Ambiente de medição

Registro de como o CodeCarbon obtém energia na máquina de medição. Verificado em
14/10/2026 com o log de inicialização (`log_level="info"`) do `EmissionsTracker`.

**Máquina de medição oficial (decisão da dupla, 14/10/2026): notebook do Danilo.**
A validação física (descarga da bateria) e todas as execuções completas são feitas nela.
A configuração usada até 01/10/2026 (notebook do Octávio) está registrada no fim
deste documento, apenas como histórico.

## Máquina

| Item | Valor |
|---|---|
| CPU | 13th Gen Intel(R) Core(TM) i5-1335U (12 threads, 1 CPU física) |
| RAM disponível | 15,697 GB |
| GPU | nenhuma detectada |
| Sistema | Windows-11-10.0.26300-SP0 |
| Python | 3.13.2 |
| CodeCarbon | 3.2.6 (`tracking_mode = machine`) |

## Backend de medição

Trecho do log de inicialização do CodeCarbon:

```
No CPU tracking mode found. Falling back on estimation based on TDP for CPU.
 Windows OS detected: Please install Intel Power Gadget to measure CPU
CPU Model on constant consumption mode: 13th Gen Intel(R) Core(TM) i5-1335U
No CPU tracking mode found. Falling back on CPU load mode.
No GPU found.
The below tracking methods have been set up:
        RAM Tracking Method: RAM power estimation model
        CPU Tracking Method: cpu_load
        GPU Tracking Method: Unspecified
```

| Componente | Método | Consequência |
|---|---|---|
| CPU | **Estimativa** `cpu_load`: potência proporcional à carga da CPU sobre o TDP de **55 W** que a base do CodeCarbon (`codecarbon/data/hardware/cpu_power.csv`, linha `Intel Core i5-1335U,55.0`) atribui ao i5-1335U. Não há RAPL nem Intel Power Gadget no Windows | A energia de CPU não é medida. Os 55 W correspondem à potência máxima em turbo do i5-1335U; a potência base do processador é de 15 W. Sob carga sustentada, o valor estimado tende a superestimar a CPU |
| RAM | **Estimativa** por modelo de potência: 10,0 W constantes | A energia de RAM é proporcional ao tempo de execução e independe da carga |
| GPU | não rastreada | — |

Em uma execução de teste de 4,6 s sem carga, a RAM respondeu por cerca de 59 % da
energia total (RAM 10,0 W; CPU ≈ 7,09 W).

## Implicações para o TCC

- Os valores de energia são **estimativas** do CodeCarbon, não medições de
  hardware. O texto deve dizer isso explicitamente.
- Como a RAM tem potência constante, a energia de RAM é tempo × 10 W; diferenças
  entre modelos refletem principalmente o tempo de execução e a carga da CPU.
- A única referência física disponível sem custo é a **bateria** do notebook: o
  Windows informa via WMI (`root\wmi:BatteryStatus`) a potência de descarga (mW,
  atualizada a cada ~10–20 s) e a carga restante (mWh, em passos de ~1 % ≈ 590 mWh;
  capacidade total atual 58.976 mWh). `experiments/energy_validation.py` compara
  as estimativas do CodeCarbon com essa referência.
- Teste preliminar de 14/10 (1 tentativa, fases de 60 s, com outros programas
  abertos; **não conclusivo**): em repouso, CodeCarbon 21,3 W × bateria 11,6 W;
  incremento da carga (Random Forest, 1 thread), CodeCarbon +0,9 W × bateria +5,6 W.
  Se confirmado na validação completa, indica que o CodeCarbon superestima a
  potência absoluta (RAM constante de 10 W e TDP de 55 W) e subestima o custo
  incremental da carga nesta máquina.
- O aviso de procedência da semana 2 (`tracking_mode = machine`, potência de RAM
  constante e, em fases curtas ou leves, RAM > 50 % da energia) será disparado
  nas execuções desta máquina.
- Potência ociosa P₀ observada nos quick-runs de 14/10 (10 s cada): 15,3 a 16,7 W.

## Verificação de `final_emissions_data`

No CodeCarbon 3.2.6, `EmissionsTracker.stop()` atribui
`self.final_emissions_data = emissions_data` antes de retornar
(`codecarbon/emissions_tracker.py`). Confirmado em execução real nas duas máquinas:
após `stop()`, o objeto é um `EmissionsData` com `energy_consumed`, `cpu_power`,
`ram_power` e `tracking_mode` preenchidos. O `GreenMLTracker` usa esse objeto como
fonte principal; o CSV só é lido como alternativa.

## Histórico: configuração anterior (notebook do Octávio, até 01/10/2026)

Usada nas execuções da v0.1 (`experiments/results/_legacy_v0.1/`) e na verificação
inicial do CodeCarbon. **Não** é a máquina de medição dos resultados finais.

| Item | Valor |
|---|---|
| CPU | 12th Gen Intel(R) Core(TM) i5-1235U (12 threads, 1 CPU física) |
| RAM disponível | 19,708 GB |
| Sistema | Windows-11-10.0.26200-SP0 |
| Python / CodeCarbon | 3.13.2 / 3.2.6 (`tracking_mode = machine`) |
| CPU (método) | `cpu_load` sobre TDP **presumido** de 48 W (4 W × 12 threads): o i5-1235U não consta da base do CodeCarbon, que tem apenas o i5-1235UL |
| RAM (método) | Estimativa constante de 20,0 W |
| Teste de 3 s sem carga | RAM ≈ 79 % da energia (RAM 20,0 W; CPU ≈ 5,06 W) |

Trecho do log de inicialização nessa máquina:

```
We saw that you have a 12th Gen Intel(R) Core(TM) i5-1235U but we don't know it. Please contact us.
We will use the default power consumption of 4 W per thread for your 12 CPU, so 48W.
No CPU tracking mode found. Falling back on estimation based on TDP for CPU.
CPU Model on constant consumption mode: 12th Gen Intel(R) Core(TM) i5-1235U
```

Como os modelos de potência diferem entre as máquinas (TDP de CPU de 48 W × 55 W;
RAM de 20 W × 10 W), resultados das duas máquinas **não são comparáveis** e não
devem ser misturados.
