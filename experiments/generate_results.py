"""
generate_results.py — Figuras e tabelas de cada execução do experimento (semana 4).

Uso:
    python experiments/generate_results.py                 # todas as execuções full
    python experiments/generate_results.py --mode quick_run
    python experiments/generate_results.py --results experiments/results/newsgroups/full

Lê ``comparative_results.csv`` (uma linha por semente × modelo) e grava em
``docs/Results/<dataset>/<modo>/``:
  - ``energy_time``: energia de treino por execução (bruta e líquida de repouso,
    mediana e IQR, escala log) e tempo de parede;
  - ``pareto_energy_f1``: F1 × energia, com a fronteira de Pareto e a referência;
  - ``gms_barchart``: GMS (mediana e IQR) — com IC e WUE constantes, o GMS é
    função só da energia (ver ``tests/test_gms_properties.py``);
  - ``summary_table.tex`` (booktabs) e ``README.md`` descritivo.

Nenhum valor é digitado à mão: rótulos, número de sementes e limites dos eixos
vêm dos dados. Diretórios iniciados por ``_`` (legado) são ignorados.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from experiments.labels import (  # noqa: E402
    comma,
    comma_formatter,
    figure_title,
    model_name,
)
from green_ml_score.scoring.relative import pareto_dominated  # noqa: E402

RESULTS_DIR = Path("experiments/results")
FIGURES_DIR = Path("docs/Results")
KWH_TO_J: float = 3.6e6
KWH_TO_MWH: float = 1e6
J_TO_MWH: float = 1 / 3.6

plt.rcParams.update(
    {
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.grid": True,
        "grid.linestyle": "--",
        "grid.alpha": 0.4,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)

PALETTE: dict[str, str] = {
    "Logistic_Regression": "#2ca02c",
    "Random_Forest": "#1f77b4",
    "MLP_Neural_Network": "#ff7f0e",
    "XGBoost": "#d62728",
}


def _name(model: str) -> str:
    return model_name(model)


def _color(model: str) -> str:
    return PALETTE.get(model, "#4c72b0")


def _save(fig: plt.Figure, out_dir: Path, stem: str) -> None:
    for ext in ("png", "svg"):
        fig.savefig(out_dir / f"{stem}.{ext}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Agregação
# ---------------------------------------------------------------------------


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """Estatísticas por modelo a partir das linhas por semente (energia em J)."""

    def q(s: pd.Series, p: float) -> float:
        return float(s.quantile(p))

    rows = []
    for model, g in df.groupby("model_name"):
        e = g["energy_kwh"] * KWH_TO_J
        row = {
            "model": str(model),
            "n": len(g),
            "accuracy_mean": g["accuracy"].mean(),
            "accuracy_std": g["accuracy"].std(ddof=1),
            "f1_mean": g["f1_macro"].mean(),
            "f1_std": g["f1_macro"].std(ddof=1),
            "energy_j_median": e.median(),
            "energy_j_q1": q(e, 0.25),
            "energy_j_q3": q(e, 0.75),
            "time_s_median": g["train_wall_time_s"].median(),
            "time_s_q1": q(g["train_wall_time_s"], 0.25),
            "time_s_q3": q(g["train_wall_time_s"], 0.75),
            "gms_median": g["gms"].median(),
            "gms_q1": q(g["gms"], 0.25),
            "gms_q3": q(g["gms"], 0.75),
        }
        if "energy_net_kwh" in g:
            en = g["energy_net_kwh"] * KWH_TO_J
            row.update(
                energy_net_j_median=en.median(),
                energy_net_j_q1=q(en, 0.25),
                energy_net_j_q3=q(en, 0.75),
            )
        if "energy_ratio_ref" in g:
            row.update(
                energy_ratio_median=g["energy_ratio_ref"].median(),
                marginal_cost_median=g["marginal_cost_j_per_f1_point"].median(),
                dominated_share=g["dominated"].mean(),
                is_reference=bool((g["model_name"] == g["reference_model"]).all()),
            )
        if "train_repetitions" in g:
            row["train_repetitions_median"] = g["train_repetitions"].median()
        rows.append(row)
    return pd.DataFrame(rows).sort_values("energy_j_median").reset_index(drop=True)


def pareto_front(energy: np.ndarray, f1: np.ndarray) -> np.ndarray:
    """
    Máscara dos pontos não dominados (menor energia E maior F1).

    Um ponto é dominado se outro tem energia ≤ e F1 ≥, com ao menos uma desigualdade
    estrita.
    """
    return ~pareto_dominated(energy, f1)


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------


def _err(center: pd.Series, lo: pd.Series, hi: pd.Series) -> np.ndarray:
    return np.vstack([center - lo, hi - center]).clip(min=0)


def plot_energy_time(agg: pd.DataFrame, out_dir: Path, title: str) -> None:
    """Energia de treino (bruta e líquida) e tempo de parede por modelo."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    labels = [_name(m) for m in agg["model"]]
    x = np.arange(len(agg))
    colors = [_color(m) for m in agg["model"]]
    has_net = "energy_net_j_median" in agg
    w = 0.38 if has_net else 0.6

    ax1.bar(
        x - (w / 2 if has_net else 0),
        agg["energy_j_median"] * J_TO_MWH,
        w,
        yerr=_err(agg["energy_j_median"], agg["energy_j_q1"], agg["energy_j_q3"])
        * J_TO_MWH,
        color=colors,
        edgecolor="black",
        capsize=4,
        label="bruta",
    )
    if has_net:
        net = agg["energy_net_j_median"] * J_TO_MWH
        positive = net > 0
        ax1.bar(
            x[positive] + w / 2,
            net[positive],
            w,
            color=[c for c, p in zip(colors, positive) if p],
            edgecolor="black",
            hatch="//",
            alpha=0.6,
            label="líquida (E − P₀·t)",
        )
        for xi, v in zip(x[~positive], net[~positive]):
            ax1.annotate(
                f"líq. {comma(v, 3)} mWh",
                (xi + w / 2, agg["energy_j_median"].min() * J_TO_MWH),
                ha="center",
                va="bottom",
                fontsize=7,
                rotation=90,
            )
        ax1.legend(fontsize=8)
    ax1.set_yscale("log")
    ax1.set_xticks(x, labels, rotation=20, ha="right")
    ax1.set_ylabel("Energia de treino por execução (mWh, escala log)")
    ax1.set_title("Energia (mediana; barras: IQR)")

    ax2.bar(
        x,
        agg["time_s_median"],
        0.6,
        yerr=_err(agg["time_s_median"], agg["time_s_q1"], agg["time_s_q3"]),
        color=colors,
        edgecolor="black",
        capsize=4,
    )
    ax2.set_yscale("log")
    ax2.set_xticks(x, labels, rotation=20, ha="right")
    ax2.set_ylabel("Tempo de parede por treino (s, escala log)")
    ax2.set_title("Tempo (mediana; barras: IQR)")
    fig.suptitle(title, fontweight="bold")
    fig.tight_layout()
    _save(fig, out_dir, "energy_time")


