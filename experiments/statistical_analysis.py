"""
statistical_analysis.py — Análise estatística reprodutível de uma execução do experimento.

Uso:
    python experiments/statistical_analysis.py experiments/results/newsgroups/full

Lê ``comparative_results.csv`` do diretório informado e grava ``stats_report.md``
no mesmo diretório, contendo:
  - estatística descritiva (média, desvio, mediana, IQR);
  - Friedman (execuções pareadas por semente) e Kruskal-Wallis;
  - pós-teste pareado de Wilcoxon com correção de Holm;
  - correlações de Spearman do GMS com energia, tempo de parede e tempo de CPU;
  - Friedman e Wilcoxon-Holm também sobre a energia de treino;
  - score relativo à referência (razão de energia, custo marginal, dominância);
  - energia líquida de repouso e número efetivo de repetições;
  - verificação de degeneração (GMS ≡ 100·(1 − E/E_max));
  - diagnóstico de procedência (modo do CodeCarbon, fração de energia da RAM e
    avisos registrados em ``run_metadata.json``).
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

KWH_TO_MWH: float = 1e6
MODEL, SEED, GMS = "model_name", "seed", "gms"
ENERGY, WALL, CPU = "energy_kwh", "train_wall_time_s", "train_cpu_time_s"


def holm(p_values: list[float]) -> list[float]:
    """Correção de Holm-Bonferroni (monotônica)."""
    order = np.argsort(p_values)
    m, running, adjusted = len(p_values), 0.0, np.empty(len(p_values))
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p_values[idx])
        adjusted[idx] = min(1.0, running)
    return adjusted.tolist()


def describe(df: pd.DataFrame) -> pd.DataFrame:
    work = df.assign(energy_mwh=df[ENERGY] * KWH_TO_MWH)

    def iqr(s: pd.Series) -> float:
        return float(s.quantile(0.75) - s.quantile(0.25))

    agg = work.groupby(MODEL)[[GMS, "energy_mwh", WALL]].agg(
        ["mean", "std", "median", iqr]
    )
    agg.columns = [f"{c} [{s}]" for c, s in agg.columns]
    return agg


def paired_tests(df: pd.DataFrame, value: str = GMS) -> tuple[str, pd.DataFrame | None]:
    """Friedman + Wilcoxon pareado (Holm). Exige o mesmo conjunto de sementes por modelo."""
    wide = df.pivot(index=SEED, columns=MODEL, values=value).dropna()
    if len(wide) < 3 or wide.shape[1] < 3:
        return "Friedman: requer ≥ 3 sementes completas e ≥ 3 modelos.", None
    fr = stats.friedmanchisquare(*wide.T.to_numpy())
    text = f"Friedman: χ²_F = {fr.statistic:.4f}; p = {fr.pvalue:.4g} (n = {len(wide)} sementes)"

    rows = []
    for a, b in combinations(wide.columns, 2):
        diff = wide[a] - wide[b]
        p = 1.0 if np.allclose(diff, 0) else stats.wilcoxon(wide[a], wide[b]).pvalue
        rows.append({"A": a, "B": b, "mediana(A−B)": diff.median(), "p": p})
    post = pd.DataFrame(rows)
    post["p_holm"] = holm(post["p"].tolist())
    if len(wide) < 6:
        text += (
            f"\n\nAVISO: com n = {len(wide)} pares, o menor p bilateral possível do "
            f"Wilcoxon é {2 / 2 ** len(wide):.3f}; comparações par a par não têm poder."
        )
    return text, post


def relative_summary(df: pd.DataFrame) -> pd.DataFrame | None:
    """Score relativo à referência por modelo (medianas e fração dominada)."""
    if "energy_ratio_ref" not in df:
        return None
    return df.groupby(MODEL).agg(
        **{
            "E/E_ref (mediana)": ("energy_ratio_ref", "median"),
            "ΔF1 pontos (mediana)": ("delta_f1_points", "median"),
            "J por ponto de F1 (mediana)": ("marginal_cost_j_per_f1_point", "median"),
            "dominado (fração)": ("dominated", "mean"),
        }
    )


def measurement_summary(df: pd.DataFrame) -> pd.DataFrame | None:
    """Energia líquida de repouso e número efetivo de repetições por modelo."""
    cols = {
        "energy_net_kwh": "Energia líquida mWh (mediana)",
        "train_repetitions": "Repetições de treino (mediana)",
        "infer_repetitions": "Repetições de inferência (mediana)",
        "train_session_s": "Sessão de treino s (mediana)",
    }
    present = {c: n for c, n in cols.items() if c in df}
    if not present:
        return None
    out = df.groupby(MODEL)[list(present)].median().rename(columns=present)
    if "energy_net_kwh" in present:
        out["Energia líquida mWh (mediana)"] *= KWH_TO_MWH
        out["Energia líquida < 0 (fração)"] = df.groupby(MODEL)["energy_net_kwh"].apply(
            lambda s: float((s < 0).mean())
        )
    return out


def build_report(df: pd.DataFrame, metadata: dict | None = None) -> str:
    lines = ["# Relatório estatístico\n"]
    lines += ["## Estatística descritiva\n", describe(df).round(4).to_markdown(), ""]

    groups = [g[GMS].to_numpy() for _, g in df.groupby(MODEL)]
    kw = stats.kruskal(*groups)
    friedman_text, post = paired_tests(df)
    lines += [
        "## Testes de hipótese (GMS)\n",
        friedman_text,
        "",
        f"Kruskal-Wallis (sem pareamento): H = {kw.statistic:.4f}; p = {kw.pvalue:.4g}",
        "",
    ]
    if post is not None:
        lines += [
            "Pós-teste: Wilcoxon pareado com correção de Holm\n",
            post.round(4).to_markdown(index=False),
            "",
        ]

    energy_text, energy_post = paired_tests(df, ENERGY)
    lines += [
        "## Testes de hipótese (energia de treino)\n",
        "Com IC e WUE constantes, o GMS é função monotônica da energia; o teste "
        "sobre a energia é o que sustenta diferenças entre modelos.\n",
        energy_text,
        "",
    ]
    if energy_post is not None:
        lines += [
            "Pós-teste: Wilcoxon pareado com correção de Holm\n",
            energy_post.to_markdown(index=False, floatfmt=".4g"),
            "",
        ]

    rel = relative_summary(df)
    if rel is not None:
        lines += [
            f"## Score relativo à referência ({df['reference_model'].iloc[0]})\n",
            rel.round(4).to_markdown(),
            "",
        ]
    meas = measurement_summary(df)
    if meas is not None:
        lines += [
            "## Medição: energia líquida e repetições\n",
            meas.round(4).to_markdown(),
            "",
        ]
        if metadata and "idle_baseline" in metadata:
            ib = metadata["idle_baseline"]
            lines += [
                f"- P₀ = {ib['power_w']:.2f} W (repouso de {ib['duration_s']:.0f} s); "
                f"janela mínima por fase: {metadata.get('min_window_s', '—')} s",
                "",
            ]

    lines += ["## O GMS carrega informação além de energia e tempo?\n"]
    for label, col in [
        ("energia", ENERGY),
        ("tempo de parede", WALL),
        ("tempo de CPU", CPU),
    ]:
        r = stats.spearmanr(df[GMS], df[col])
        lines.append(
            f"- Spearman GMS × {label}: ρ = {r.statistic:.4f} (p = {r.pvalue:.3g})"
        )
    e = df[ENERGY]
    gap = float((df[GMS] - 100 * (1 - e / e.max())).abs().max())
    lines += [
        "",
        f"- max |GMS − 100·(1 − E/E_max)| = {gap:.2e} "
        "(≈ 0 ⇒ o GMS é função exclusiva da energia neste cenário)",
        "",
    ]

    if "ram_energy_share" in df and df["ram_energy_share"].notna().any():
        share = df["ram_energy_share"]
        lines += [
            "## Procedência da medição\n",
            f"- Modo(s) do CodeCarbon: {sorted(str(x) for x in df['tracking_mode'].dropna().unique())}",
            f"- Potência de RAM (W): {sorted(float(x) for x in df['ram_power_w'].dropna().unique())}",
            f"- Fração da energia atribuída à RAM: média {share.mean():.1%}, "
            f"mín {share.min():.1%}, máx {share.max():.1%}",
            "",
        ]
    if metadata and metadata.get("provenance_warnings"):
        lines += ["Avisos registrados na execução:\n"]
        lines += [f"- ⚠ {w}" for w in metadata["provenance_warnings"]]
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("results_dir", type=Path)
    args = parser.parse_args()

    csv_path = args.results_dir / "comparative_results.csv"
    if not csv_path.exists():
        sys.exit(f"Arquivo não encontrado: {csv_path}")
    meta_path = args.results_dir / "run_metadata.json"
    metadata = (
        json.loads(meta_path.read_text(encoding="utf-8"))
        if meta_path.exists()
        else None
    )
    report = build_report(pd.read_csv(csv_path), metadata)
    (args.results_dir / "stats_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
