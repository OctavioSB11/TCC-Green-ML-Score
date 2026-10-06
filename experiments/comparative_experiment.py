"""
comparative_experiment.py — Experimento comparativo do GreenML Score (Seção 5 do TCC).

Protocolo por (dataset, semente, modelo):
  1. Divisão treino/teste e pré-processamento dependentes da semente (fora da medição).
  2. Fase de TREINO medida: N ajustes de clones idênticos do estimador.
  3. Fase de INFERÊNCIA medida: N predições sobre o conjunto de teste.
  4. Energia, tempo de parede e tempo de CPU reportados POR REPETIÇÃO.
O GMS é calculado ao final, por dataset, sobre a energia de treino por repetição.

Todos os modelos usam o mesmo grau de paralelismo (config.N_JOBS), inclusive nas
bibliotecas numéricas (BLAS/OpenMP), e a ordem dos modelos é sorteada a cada
semente para não acumular efeitos sistemáticos de ordem de execução.

Uso:
    python experiments/comparative_experiment.py --quick-run --dataset breast_cancer
    python experiments/comparative_experiment.py --dataset newsgroups
    python experiments/comparative_experiment.py --dataset all --seeds 42 123 2024
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neural_network import MLPClassifier
from threadpoolctl import threadpool_limits

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from experiments.config import config  # noqa: E402
from experiments.dataset import (  # noqa: E402
    RawDataset,
    load_raw_dataset,
    preprocess_features,
    split_dataset,
)
from green_ml_score.collectors.codecarbon import GreenMLTracker  # noqa: E402
from green_ml_score.scoring.gms import (  # noqa: E402
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
    calculate_gms,
)

KWH_TO_J: float = 3.6e6
KWH_TO_MWH: float = 1e6  # 1 kWh = 1.000.000 mWh


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------


def get_models(include_all: bool, random_state: int, n_jobs: int) -> dict[str, Any]:
    """Estimadores avaliados, todos com o mesmo grau de paralelismo."""
    models: dict[str, Any] = {
        "Logistic_Regression": LogisticRegression(
            max_iter=1000, random_state=random_state
        ),
        "Random_Forest": RandomForestClassifier(
            n_estimators=100, random_state=random_state, n_jobs=n_jobs
        ),
    }
    if include_all:
        try:
            from xgboost import XGBClassifier
        except ImportError as exc:
            raise ImportError(
                "XGBoost é obrigatório com --models all: pip install xgboost"
            ) from exc
        models["XGBoost"] = XGBClassifier(
            n_estimators=100,
            random_state=random_state,
            n_jobs=n_jobs,
            eval_metric="logloss",
        )
        models["MLP_Neural_Network"] = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            max_iter=200,
            random_state=random_state,
            early_stopping=True,
        )
    return models


# ---------------------------------------------------------------------------
# Medição
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PhaseMeasurement:
    """Resultado de uma fase medida, normalizado por repetição."""

    energy_kwh: float
    wall_time_s: float
    cpu_time_s: float
    tracking_mode: str | None
    ram_share: float | None
    cpu_power_w: float | None
    ram_power_w: float | None


def measure_phase(
    action: Callable[[], Any], repetitions: int, tracker_kwargs: dict[str, Any]
) -> tuple[PhaseMeasurement, Any]:
    """Executa ``action`` N vezes sob medição e devolve valores por repetição."""
    tracker = GreenMLTracker(**tracker_kwargs)
    result: Any = None
    with threadpool_limits(limits=config.N_JOBS):
        tracker.start()
        try:
            # Cronômetros internos à medição: excluem o overhead de start/stop do tracker
            wall_start, cpu_start = time.perf_counter(), time.process_time()
            for _ in range(repetitions):
                result = action()
            wall, cpu = (
                time.perf_counter() - wall_start,
                time.process_time() - cpu_start,
            )
        finally:
            tracker.stop()

    d = tracker.details
    return (
        PhaseMeasurement(
            energy_kwh=tracker.energy_kwh / repetitions,
            wall_time_s=wall / repetitions,
            cpu_time_s=cpu / repetitions,
            tracking_mode=d.tracking_mode,
            ram_share=d.ram_share,
            cpu_power_w=d.cpu_power_w,
            ram_power_w=d.ram_power_w,
        ),
        result,
    )


def run_single(
    model_name: str,
    estimator: Any,
    data: tuple[Any, Any, np.ndarray, np.ndarray],
    repetitions: int,
    tracker_kwargs: dict[str, Any],
) -> dict[str, Any]:
    """Mede treino e inferência de um estimador e devolve uma linha de resultados."""
    X_train, X_test, y_train, y_test = data

    def train_once() -> Any:
        return clone(estimator).fit(X_train, y_train)

    train, fitted = measure_phase(train_once, repetitions, tracker_kwargs)
    infer, y_pred = measure_phase(
        lambda: fitted.predict(X_test), repetitions, tracker_kwargs
    )

    carbon_kg = train.energy_kwh * tracker_kwargs["carbon_intensity_g_per_kwh"] / 1000.0
    water_l = train.energy_kwh * tracker_kwargs["wue_liters_per_kwh"]
    n_test = X_test.shape[0]

    return {
        "model_name": model_name,
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_macro": f1_score(y_test, y_pred, average="macro"),
        "n_train": X_train.shape[0],
        "n_test": n_test,
        "repetitions": repetitions,
        # Treino (por repetição) — base do GMS
        "energy_kwh": train.energy_kwh,
        "energy_j": train.energy_kwh * KWH_TO_J,
        "carbon_kg": carbon_kg,
        "water_liters": water_l,
        "train_wall_time_s": train.wall_time_s,
        "train_cpu_time_s": train.cpu_time_s,
        # Inferência (por repetição)
        "infer_energy_kwh": infer.energy_kwh,
        "infer_energy_j_per_1k": infer.energy_kwh * KWH_TO_J / n_test * 1000,
        "infer_wall_time_s": infer.wall_time_s,
        "infer_cpu_time_s": infer.cpu_time_s,
        # Procedência da medição
        "tracking_mode": train.tracking_mode,
        "ram_energy_share": train.ram_share,
        "cpu_power_w": train.cpu_power_w,
        "ram_power_w": train.ram_power_w,
    }


# ---------------------------------------------------------------------------
# Agregação e persistência
# ---------------------------------------------------------------------------


def add_gms(df: pd.DataFrame) -> pd.DataFrame:
    """GMS (0–100) sobre a energia de treino, com limites definidos no próprio conjunto."""
    metrics = [
        EnvironmentalMetrics(r.energy_kwh, r.carbon_kg, r.water_liters)
        for r in df.itertuples()
    ]
    bounds = NormalizationBounds.from_metrics_list(metrics)
    out = df.copy()
    out["gms"] = [calculate_gms(m, bounds, Weights(), scale_100=True) for m in metrics]
    return out


def _iqr(s: pd.Series) -> float:
    return float(s.quantile(0.75) - s.quantile(0.25))


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo por modelo para apresentação (energia em mWh; médias, desvios, medianas e IQR)."""
    rows = []
    for model, g in df.groupby("model_name"):
        rows.append(
            {
                "Modelo": model,
                "N": len(g),
                "Acurácia (Média)": g["accuracy"].mean(),
                "Acurácia (Std)": g["accuracy"].std(ddof=1),
                "F1-Score (Média)": g["f1_macro"].mean(),
                "Tempo s (Média)": g["train_wall_time_s"].mean(),
                "Tempo CPU s (Média)": g["train_cpu_time_s"].mean(),
                "Energia kWh (Média)": g["energy_kwh"].mean(),
                "Energia mWh (Média)": g["energy_kwh"].mean() * KWH_TO_MWH,
                "Energia mWh (Mediana)": g["energy_kwh"].median() * KWH_TO_MWH,
                "Energia mWh (IQR)": _iqr(g["energy_kwh"]) * KWH_TO_MWH,
                "Inferência J/1k amostras (Média)": g["infer_energy_j_per_1k"].mean(),
                "Carbono kg (Média)": g["carbon_kg"].mean(),
                "Água L (Média)": g["water_liters"].mean(),
                "GreenML Score (Média)": g["gms"].mean(),
                "GreenML Score (Std)": g["gms"].std(ddof=1),
                "GreenML Score (Mediana)": g["gms"].median(),
                "GreenML Score (IQR)": _iqr(g["gms"]),
            }
        )
    return pd.DataFrame(rows).sort_values("GreenML Score (Média)", ascending=False)