def plot_pareto(agg: pd.DataFrame, out_dir: Path, title: str) -> None:
    """F1 × energia, com fronteira de Pareto e o modelo de referência destacado."""
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    front = pareto_front(agg["energy_j_median"].to_numpy(), agg["f1_mean"].to_numpy())
    for i, r in agg.iterrows():
        ax.errorbar(
            r["energy_j_median"] * J_TO_MWH,
            r["f1_mean"],
            xerr=_err(
                pd.Series([r["energy_j_median"]]),
                pd.Series([r["energy_j_q1"]]),
                pd.Series([r["energy_j_q3"]]),
            )
            * J_TO_MWH,
            yerr=0 if np.isnan(r["f1_std"]) else r["f1_std"],
            fmt="*" if r.get("is_reference", False) else "o",
            markersize=14 if r.get("is_reference", False) else 9,
            color=_color(r["model"]),
            markeredgecolor="black",
            capsize=4,
            label=_name(r["model"])
            + (" (referência)" if r.get("is_reference", False) else "")
            + ("" if front[i] else " (dominado)"),
            zorder=3,
        )
    pts = agg.loc[front].sort_values("energy_j_median")
    ax.step(
        pts["energy_j_median"] * J_TO_MWH,
        pts["f1_mean"],
        where="post",
        color="gray",
        linestyle=":",
        label="fronteira de Pareto",
        zorder=2,
    )
    ax.set_xscale("log")
    ax.set_xlabel("Energia de treino por execução (mWh, mediana, escala log)")
    ax.set_ylabel("F1-Score macro (média ± desvio)")
    ax.yaxis.set_major_formatter(comma_formatter(2))
    ax.set_title(title)
    ax.legend(
        fontsize=8,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=2,
        frameon=False,
    )
    fig.tight_layout()
    _save(fig, out_dir, "pareto_energy_f1")


