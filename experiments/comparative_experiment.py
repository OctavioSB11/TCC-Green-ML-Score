"""
comparative_experiment.py — Experimento comparativo do GreenML Score (Seção 5 do TCC).

Protocolo por dataset:
  0a. Baseline de repouso: a máquina é medida sem carga por ``IDLE_BASELINE_S``
      segundos, obtendo-se a potência ociosa P₀.
  0b. Aquecimento: uma execução (treino + inferência) descartada por modelo.
Protocolo por (dataset, semente, modelo):
  1. Divisão treino/teste e pré-processamento dependentes da semente (fora da medição).
  2. Fase de TREINO medida: N ajustes de clones idênticos do estimador.
  3. Fase de INFERÊNCIA medida: N predições sobre o conjunto de teste.
  4. Energia bruta e líquida de repouso (E − P₀·t), tempo de parede e tempo de CPU
     reportados POR REPETIÇÃO.
Ao final, por dataset: GMS sobre a energia bruta de treino por repetição, score
relativo ao modelo de referência (razão de energia e custo marginal em J por ponto
de F1), avisos de procedência e um cartão ambiental por modelo.

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
import warnings
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
from green_ml_score.collectors.codecarbon import (  # noqa: E402
    GreenMLTracker,
    MeasurementDetails,
    MeasurementError,
    ProvenanceWarning,
    provenance_warnings_for,
)
from green_ml_score.reporting import EnvironmentalCard  # noqa: E402
from green_ml_score.scoring.gms import (  # noqa: E402
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
    calculate_gms,
)
from green_ml_score.scoring.relative import (  # noqa: E402
    pareto_dominated,
    relative_to_reference,
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
class IdleBaseline:
    """Medição da máquina em repouso, que define a potência ociosa P₀."""

    power_w: float
    duration_s: float
    energy_kwh: float
    details: MeasurementDetails


@dataclass(frozen=True)
class PhaseMeasurement:
    """Resultado de uma fase medida, normalizado por repetição."""

    energy_kwh: float
    energy_net_kwh: float
    wall_time_s: float
    cpu_time_s: float
    session_s: float
    repetitions: int
    details: MeasurementDetails

    @property
    def tracking_mode(self) -> str | None:
        return self.details.tracking_mode

    @property
    def ram_share(self) -> float | None:
        return self.details.ram_share

    @property
    def cpu_power_w(self) -> float | None:
        return self.details.cpu_power_w

    @property
    def ram_power_w(self) -> float | None:
        return self.details.ram_power_w


def _session_duration(details: MeasurementDetails, fallback_s: float) -> float:
    """Duração da sessão do CodeCarbon (a mesma janela em que a energia foi integrada)."""
    return details.duration_s if details.duration_s is not None else fallback_s


def measure_idle(duration_s: float, tracker_kwargs: dict[str, Any]) -> IdleBaseline:
    """
    Mede a máquina sem carga por ``duration_s`` segundos e devolve P₀ = E / t.

    A sessão inclui o overhead de start/stop do CodeCarbon, assim como as fases
    medidas; com t ≫ overhead, P₀ aproxima a potência ociosa da máquina.

    Raises:
        MeasurementError: se a medição de repouso não registrar energia positiva.
    """
    if duration_s <= 0:
        raise ValueError("duration_s deve ser positivo.")
    tracker = GreenMLTracker(**tracker_kwargs)
    session_start = time.perf_counter()
    tracker.start()
    try:
        time.sleep(duration_s)
    finally:
        tracker.stop()
    session = _session_duration(tracker.details, time.perf_counter() - session_start)
    if tracker.energy_kwh <= 0 or session <= 0:
        raise MeasurementError(
            "A medição de repouso não registrou energia; P₀ indefinida."
        )
    return IdleBaseline(
        power_w=tracker.energy_kwh * KWH_TO_J / session,
        duration_s=session,
        energy_kwh=tracker.energy_kwh,
        details=tracker.details,
    )


def measure_phase(
    action: Callable[[], Any],
    repetitions: int,
    tracker_kwargs: dict[str, Any],
    idle_power_w: float = 0.0,
    min_window_s: float = 0.0,
) -> tuple[PhaseMeasurement, Any]:
    """
    Executa ``action`` sob medição e devolve valores por repetição.

    A ação é repetida ao menos ``repetitions`` vezes E até que a carga ocupe ao
    menos ``min_window_s`` segundos. A janela mínima dilui o overhead fixo de
    start/stop do CodeCarbon (≈ 1,5 s por sessão) e garante que a energia seja
    integrada sobre várias leituras de potência, e não apenas a final; o número
    efetivo de repetições varia por modelo e é reportado.

    A energia líquida desconta P₀ × duração da sessão do CodeCarbon, isto é, a
    energia que a máquina consumiria ociosa na mesma janela. Ela pode ser negativa
    quando o custo da carga é menor que o ruído da medição; esses valores são
    mantidos, e não truncados, para não enviesar as médias.
    """
    tracker = GreenMLTracker(**tracker_kwargs)
    result: Any = None
    with threadpool_limits(limits=config.N_JOBS):
        session_start = time.perf_counter()
        tracker.start()
        try:
            # Cronômetros internos à medição: excluem o overhead de start/stop do tracker
            wall_start, cpu_start = time.perf_counter(), time.process_time()
            done = 0
            while done < repetitions or time.perf_counter() - wall_start < min_window_s:
                result = action()
                done += 1
            wall, cpu = (
                time.perf_counter() - wall_start,
                time.process_time() - cpu_start,
            )
        finally:
            tracker.stop()
        session = _session_duration(
            tracker.details, time.perf_counter() - session_start
        )

    net_kwh = tracker.energy_kwh - idle_power_w * session / KWH_TO_J
    return (
        PhaseMeasurement(
            energy_kwh=tracker.energy_kwh / done,
            energy_net_kwh=net_kwh / done,
            wall_time_s=wall / done,
            cpu_time_s=cpu / done,
            session_s=session,
            repetitions=done,
            details=tracker.details,
        ),
        result,
    )


def warm_up(
    models: dict[str, Any], data: tuple[Any, Any, np.ndarray, np.ndarray]
) -> None:
    """Uma execução não medida (treino + inferência) por modelo, descartada."""
    X_train, X_test, y_train, _ = data
    with threadpool_limits(limits=config.N_JOBS):
        for name, estimator in models.items():
            print(f"  aquecimento: {name}", flush=True)
            clone(estimator).fit(X_train, y_train).predict(X_test)


def run_single(
    model_name: str,
    estimator: Any,
    data: tuple[Any, Any, np.ndarray, np.ndarray],
    repetitions: int,
    tracker_kwargs: dict[str, Any],
    idle_power_w: float = 0.0,
    details_sink: list[MeasurementDetails] | None = None,
    min_window_s: float = 0.0,
) -> dict[str, Any]:
    """
    Mede treino e inferência de um estimador e devolve uma linha de resultados.

    Os detalhes de procedência das duas fases são acrescentados a ``details_sink``.
    """
    X_train, X_test, y_train, y_test = data

    def train_once() -> Any:
        return clone(estimator).fit(X_train, y_train)

    train, fitted = measure_phase(
        train_once, repetitions, tracker_kwargs, idle_power_w, min_window_s
    )
    infer, y_pred = measure_phase(
        lambda: fitted.predict(X_test),
        repetitions,
        tracker_kwargs,
        idle_power_w,
        min_window_s,
    )
    if details_sink is not None:
        details_sink.extend([train.details, infer.details])

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
        "train_repetitions": train.repetitions,
        "infer_repetitions": infer.repetitions,
        "min_window_s": min_window_s,
        # Treino (por repetição) — base do GMS
        "energy_kwh": train.energy_kwh,
        "energy_j": train.energy_kwh * KWH_TO_J,
        "energy_net_kwh": train.energy_net_kwh,
        "energy_net_j": train.energy_net_kwh * KWH_TO_J,
        "carbon_kg": carbon_kg,
        "water_liters": water_l,
        "train_wall_time_s": train.wall_time_s,
        "train_cpu_time_s": train.cpu_time_s,
        "train_session_s": train.session_s,
        # Inferência (por repetição)
        "infer_energy_kwh": infer.energy_kwh,
        "infer_energy_net_kwh": infer.energy_net_kwh,
        "infer_energy_j_per_1k": infer.energy_kwh * KWH_TO_J / n_test * 1000,
        "infer_session_s": infer.session_s,
        "idle_power_w": idle_power_w,
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


def add_relative_scores(df: pd.DataFrame, reference: str) -> pd.DataFrame:
    """
    Score relativo à referência, pareado por semente: razão de energia, ΔF1 (pontos),
    custo marginal (J por ponto de F1), quadrante em relação à referência e
    dominância de Pareto (F1 × energia) entre todos os modelos da mesma semente.

    Raises:
        ValueError: se a referência não tiver sido executada em alguma semente.
    """
    out = df.copy()
    ref = df[df["model_name"] == reference].set_index("seed")
    missing = set(df["seed"]) - set(ref.index)
    if missing:
        raise ValueError(
            f"Modelo de referência '{reference}' ausente nas sementes {sorted(missing)}."
        )
    scores = [
        relative_to_reference(
            r.energy_kwh,
            r.f1_macro,
            ref.at[r.seed, "energy_kwh"],
            ref.at[r.seed, "f1_macro"],
            is_reference=r.model_name == reference,
        )
        for r in df.itertuples()
    ]
    out["reference_model"] = reference
    out["energy_ratio_ref"] = [s.energy_ratio for s in scores]
    out["delta_f1_points"] = [s.delta_f1_points for s in scores]
    out["marginal_cost_j_per_f1_point"] = [
        s.marginal_cost_j_per_f1_point for s in scores
    ]
    out["position_vs_ref"] = [s.position for s in scores]
    out["dominated"] = False
    for _, idx in df.groupby("seed").groups.items():
        g = df.loc[idx]
        out.loc[idx, "dominated"] = pareto_dominated(g["energy_kwh"], g["f1_macro"])
    out["dominated"] = out["dominated"].astype(bool)
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
                "Energia líquida mWh (Mediana)": g["energy_net_kwh"].median()
                * KWH_TO_MWH,
                "Inferência J/1k amostras (Média)": g["infer_energy_j_per_1k"].mean(),
                "Carbono kg (Média)": g["carbon_kg"].mean(),
                "Água L (Média)": g["water_liters"].mean(),
                "GreenML Score (Média)": g["gms"].mean(),
                "GreenML Score (Std)": g["gms"].std(ddof=1),
                "GreenML Score (Mediana)": g["gms"].median(),
                "GreenML Score (IQR)": _iqr(g["gms"]),
                "E/E_ref (Mediana)": g["energy_ratio_ref"].median(),
                "Custo marginal J/ponto F1 (Mediana)": g[
                    "marginal_cost_j_per_f1_point"
                ].median(),
                "Dominado (fração)": g["dominated"].mean(),
            }
        )
    return pd.DataFrame(rows).sort_values("GreenML Score (Média)", ascending=False)


def build_cards(
    df: pd.DataFrame,
    dataset: str,
    carbon_intensity: float,
    wue: float,
    warnings_: list[str],
) -> dict[str, EnvironmentalCard]:
    """Um cartão ambiental por modelo a partir dos resultados por semente."""

    def std(s: pd.Series) -> float | None:
        return float(s.std(ddof=1)) if len(s) > 1 else None

    cards = {}
    for model, g in df.groupby("model_name"):
        cards[str(model)] = EnvironmentalCard(
            model=str(model),
            dataset=dataset,
            n_runs=len(g),
            accuracy_mean=float(g["accuracy"].mean()),
            accuracy_std=std(g["accuracy"]),
            f1_mean=float(g["f1_macro"].mean()),
            f1_std=std(g["f1_macro"]),
            train_energy_median_kwh=float(g["energy_kwh"].median()),
            train_energy_iqr_kwh=_iqr(g["energy_kwh"]) if len(g) > 1 else None,
            train_wall_time_median_s=float(g["train_wall_time_s"].median()),
            carbon_median_kg=float(g["carbon_kg"].median()),
            water_median_l=float(g["water_liters"].median()),
            gms_median=float(g["gms"].median()),
            carbon_intensity_g_per_kwh=carbon_intensity,
            wue_l_per_kwh=wue,
            train_energy_net_median_kwh=float(g["energy_net_kwh"].median()),
            idle_power_w=float(g["idle_power_w"].iloc[0]),
            infer_energy_j_per_1k_median=float(g["infer_energy_j_per_1k"].median()),
            reference_model=str(g["reference_model"].iloc[0]),
            energy_ratio_median=float(g["energy_ratio_ref"].median()),
            marginal_cost_median_j_per_f1_point=float(
                g["marginal_cost_j_per_f1_point"].median()
            ),
            dominated_share=float(g["dominated"].mean()),
            tracking_modes=sorted(str(x) for x in g["tracking_mode"].dropna().unique()),
            ram_share_median=(
                float(g["ram_energy_share"].median())
                if g["ram_energy_share"].notna().any()
                else None
            ),
            provenance_warnings=warnings_,
        )
    return cards


def _git_commit() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_outputs(
    out_dir: Path,
    df: pd.DataFrame,
    summary: pd.DataFrame,
    meta: dict[str, Any],
    cards: dict[str, EnvironmentalCard] | None = None,
) -> None:
    """Grava resultados brutos SEM arredondamento, o resumo, os cartões e os metadados."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if cards:
        (out_dir / "cards").mkdir(exist_ok=True)
        for model, card in cards.items():
            (out_dir / "cards" / f"{model}.md").write_text(
                card.to_markdown(), encoding="utf-8"
            )
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
        default=config.CARBON_INTENSITY_BR_2024,
        help="gCO2e/kWh",
    )
    parser.add_argument(
        "--wue", type=float, default=config.WUE_MICROSOFT_FY24, help="L/kWh"
    )
    parser.add_argument(
        "--no-mlflow", action="store_true", help="Não registra no MLflow."
    )
    parser.add_argument(
        "--idle-seconds",
        type=float,
        default=None,
        help="Duração da medição de repouso (P₀). Padrão: 60 s (10 s no quick-run).",
    )
    parser.add_argument(
        "--min-window",
        type=float,
        default=None,
        help="Janela mínima de cada fase medida, em s. Padrão: 30 s (5 s no quick-run).",
    )
    parser.add_argument(
        "--no-warmup",
        action="store_true",
        help="Não executa o aquecimento descartado por modelo.",
    )
    parser.add_argument(
        "--reference-model",
        default=config.REFERENCE_MODEL,
        help="Modelo de referência para o score relativo.",
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
    idle_power_w: float = 0.0,
    warmup: bool = True,
    details_sink: list[MeasurementDetails] | None = None,
    min_window_s: float = 0.0,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for i, seed in enumerate(seeds):
        X_tr_raw, X_te_raw, y_tr, y_te = split_dataset(raw, seed)
        X_tr, X_te, _ = preprocess_features(X_tr_raw, X_te_raw, raw.is_text)
        models = get_models(include_all, random_state=seed, n_jobs=config.N_JOBS)
        if warmup and i == 0:
            warm_up(models, (X_tr, X_te, y_tr, y_te))
        order = np.random.default_rng(seed).permutation(list(models))

        for model_name in order:
            print(f"  seed={seed:<5} {model_name:<20}", end=" ", flush=True)
            row = run_single(
                str(model_name),
                models[model_name],
                (X_tr, X_te, y_tr, y_te),
                repetitions,
                tracker_kwargs,
                idle_power_w,
                details_sink,
                min_window_s,
            )
            row.update({"dataset": raw.name, "seed": seed})
            rows.append(row)
            print(
                f"acc={row['accuracy']:.4f}  E_treino={row['energy_j']:.2f} J  "
                f"(líquida {row['energy_net_j']:.2f} J)  "
                f"t={row['train_wall_time_s']:.2f} s  reps={row['train_repetitions']}"
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
    idle_seconds = args.idle_seconds or (
        config.QUICK_RUN_IDLE_BASELINE_S if args.quick_run else config.IDLE_BASELINE_S
    )
    warmup = config.WARMUP and not args.no_warmup
    min_window_s = (
        args.min_window
        if args.min_window is not None
        else (
            config.QUICK_RUN_MIN_WINDOW_S
            if args.quick_run
            else config.MIN_MEASUREMENT_WINDOW_S
        )
    )

    if not args.no_mlflow:
        import mlflow

        mlflow.set_experiment(config.MLFLOW_EXPERIMENT_NAME)

    for name in datasets:
        print(
            f"\n=== {name.upper()} | modo={mode} | seeds={seeds} | repetições≥{repetitions} | janela≥{min_window_s:g} s"
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
        print(f"  repouso: medindo P₀ por {idle_seconds:g} s (não use a máquina)...")
        idle = measure_idle(idle_seconds, tracker_kwargs)
        print(f"  P₀ = {idle.power_w:.2f} W")

        details: list[MeasurementDetails] = [idle.details]
        df = run_dataset(
            raw,
            seeds,
            args.models == "all",
            repetitions,
            tracker_kwargs,
            not args.no_mlflow,
            idle_power_w=idle.power_w,
            warmup=warmup,
            details_sink=details,
            min_window_s=min_window_s,
        )
        df = add_relative_scores(add_gms(df), args.reference_model)
        summary = summarize(df)

        provenance = provenance_warnings_for(details)
        for message in provenance:
            warnings.warn(message, ProvenanceWarning, stacklevel=1)
        cards = build_cards(df, name, args.carbon_intensity, args.wue, provenance)
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
            "warmup": warmup,
            "min_window_s": min_window_s,
            "reference_model": args.reference_model,
            "idle_baseline": {
                "power_w": idle.power_w,
                "duration_s": idle.duration_s,
                "energy_kwh": idle.energy_kwh,
                "tracking_mode": idle.details.tracking_mode,
            },
            "provenance_warnings": provenance,
        }
        write_outputs(out_dir, df, summary, meta, cards)
        print(f"[OK] Resultados em {out_dir}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
