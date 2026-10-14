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
    seleção difere do critério só-energia).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("results_dir", type=Path)
    parser.add_argument(
        "--contexts", type=Path, default=Path("experiments/contexts/contexts.csv")
    )
    parser.add_argument("--step", type=float, default=0.05, help="Passo do simplex.")
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
    print(report)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