def _git_commit() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_outputs(
    out_dir: Path, df: pd.DataFrame, summary: pd.DataFrame, meta: dict[str, Any]
) -> None:
    """Grava resultados brutos SEM arredondamento, o resumo e os metadados da execução."""
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "comparative_results.csv", index=False)
    summary.to_csv(out_dir / "summary_metrics.csv", index=False)
    with open(out_dir / "summary_table.md", "w", encoding="utf-8") as f:
        f.write(f"# Resumo — {meta['dataset']} ({meta['mode']})\n\n")
        f.write(summary.round(4).to_markdown(index=False))
        f.write("\n")
    with open(out_dir / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Experimento comparativo do GreenML Score."
    )
    parser.add_argument(
        "--quick-run",
        action="store_true",
        help="Subconjunto reduzido, 1 semente e 1 repetição (validação).",
    )
    parser.add_argument("--models", default="all", choices=["sklearn", "all"])
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    parser.add_argument(
        "--dataset", default="all", choices=["all", *config.AVAILABLE_DATASETS]
    )
    parser.add_argument(
        "--carbon-intensity",
        type=float,
        default=config.CARBON_INTENSITY_SAO_PAULO,
        help="gCO2e/kWh",
    )
    parser.add_argument(
        "--wue", type=float, default=config.WUE_GOOGLE_2024, help="L/kWh"
    )
    parser.add_argument(
        "--no-mlflow", action="store_true", help="Não registra no MLflow."
    )
    return parser.parse_args()


