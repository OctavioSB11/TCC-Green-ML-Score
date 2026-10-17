"""
context_analysis.py — Avaliação modelo × contexto de execução (região × horário).

Uso:
    python experiments/context_analysis.py experiments/results/newsgroups/full \
        --contexts experiments/contexts/contexts.csv

Lê ``comparative_results.csv`` (energia de treino por semente) e um CSV de
contextos (ver ``experiments/contexts/README.md``). A energia de cada modelo é a
mediana entre sementes. Grava no diretório de resultados:
  - ``context_configurations.csv``: E, C, W, GMS e rankings de cada configuração;
  - ``context_sensitivity.csv``: τ_b e melhor configuração em cada ponto do simplex;
  - ``context_report.md``: resumo (τ_b de Kendall e fração do simplex em que a
    seleção difere do critério só-energia);
e, em ``docs/Results/<dataset>/<modo>/``, as figuras ``context_gms_heatmap`` e
``context_simplex`` (τ_b e configuração vencedora em cada ponto do simplex).
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
from green_ml_score.contexts import (  # noqa: E402
    ContextEvaluation,
    evaluate_configurations,
    load_contexts_csv,
)


def build_report(evaluation: ContextEvaluation, contexts_path: Path) -> str:
    s = evaluation.summary()
    lines = [
        "# Avaliação modelo × contexto de execução\n",
        f"Contextos: `{contexts_path.as_posix()}` · modelos: {s['n_models']} · "
        f"contextos: {s['n_contexts']} · configurações: {s['n_configurations']}\n",
        "## Concordância com o critério só-energia\n",
        f"- τ_b de Kendall (GMS com pesos 1/3 × energia): {s['kendall_tau']:.4f}",
        f"- τ_b no simplex de pesos: mín {s['kendall_tau_min_simplex']:.4f}, "
        f"mediana {s['kendall_tau_median_simplex']:.4f}, máx {s['kendall_tau_max_simplex']:.4f}",
        f"- Modelo de menor energia: {s['energy_best_model']}",
        f"- Fração do simplex em que o melhor GMS usa outro modelo: "
        f"{s['selection_change_share']:.1%}",
        "",
        "Observação: o critério só-energia não distingue contextos (a energia de TI "
        "não depende da região); empates de energia entre contextos de um mesmo "
        "modelo são tratados pelo τ_b.",
        "",
        "## Configurações (pesos 1/3)\n",
        evaluation.configurations.round(8).to_markdown(index=False),
        "",
    ]
    return "\n".join(lines)


def _ternary(sens: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Coordenadas no triângulo: vértices E = (0, 0), C = (1, 0), W = (½, √3/2)."""
    x = sens["w_C"] + sens["w_W"] / 2
    y = sens["w_W"] * np.sqrt(3) / 2
    return x.to_numpy(), y.to_numpy()


def _triangle(ax: plt.Axes) -> None:
    h = np.sqrt(3) / 2
    ax.plot([0, 1, 0.5, 0], [0, 0, h, 0], color="black", lw=1)
    ax.text(-0.03, -0.04, "w_E = 1", ha="right", va="top", fontsize=9)
    ax.text(1.03, -0.04, "w_C = 1", ha="left", va="top", fontsize=9)
    ax.text(0.5, h + 0.03, "w_W = 1", ha="center", va="bottom", fontsize=9)
    ax.set_xlim(-0.18, 1.18)
    ax.set_ylim(-0.14, h + 0.12)
    ax.set_aspect("equal")
    ax.axis("off")


def plot_figures(evaluation: ContextEvaluation, out_dir: Path, title: str) -> None:
    """Heatmap modelo × contexto, τ_b no simplex e melhor configuração no simplex."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = evaluation.configurations

    # 1. GMS (pesos 1/3) por modelo × contexto
    grid = cfg.pivot(index="model", columns="context", values="gms")
    grid.index = [model_name(m) for m in grid.index]
    fig, ax = plt.subplots(
        figsize=(1.2 + 1.1 * grid.shape[1], 1.2 + 0.55 * grid.shape[0])
    )
    im = ax.imshow(grid.to_numpy(), cmap="Greens", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(grid.shape[1]), grid.columns, rotation=30, ha="right")
    ax.set_yticks(range(grid.shape[0]), grid.index)
    for (i, j), v in np.ndenumerate(grid.to_numpy()):
        ax.text(
            j,
            i,
            comma(v, 1),
            ha="center",
            va="center",
            fontsize=8,
            color="white" if v > 60 else "black",
        )
    fig.colorbar(im, ax=ax, label="GMS (0–100)")
    ax.set_title(f"GMS por configuração (pesos iguais): {title}", fontsize=10)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(
            out_dir / f"context_gms_heatmap.{ext}", dpi=300, bbox_inches="tight"
        )
    plt.close(fig)

    # 2. τ_b no simplex e 3. melhor configuração no simplex
    sens = evaluation.sensitivity
    x, y = _ternary(sens)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
    sc = ax1.scatter(
        x, y, c=sens["kendall_tau"], cmap="viridis", vmin=-1, vmax=1, s=40, marker="h"
    )
    _triangle(ax1)
    cbar = fig.colorbar(sc, ax=ax1, label="τ_b (GMS × energia)", shrink=0.8, pad=0.06)
    cbar.ax.yaxis.set_major_formatter(comma_formatter(2))
    ax1.set_title("Concordância com o ranking por energia", fontsize=10, pad=14)

    best = (
        sens["best_configuration"]
        .map(lambda s: " | ".join([model_name(s.split(" | ")[0]), *s.split(" | ")[1:]]))
        .astype("category")
    )
    cmap = plt.get_cmap("tab10")
    for k, name in enumerate(best.cat.categories):
        m = (best == name).to_numpy()
        ax2.scatter(x[m], y[m], color=cmap(k % 10), s=40, marker="h", label=name)
    _triangle(ax2)
    ax2.legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.72, 1.0), frameon=False)
    ax2.set_title("Configuração de maior GMS", fontsize=10, pad=14)
    fig.suptitle(f"Sensibilidade aos pesos: {title}", fontweight="bold")
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(out_dir / f"context_simplex.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("results_dir", type=Path)
    parser.add_argument(
        "--contexts", type=Path, default=Path("experiments/contexts/contexts.csv")
    )
    parser.add_argument("--step", type=float, default=0.05, help="Passo do simplex.")
    parser.add_argument(
        "--figures",
        type=Path,
        default=None,
        help="Pasta das figuras (padrão: docs/Results/<dataset>/<modo>).",
    )
    args = parser.parse_args()

    csv_path = args.results_dir / "comparative_results.csv"
    if not csv_path.exists():
        sys.exit(f"Arquivo não encontrado: {csv_path}")
    df = pd.read_csv(csv_path)
    energy = df.groupby("model_name")["energy_kwh"].median().to_dict()
    contexts = load_contexts_csv(args.contexts)

    evaluation = evaluate_configurations(energy, contexts, simplex_step=args.step)
    evaluation.configurations.to_csv(
        args.results_dir / "context_configurations.csv", index=False
    )
    evaluation.sensitivity.to_csv(
        args.results_dir / "context_sensitivity.csv", index=False
    )
    report = build_report(evaluation, args.contexts)
    (args.results_dir / "context_report.md").write_text(report, encoding="utf-8")
    figures = (
        args.figures
        or Path("docs/Results") / args.results_dir.parent.name / args.results_dir.name
    )
    plot_figures(
        evaluation,
        figures,
        figure_title(args.results_dir.parent.name, args.results_dir.name),
    )
    print(report)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