def plot_gms(agg: pd.DataFrame, out_dir: Path, title: str) -> None:
    """GMS (mediana e IQR) por modelo."""
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    order = agg.sort_values("gms_median")
    ax.barh(
        [_name(m) for m in order["model"]],
        order["gms_median"],
        xerr=_err(order["gms_median"], order["gms_q1"], order["gms_q3"]),
        color=[_color(m) for m in order["model"]],
        edgecolor="black",
        capsize=4,
    )
    ax.set_xlim(0, 105)
    ax.set_xlabel("GreenML Score (0–100; mediana, barras: IQR)")
    ax.set_title(title)
    fig.text(
        0.01,
        -0.04,
        "Com IC e WUE constantes, GMS = 100·(1 − E/E_max): o ranking coincide com o de energia.",
        fontsize=7.5,
        style="italic",
    )
    fig.tight_layout()
    _save(fig, out_dir, "gms_barchart")


# ---------------------------------------------------------------------------
# Tabelas
# ---------------------------------------------------------------------------


def _iqr_text(c: float, lo: float, hi: float, spec: str) -> str:
    return f"{c:{spec}} [{lo:{spec}}; {hi:{spec}}]"


def latex_table(agg: pd.DataFrame, dataset: str, mode: str) -> str:
    """Tabela booktabs: qualidade, energia, tempo, score relativo e GMS."""
    n = int(agg["n"].max())
    has_rel = "energy_ratio_median" in agg
    cols = "lcccccc" + ("ccc" if has_rel else "")
    head = (
        r"\textbf{Modelo} & \textbf{Acurácia} & \textbf{F1} & "
        r"\textbf{Energia (J)} & \textbf{Líquida (J)} & \textbf{Tempo (s)} & "
        r"\textbf{GMS}"
    )
    if has_rel:
        head += r" & \textbf{$E/E_{ref}$} & \textbf{J/ponto F1} & \textbf{Dominado}"
    tex_dataset = dataset.replace("_", r"\_")
    tex_mode = mode.replace("_", "-")
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        rf"\caption{{Resultados no dataset {tex_dataset} ({tex_mode}): "
        rf"média $\pm$ desvio (acurácia, F1) e mediana [Q1; Q3] (energia, tempo, GMS) "
        rf"sobre {n} semente(s). Energia de treino por execução. Dominado: fração "
        rf"das sementes em que outro modelo tem F1 $\geq$ e energia $\leq$, com "
        rf"ao menos uma desigualdade estrita; J/ponto F1 só é definido com ganho de F1.}}",
        rf"\label{{tab:resultados_{dataset}_{mode}}}",
        rf"\begin{{tabular}}{{{cols}}}",
        r"\toprule",
        head + r" \\",
        r"\midrule",
    ]
    for _, r in agg.iterrows():

        def pm(m: float, s: float) -> str:
            return f"{m:.4f}" + ("" if np.isnan(s) else f" $\\pm$ {s:.4f}")

        cells = [
            _name(r["model"]),
            pm(r["accuracy_mean"], r["accuracy_std"]),
            pm(r["f1_mean"], r["f1_std"]),
            _iqr_text(r["energy_j_median"], r["energy_j_q1"], r["energy_j_q3"], ".3g"),
            (
                f"{r['energy_net_j_median']:.3g}"
                if "energy_net_j_median" in r and not np.isnan(r["energy_net_j_median"])
                else "--"
            ),
            f"{r['time_s_median']:.3g}",
            _iqr_text(r["gms_median"], r["gms_q1"], r["gms_q3"], ".1f"),
        ]
        if has_rel:
            cost = r["marginal_cost_median"]
            cells += [
                f"{r['energy_ratio_median']:.3g}",
                (
                    "ref."
                    if r["is_reference"]
                    else ("--" if np.isnan(cost) else f"{cost:.3g}")
                ),
                f"{r['dominated_share']:.0%}".replace("%", r"\%"),
            ]
        lines.append(" & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


def readme(agg: pd.DataFrame, dataset: str, mode: str) -> str:
    """README descritivo, sem conclusões pré-redigidas."""
    show = agg.rename(
        columns={
            "model": "Modelo",
            "n": "N",
            "f1_mean": "F1 (média)",
            "energy_j_median": "Energia J (mediana)",
            "energy_net_j_median": "Líquida J (mediana)",
            "time_s_median": "Tempo s (mediana)",
            "gms_median": "GMS (mediana)",
            "energy_ratio_median": "E/E_ref (mediana)",
            "marginal_cost_median": "J/ponto F1 (mediana)",
            "dominated_share": "Dominado (fração)",
            "train_repetitions_median": "Repetições de treino (mediana)",
        }
    )
    keep = [
        c
        for c in [
            "Modelo",
            "N",
            "F1 (média)",
            "Energia J (mediana)",
            "Líquida J (mediana)",
            "Tempo s (mediana)",
            "GMS (mediana)",
            "E/E_ref (mediana)",
            "J/ponto F1 (mediana)",
            "Dominado (fração)",
            "Repetições de treino (mediana)",
        ]
        if c in show
    ]
    return (
        f"# Resultados: {dataset} ({mode})\n\n"
        "Gerado por `experiments/generate_results.py` a partir de "
        "`comparative_results.csv`. Energia de treino por execução.\n\n"
        + show[keep].to_markdown(index=False, floatfmt=".4g")
        + "\n\nFiguras: `energy_time`, `pareto_energy_f1`, `gms_barchart` (PNG e SVG);"
        " tabela: `summary_table.tex`. Testes de hipótese: "
        "`experiments/statistical_analysis.py`; contextos: "
        "`experiments/context_analysis.py`.\n"
    )


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------


def process(results_dir: Path, figures_dir: Path) -> None:
    """Gera figuras e tabelas de uma execução."""
    csv_path = results_dir / "comparative_results.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")
    df = pd.read_csv(csv_path)
    dataset, mode = results_dir.parent.name, results_dir.name
    figures_dir.mkdir(parents=True, exist_ok=True)

    agg = aggregate(df)
    n = int(agg["n"].max())
    title = figure_title(dataset, mode, f"{n} semente{'s' if n > 1 else ''}")
    plot_energy_time(agg, figures_dir, title)
    plot_pareto(agg, figures_dir, f"F1-Score × energia: {title}")
    plot_gms(agg, figures_dir, f"GreenML Score: {title}")
    (figures_dir / "summary_table.tex").write_text(
        latex_table(agg, dataset, mode), encoding="utf-8"
    )
    (figures_dir / "README.md").write_text(readme(agg, dataset, mode), encoding="utf-8")
    print(f"[OK] {dataset}/{mode} -> {figures_dir}")


def discover(mode: str) -> list[Path]:
    """Execuções em experiments/results/<dataset>/<modo>, ignorando o legado (_*)."""
    if not RESULTS_DIR.is_dir():
        return []
    return sorted(
        d / mode
        for d in RESULTS_DIR.iterdir()
        if d.is_dir()
        and not d.name.startswith("_")
        and (d / mode / "comparative_results.csv").exists()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--mode", default="full", choices=["full", "quick_run"])
    parser.add_argument("--results", type=Path, default=None)
    args = parser.parse_args()

    runs = [args.results] if args.results else discover(args.mode)
    if not runs:
        sys.exit(f"Nenhuma execução '{args.mode}' encontrada em {RESULTS_DIR}.")
    for run in runs:
        process(run, FIGURES_DIR / run.parent.name / run.name)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