def log_to_mlflow(row: dict[str, Any], dataset: str, seed: int) -> None:
    import mlflow

    with mlflow.start_run(run_name=f"{dataset}_{row['model_name']}_seed_{seed}"):
        mlflow.log_params(
            {
                "dataset": dataset,
                "seed": seed,
                "model_name": row["model_name"],
                "repetitions": row["repetitions"],
                "n_jobs": config.N_JOBS,
                "tracking_mode": row["tracking_mode"],
            }
        )
        mlflow.log_metrics(
            {
                k: v
                for k, v in row.items()
                if isinstance(v, (int, float))
                and v == v
                and k not in {"seed", "repetitions"}
            }
        )


def run_dataset(
    raw: RawDataset,
    seeds: list[int],
    include_all: bool,
    repetitions: int,
    tracker_kwargs: dict[str, Any],
    use_mlflow: bool,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        X_tr_raw, X_te_raw, y_tr, y_te = split_dataset(raw, seed)
        X_tr, X_te, _ = preprocess_features(X_tr_raw, X_te_raw, raw.is_text)
        models = get_models(include_all, random_state=seed, n_jobs=config.N_JOBS)
        order = np.random.default_rng(seed).permutation(list(models))

        for model_name in order:
            print(f"  seed={seed:<5} {model_name:<20}", end=" ", flush=True)
            row = run_single(
                str(model_name),
                models[model_name],
                (X_tr, X_te, y_tr, y_te),
                repetitions,
                tracker_kwargs,
            )
            row.update({"dataset": raw.name, "seed": seed})
            rows.append(row)
            print(
                f"acc={row['accuracy']:.4f}  E_treino={row['energy_j']:.2f} J  "
                f"t={row['train_wall_time_s']:.2f} s"
            )
            if use_mlflow:
                log_to_mlflow(row, raw.name, seed)
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    seeds = args.seeds or ([config.SEEDS[0]] if args.quick_run else config.SEEDS)
    repetitions = (
        config.QUICK_RUN_REPETITIONS if args.quick_run else config.WORKLOAD_REPETITIONS
    )
    datasets = config.AVAILABLE_DATASETS if args.dataset == "all" else [args.dataset]
    mode = "quick_run" if args.quick_run else "full"

    if not args.no_mlflow:
        import mlflow

        mlflow.set_experiment(config.MLFLOW_EXPERIMENT_NAME)

    for name in datasets:
        print(
            f"\n=== {name.upper()} | modo={mode} | seeds={seeds} | repetições={repetitions}"
        )
        raw = load_raw_dataset(name, quick_run=args.quick_run)
        out_dir = Path(config.RESULTS_DIR) / name / mode
        tracker_kwargs = {
            "carbon_intensity_g_per_kwh": args.carbon_intensity,
            "wue_liters_per_kwh": args.wue,
            "output_dir": str(out_dir / "codecarbon"),
            "log_level": "error",
        }
        (out_dir / "codecarbon").mkdir(parents=True, exist_ok=True)

        started = datetime.now(timezone.utc).isoformat()
        df = add_gms(
            run_dataset(
                raw,
                seeds,
                args.models == "all",
                repetitions,
                tracker_kwargs,
                not args.no_mlflow,
            )
        )
        summary = summarize(df)
        print(
            summary[
                [
                    "Modelo",
                    "Acurácia (Média)",
                    "Energia mWh (Mediana)",
                    "GreenML Score (Mediana)",
                ]
            ]
            .round(3)
            .to_string(index=False)
        )

        meta = {
            "dataset": name,
            "mode": mode,
            "seeds": seeds,
            "repetitions": repetitions,
            "n_samples": int(len(raw.y)),
            "started_utc": started,
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "git_commit": _git_commit(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "config": asdict(config),
            "carbon_intensity_g_per_kwh": args.carbon_intensity,
            "wue_l_per_kwh": args.wue,
        }
        write_outputs(out_dir, df, summary, meta)
        print(f"[OK] Resultados em {out_dir}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
