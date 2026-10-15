"""
meter_validation.py — Validação do CodeCarbon com um medidor de energia de tomada.

O medidor de tomada é a única medição física disponível no ambiente do TCC: o
CodeCarbon, nesta máquina, ESTIMA a CPU (cpu_load sobre um TDP presumido) e a RAM
(potência constante). Este script compara as duas fontes.

Protocolo (por tentativa): uma fase de REPOUSO e uma fase de CARGA de mesma
duração, medidas ao mesmo tempo pelo CodeCarbon e pelo medidor. O operador digita
a leitura acumulada do medidor (Wh) no início e no fim de cada fase. Como o medidor
inclui tela, carregador e demais componentes, a comparação principal é a da
energia INCREMENTAL da carga, ΔE = E_carga − E_repouso, em que esses termos fixos
se cancelam.

Uso (notebook na tomada, ligado ao medidor, sem outros programas abertos):
    python experiments/meter_validation.py --trials 3 --duration 600
    python experiments/meter_validation.py --meter-mode power   # medidor só mostra W
    python experiments/meter_validation.py --analyze experiments/results/meter_validation/<arquivo>.csv

Resolução: escolha ``--duration`` para que cada fase acumule ao menos 100× a
resolução do medidor (ex.: resolução de 0,01 kWh = 10 Wh exige fases muito longas;
prefira medidores com resolução de 1 Wh ou melhor, ou o modo ``power``).
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from experiments.config import config  # noqa: E402

KWH_TO_WH: float = 1000.0
OUT_DIR = Path(config.RESULTS_DIR) / "meter_validation"


# ---------------------------------------------------------------------------
# Análise (pura, testável)
# ---------------------------------------------------------------------------


def analyze(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compara CodeCarbon e medidor por tentativa.

    Espera colunas ``trial``, ``phase`` (``idle``/``load``), ``duration_s``,
    ``cc_energy_wh`` e ``meter_energy_wh``. Devolve uma linha por tentativa com as
    potências médias de cada fonte, a energia incremental ΔE da carga e as razões
    CodeCarbon / medidor (absoluta na carga e incremental).

    Raises:
        ValueError: se faltar alguma fase em alguma tentativa ou houver valores
            ausentes.
    """
    required = {"trial", "phase", "duration_s", "cc_energy_wh", "meter_energy_wh"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    if df[list(required)].isna().any().any():
        raise ValueError("Há leituras ausentes; preencha meter_energy_wh.")

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
        d_meter = load["meter_energy_wh"] - idle["meter_energy_wh"] * scale
        rows.append(
            {
                "trial": trial,
                "cc_idle_w": idle["cc_energy_wh"] * 3600 / idle["duration_s"],
                "meter_idle_w": idle["meter_energy_wh"] * 3600 / idle["duration_s"],
                "cc_load_w": load["cc_energy_wh"] * 3600 / load["duration_s"],
                "meter_load_w": load["meter_energy_wh"] * 3600 / load["duration_s"],
                "cc_delta_wh": d_cc,
                "meter_delta_wh": d_meter,
                "ratio_load": load["cc_energy_wh"] / load["meter_energy_wh"],
                "ratio_delta": d_cc / d_meter if d_meter > 0 else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_report(per_trial: pd.DataFrame, source: Path) -> str:
    """Relatório Markdown com médias e desvios entre tentativas."""
    n = len(per_trial)

    def ms(col: str, spec: str = ".3f") -> str:
        s = per_trial[col]
        sd = f" ± {s.std(ddof=1):{spec}}" if n > 1 else ""
        return f"{s.mean():{spec}}{sd}"

    return "\n".join(
        [
            "# Validação do CodeCarbon com medidor de tomada\n",
            f"Fonte: `{source.as_posix()}` · tentativas: {n}\n",
            "## Resumo (média ± desvio entre tentativas)\n",
            "| Grandeza | CodeCarbon | Medidor |",
            "|---|---|---|",
            f"| Potência em repouso (W) | {ms('cc_idle_w', '.2f')} | {ms('meter_idle_w', '.2f')} |",
            f"| Potência em carga (W) | {ms('cc_load_w', '.2f')} | {ms('meter_load_w', '.2f')} |",
            f"| Energia incremental da carga ΔE (Wh) | {ms('cc_delta_wh')} | {ms('meter_delta_wh')} |",
            "",
            f"- Razão CodeCarbon / medidor, energia absoluta na carga: {ms('ratio_load')}",
            f"- Razão CodeCarbon / medidor, energia incremental ΔE: {ms('ratio_delta')}",
            "",
            "Interpretação: a razão absoluta é afetada por componentes que o "
            "CodeCarbon não vê (tela, carregador, placa-mãe); a razão incremental "
            "indica se o CodeCarbon captura o custo da CARGA, que é o que o GMS "
            "compara entre modelos. Razão incremental próxima de 1 com baixa "
            "dispersão sustenta o uso das estimativas; caso contrário, o texto deve "
            "reportar o fator de correção ou tratar a energia como indicador relativo.",
            "",
            "## Por tentativa\n",
            per_trial.round(4).to_markdown(index=False),
            "",
        ]
    )


# ---------------------------------------------------------------------------
# Coleta (interativa)
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
    phase: str, duration_s: float, meter_mode: str, load: Callable[[], Any]
) -> dict[str, Any]:
    """Mede uma fase com o CodeCarbon e registra as leituras do medidor."""
    from threadpoolctl import threadpool_limits

    from green_ml_score.collectors.codecarbon import GreenMLTracker

    out_dir = OUT_DIR / "codecarbon"
    out_dir.mkdir(parents=True, exist_ok=True)
    tracker = GreenMLTracker(output_dir=str(out_dir), log_level="error")

    meter_start = None
    if meter_mode == "energy":
        meter_start = ask_float(
            f"\n[{phase}] Leitura ACUMULADA do medidor (Wh) e Enter para iniciar: "
        )
    else:
        input(f"\n[{phase}] Enter para iniciar a fase: ")

    print(f"  medindo {phase} por {duration_s:g} s — não use o computador...")
    with threadpool_limits(limits=config.N_JOBS):
        start = time.perf_counter()
        tracker.start()
        try:
            while time.perf_counter() - start < duration_s:
                if phase == "load":
                    load()
                else:
                    time.sleep(0.5)
        finally:
            tracker.stop()
        elapsed = time.perf_counter() - start

    d = tracker.details
    duration = d.duration_s if d.duration_s is not None else elapsed
    if meter_mode == "energy":
        meter_end = ask_float(f"[{phase}] Leitura ACUMULADA do medidor (Wh) agora: ")
        meter_energy = meter_end - meter_start
    else:
        meter_end = None
        meter_energy = (
            ask_float(f"[{phase}] Potência MÉDIA indicada pelo medidor (W): ")
            * duration
            / 3600
        )
    return {
        "phase": phase,
        "duration_s": duration,
        "cc_energy_wh": tracker.energy_kwh * KWH_TO_WH,
        "cc_cpu_wh": None if d.cpu_energy_kwh is None else d.cpu_energy_kwh * KWH_TO_WH,
        "cc_ram_wh": None if d.ram_energy_kwh is None else d.ram_energy_kwh * KWH_TO_WH,
        "cc_tracking_mode": d.tracking_mode,
        "meter_mode": meter_mode,
        "meter_start_wh": meter_start,
        "meter_end_wh": meter_end,
        "meter_energy_wh": meter_energy,
    }


def collect(trials: int, duration_s: float, meter_mode: str) -> Path:
    """Executa as tentativas e grava o CSV bruto."""
    load = make_load()
    load()  # aquecimento, fora da medição
    rows = []
    for trial in range(1, trials + 1):
        print(f"\n=== Tentativa {trial}/{trials} ===")
        for phase in ("idle", "load"):
            rows.append(
                {"trial": trial, **run_phase(phase, duration_s, meter_mode, load)}
            )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"meter_validation_{datetime.now():%Y%m%d_%H%M%S}.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--duration", type=float, default=600.0, help="s por fase")
    parser.add_argument("--meter-mode", choices=["energy", "power"], default="energy")
    parser.add_argument(
        "--analyze", type=Path, default=None, help="Só analisa um CSV já coletado."
    )
    args = parser.parse_args()

    path = args.analyze or collect(args.trials, args.duration, args.meter_mode)
    if not path.exists():
        sys.exit(f"Arquivo não encontrado: {path}")
    report = build_report(analyze(pd.read_csv(path)), path)
    path.with_suffix(".md").write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"[OK] Dados em {path}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
