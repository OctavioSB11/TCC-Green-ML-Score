"""
energy_validation.py — Validação física das estimativas do CodeCarbon, sem custo.

Nesta máquina o CodeCarbon ESTIMA a energia (CPU por ``cpu_load`` sobre um TDP de
tabela; RAM com potência constante). A referência física gratuita disponível é a
**bateria do próprio notebook**: com o carregador desconectado, o Windows informa,
via WMI (``root\\wmi:BatteryStatus``), a potência de descarga (mW) e a carga
restante (mWh) do sistema inteiro.

Fontes de referência (``--source``):
  - ``battery`` (padrão): leitura automática da bateria. A energia de cada fase é
    a integral da potência de descarga amostrada a cada segundo; a queda da carga
    restante é registrada como verificação cruzada (resolução de ~1 % da bateria).
  - ``meter``: medidor de tomada, com leituras digitadas pelo operador (mantido
    caso um medidor venha a estar disponível).

Protocolo (por tentativa): uma fase de REPOUSO e uma fase de CARGA de mesma
duração, medidas ao mesmo tempo pelo CodeCarbon e pela referência. A referência
inclui tela, Wi-Fi e demais componentes que o CodeCarbon não vê; por isso a
comparação principal é a da energia INCREMENTAL da carga, ΔE = E_carga − E_repouso,
em que esses termos fixos se cancelam.

Uso (bateria ≥ 80 %, carregador DESCONECTADO, brilho fixo, sem outros programas):
    python experiments/energy_validation.py --trials 3 --duration 600
    python experiments/energy_validation.py --analyze experiments/results/energy_validation/<arquivo>.csv

Limitação: na bateria o Windows pode aplicar um perfil de energia diferente do da
tomada (frequência da CPU). A validação mede a fidelidade do CodeCarbon a uma
referência física nas mesmas condições, e não reproduz exatamente o ambiente do
experimento principal, executado na tomada.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from experiments.config import config  # noqa: E402

KWH_TO_WH: float = 1000.0
OUT_DIR = Path(config.RESULTS_DIR) / "energy_validation"
MIN_BATTERY_SHARE: float = 0.25  # interrompe abaixo de 25 % (economia de bateria)


class ValidationError(RuntimeError):
    """Condição inválida para a validação (ex.: carregador conectado)."""


# ---------------------------------------------------------------------------
# Análise (pura, testável)
# ---------------------------------------------------------------------------


def integrate_power_wh(
    times_s: np.ndarray, power_w: np.ndarray, t0: float, t1: float
) -> float:
    """
    Energia (Wh) de uma série de potência amostrada, no intervalo [t0, t1].

    A potência é tratada como constante por partes (cada amostra vale até a
    seguinte), pois o firmware da bateria só atualiza o valor a cada poucos segundos.
    O valor vigente em t0 é a última amostra anterior a t0.

    Raises:
        ValueError: se não houver amostra até t0 ou se t1 ≤ t0.
    """
    if t1 <= t0:
        raise ValueError("t1 deve ser maior que t0.")
    t, p = np.asarray(times_s, float), np.asarray(power_w, float)
    order = np.argsort(t)
    t, p = t[order], p[order]
    if t.size == 0 or t[0] > t0:
        raise ValueError("Não há amostra de potência no início da fase.")
    start = int(np.searchsorted(t, t0, side="right") - 1)
    inside = (t > t0) & (t < t1)
    knots = np.concatenate([[t0], t[inside], [t1]])
    values = np.concatenate([[p[start]], p[inside]])
    return float(np.sum(values * np.diff(knots)) / 3600.0)


def analyze(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compara CodeCarbon e referência física por tentativa.

    Espera colunas ``trial``, ``phase`` (``idle``/``load``), ``duration_s``,
    ``cc_energy_wh`` e ``ref_energy_wh``. Devolve uma linha por tentativa com as
    potências médias de cada fonte, a energia incremental ΔE da carga e as razões
    CodeCarbon / referência (absoluta na carga e incremental).

    Raises:
        ValueError: se faltar alguma fase em alguma tentativa ou houver valores
            ausentes.
    """
    required = {"trial", "phase", "duration_s", "cc_energy_wh", "ref_energy_wh"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    if df[list(required)].isna().any().any():
        raise ValueError("Há leituras ausentes em ref_energy_wh ou cc_energy_wh.")

    rows = []
    for trial, g in df.groupby("trial"):
        phases = g.set_index("phase")
        if not {"idle", "load"} <= set(phases.index):
            raise ValueError(f"Tentativa {trial} sem as fases idle e load.")
        idle, load = phases.loc["idle"], phases.loc["load"]
        # Repouso e carga podem ter durações ligeiramente diferentes: o ΔE
        # compara a carga com o repouso escalado para a mesma duração.
        scale = load["duration_s"] / idle["duration_s"]
        d_cc = load["cc_energy_wh"] - idle["cc_energy_wh"] * scale
        d_ref = load["ref_energy_wh"] - idle["ref_energy_wh"] * scale
        rows.append(
            {
                "trial": trial,
                "cc_idle_w": idle["cc_energy_wh"] * 3600 / idle["duration_s"],
                "ref_idle_w": idle["ref_energy_wh"] * 3600 / idle["duration_s"],
                "cc_load_w": load["cc_energy_wh"] * 3600 / load["duration_s"],
                "ref_load_w": load["ref_energy_wh"] * 3600 / load["duration_s"],
                "cc_delta_wh": d_cc,
                "ref_delta_wh": d_ref,
                "ratio_load": load["cc_energy_wh"] / load["ref_energy_wh"],
                "ratio_delta": d_cc / d_ref if d_ref > 0 else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_report(per_trial: pd.DataFrame, source: Path, reference: str) -> str:
    """Relatório Markdown com médias e desvios entre tentativas."""
    n = len(per_trial)

    def ms(col: str, spec: str = ".3f") -> str:
        s = per_trial[col]
        sd = f" ± {s.std(ddof=1):{spec}}" if n > 1 else ""
        return f"{s.mean():{spec}}{sd}"

    return "\n".join(
        [
            "# Validação física das estimativas do CodeCarbon\n",
            f"Fonte: `{source.as_posix()}` · referência: **{reference}** · tentativas: {n}\n",
            "## Resumo (média ± desvio entre tentativas)\n",
            "| Grandeza | CodeCarbon | Referência |",
            "|---|---|---|",
            f"| Potência em repouso (W) | {ms('cc_idle_w', '.2f')} | {ms('ref_idle_w', '.2f')} |",
            f"| Potência em carga (W) | {ms('cc_load_w', '.2f')} | {ms('ref_load_w', '.2f')} |",
            f"| Energia incremental da carga ΔE (Wh) | {ms('cc_delta_wh')} | {ms('ref_delta_wh')} |",
            "",
            f"- Razão CodeCarbon / referência, energia absoluta na carga: {ms('ratio_load')}",
            f"- Razão CodeCarbon / referência, energia incremental ΔE: {ms('ratio_delta')}",
            "",
            "Interpretação: a razão absoluta é afetada por componentes que o "
            "CodeCarbon não vê (tela, Wi-Fi, placa-mãe); a razão incremental indica "
            "se o CodeCarbon captura o custo da CARGA, que é o que o GMS compara "
            "entre modelos. Razão incremental próxima de 1 com baixa dispersão "
            "sustenta o uso das estimativas; caso contrário, o texto deve reportar o "
            "fator observado ou tratar a energia como indicador relativo.",
            "",
            "## Por tentativa\n",
            per_trial.round(4).to_markdown(index=False),
            "",
        ]
    )


# ---------------------------------------------------------------------------
# Leitura da bateria (Windows)
# ---------------------------------------------------------------------------

_PS_SAMPLER = (
    "$ErrorActionPreference='Stop';"
    "while($true){"
    "$b=Get-CimInstance -Namespace root\\wmi -ClassName BatteryStatus|Select-Object -First 1;"
    '[Console]::Out.WriteLine("$($b.RemainingCapacity) $($b.DischargeRate) $($b.PowerOnline)");'
    "[Console]::Out.Flush();Start-Sleep -Milliseconds 1000}"
)


def read_full_capacity_mwh() -> float:
    """Capacidade de carga completa atual da bateria (mWh), via WMI."""
    out = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "(Get-CimInstance -Namespace root\\wmi -ClassName "
            "BatteryFullChargedCapacity|Select-Object -First 1).FullChargedCapacity",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(out.stdout.strip())


@dataclass
class BatterySampler:
    """
    Amostrador contínuo da bateria: um único processo PowerShell imprime, a cada
    segundo, carga restante (mWh), potência de descarga (mW) e se há carregador.

    O processo roda durante TODA a sessão (repouso e carga), de modo que seu
    custo aparece igualmente nas duas fases e se cancela no ΔE.
    """

    times_s: list[float] = field(default_factory=list)
    capacity_mwh: list[float] = field(default_factory=list)
    rate_mw: list[float] = field(default_factory=list)
    online: list[bool] = field(default_factory=list)
    _proc: subprocess.Popen[str] | None = None
    _thread: threading.Thread | None = None

    def start(self) -> None:
        if sys.platform != "win32":
            raise ValidationError("A leitura da bateria via WMI exige Windows.")
        self._proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", _PS_SAMPLER],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        self._thread = threading.Thread(target=self._read, daemon=True)
        self._thread.start()
        deadline = time.perf_counter() + 30
        while not self.times_s:
            if time.perf_counter() > deadline or self._proc.poll() is not None:
                self.stop()
                raise ValidationError(
                    "A bateria não respondeu via WMI (root\\wmi:BatteryStatus)."
                )
            time.sleep(0.2)

    def _read(self) -> None:
        assert self._proc is not None and self._proc.stdout is not None
        for line in self._proc.stdout:
            parts = line.split()
            if len(parts) != 3:
                continue
            self.times_s.append(time.perf_counter())
            self.capacity_mwh.append(float(parts[0]))
            self.rate_mw.append(float(parts[1]))
            self.online.append(parts[2].lower() == "true")

    def stop(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()

    def check_on_battery(self, min_capacity_mwh: float) -> None:
        """Interrompe se o carregador foi conectado ou a carga ficou baixa."""
        if self.online and self.online[-1]:
            raise ValidationError(
                "Carregador conectado: desconecte-o (a medição exige descarga)."
            )
        if self.capacity_mwh and self.capacity_mwh[-1] < min_capacity_mwh:
            raise ValidationError(
                "Carga da bateria abaixo do mínimo; recarregue e recomece."
            )

    def phase_energy(self, t0: float, t1: float) -> tuple[float, float]:
        """(energia integrada da potência de descarga, queda da carga restante), em Wh."""
        t = np.array(self.times_s)
        if any(o for o, ti in zip(self.online, t) if t0 <= ti <= t1):
            raise ValidationError("Carregador conectado durante a fase.")
        rate_wh = integrate_power_wh(t, np.array(self.rate_mw) / 1000.0, t0, t1)
        cap = np.array(self.capacity_mwh)
        before = cap[t <= t0][-1]
        after = cap[t <= t1][-1]
        return rate_wh, (before - after) / 1000.0


# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------


def make_load() -> Callable[[], Any]:
    """Carga representativa: treino de Random Forest em breast_cancer (N_JOBS fixo)."""
    from sklearn.datasets import load_breast_cancer
    from sklearn.ensemble import RandomForestClassifier

    X, y = load_breast_cancer(return_X_y=True)
    model = RandomForestClassifier(
        n_estimators=100, random_state=config.SEEDS[0], n_jobs=config.N_JOBS
    )
    return lambda: model.fit(X, y)


def ask_float(prompt: str) -> float:
    """Lê um número digitado pelo operador (aceita vírgula decimal)."""
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            print("  Valor inválido; digite apenas o número.")


def run_phase(
    phase: str,
    duration_s: float,
    load: Callable[[], Any],
    sampler: BatterySampler | None,
    min_capacity_mwh: float = 0.0,
) -> dict[str, Any]:
    """Mede uma fase com o CodeCarbon e com a referência física."""
    from threadpoolctl import threadpool_limits

    from green_ml_score.collectors.codecarbon import GreenMLTracker

    out_dir = OUT_DIR / "codecarbon"
    out_dir.mkdir(parents=True, exist_ok=True)
    tracker = GreenMLTracker(output_dir=str(out_dir), log_level="error")

    meter_start = None
    if sampler is None:
        meter_start = ask_float(
            f"\n[{phase}] Leitura ACUMULADA do medidor (Wh) e Enter para iniciar: "
        )
    else:
        sampler.check_on_battery(min_capacity_mwh)

    print(f"  medindo {phase} por {duration_s:g} s — não use o computador...")
    with threadpool_limits(limits=config.N_JOBS):
        tracker.start()
        t0 = time.perf_counter()
        try:
            while time.perf_counter() - t0 < duration_s:
                if phase == "load":
                    load()
                else:
                    time.sleep(0.5)
        finally:
            t1 = time.perf_counter()
            tracker.stop()

    d = tracker.details
    row: dict[str, Any] = {
        "phase": phase,
        "duration_s": t1 - t0,
        "cc_session_s": d.duration_s,
        "cc_energy_wh": tracker.energy_kwh * KWH_TO_WH,
        "cc_cpu_wh": None if d.cpu_energy_kwh is None else d.cpu_energy_kwh * KWH_TO_WH,
        "cc_ram_wh": None if d.ram_energy_kwh is None else d.ram_energy_kwh * KWH_TO_WH,
        "cc_tracking_mode": d.tracking_mode,
    }
    if sampler is None:
        meter_end = ask_float(f"[{phase}] Leitura ACUMULADA do medidor (Wh) agora: ")
        row.update(
            {
                "ref_source": "meter",
                "ref_energy_wh": meter_end - meter_start,
                "meter_start_wh": meter_start,
                "meter_end_wh": meter_end,
            }
        )
    else:
        time.sleep(2.0)  # garante uma amostra após t1
        rate_wh, cap_wh = sampler.phase_energy(t0, t1)
        print(
            f"  CodeCarbon {row['cc_energy_wh']:.3f} Wh · bateria {rate_wh:.3f} Wh "
            f"(queda de carga {cap_wh:.3f} Wh)"
        )
        row.update(
            {
                "ref_source": "battery",
                "ref_energy_wh": rate_wh,
                "battery_capacity_drop_wh": cap_wh,
            }
        )
    return row


def collect(trials: int, duration_s: float, source: str) -> Path:
    """Executa as tentativas e grava o CSV bruto."""
    load = make_load()
    load()  # aquecimento, fora da medição
    sampler = BatterySampler() if source == "battery" else None
    min_capacity = 0.0
    if sampler is not None:
        min_capacity = MIN_BATTERY_SHARE * read_full_capacity_mwh()
        sampler.start()
        sampler.check_on_battery(min_capacity)
    rows = []
    try:
        for trial in range(1, trials + 1):
            print(f"\n=== Tentativa {trial}/{trials} ===")
            for phase in ("idle", "load"):
                rows.append(
                    {
                        "trial": trial,
                        **run_phase(phase, duration_s, load, sampler, min_capacity),
                    }
                )
    finally:
        if sampler is not None:
            sampler.stop()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"energy_validation_{source}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--source", choices=["battery", "meter"], default="battery")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--duration", type=float, default=600.0, help="s por fase")
    parser.add_argument(
        "--analyze", type=Path, default=None, help="Só analisa um CSV já coletado."
    )
    args = parser.parse_args()

    path = args.analyze or collect(args.trials, args.duration, args.source)
    if not path.exists():
        sys.exit(f"Arquivo não encontrado: {path}")
    df = pd.read_csv(path)
    reference = str(df["ref_source"].iloc[0]) if "ref_source" in df else args.source
    report = build_report(analyze(df), path, reference)
    path.with_suffix(".md").write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"[OK] Dados em {path}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
