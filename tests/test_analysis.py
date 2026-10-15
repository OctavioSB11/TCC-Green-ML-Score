"""
test_analysis.py — Agregação, fronteira de Pareto, tabelas e relatório estatístico.
"""

import numpy as np
import pandas as pd

from experiments.generate_results import aggregate, latex_table, pareto_front, readme
from experiments.run_analysis import contexts_defined
from experiments.statistical_analysis import (
    build_report,
    measurement_summary,
    relative_summary,
)

KWH_TO_J = 3.6e6


def _results(n_seeds: int = 4) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    base = {"LR": (1e-7, 0.90), "RF": (4e-6, 0.92), "MLP": (2e-6, 0.88)}
    for seed in range(n_seeds):
        for model, (e, f1) in base.items():
            energy = e * (1 + 0.05 * rng.standard_normal())
            rows.append(
                {
                    "seed": seed,
                    "model_name": model,
                    "accuracy": f1,
                    "f1_macro": f1 + 0.001 * seed,
                    "energy_kwh": energy,
                    "energy_net_kwh": energy - 5e-8,
                    "train_wall_time_s": energy * 1e5,
                    "train_cpu_time_s": energy * 1e5,
                    "train_repetitions": 10,
                    "infer_repetitions": 100,
                    "train_session_s": 30.0,
                    "reference_model": "LR",
                    "energy_ratio_ref": energy / 1e-7,
                    "delta_f1_points": 100 * (f1 - 0.90),
                    "marginal_cost_j_per_f1_point": (
                        np.nan if f1 <= 0.90 else (energy - 1e-7) * KWH_TO_J / 2
                    ),
                    "dominated": model == "MLP",
                }
            )
    df = pd.DataFrame(rows)
    df["gms"] = 100 * (1 - df["energy_kwh"] / df["energy_kwh"].max())
    return df


def test_pareto_front() -> None:
    e = np.array([1.0, 2.0, 3.0, 2.0])
    f = np.array([0.8, 0.9, 0.85, 0.9])
    # (3, 0.85) é dominado por (2, 0.9); os dois pontos (2, 0.9) não se dominam
    assert pareto_front(e, f).tolist() == [True, True, False, True]


def test_aggregate_orders_by_energy_and_marks_reference() -> None:
    agg = aggregate(_results())
    assert agg["model"].tolist() == ["LR", "MLP", "RF"]
    assert agg.set_index("model").loc["LR", "is_reference"]
    assert agg["n"].tolist() == [4, 4, 4]
    assert (agg["energy_j_q1"] <= agg["energy_j_median"]).all()
    assert (agg["energy_j_median"] <= agg["energy_j_q3"]).all()


def test_latex_table_and_readme_use_data() -> None:
    agg = aggregate(_results())
    tex = latex_table(agg, "breast_cancer", "full")
    assert r"breast\_cancer" in tex and "4 semente(s)" in tex
    assert "ref." in tex and "dominado" in tex
    assert tex.count(r"\\") >= 4
    md = readme(agg, "breast_cancer", "full")
    assert "E/E_ref" in md


def test_statistical_report_sections() -> None:
    df = _results(n_seeds=6)
    meta = {
        "idle_baseline": {"power_w": 15.0, "duration_s": 60.0},
        "min_window_s": 30.0,
        "provenance_warnings": ["tracking_mode = machine: teste"],
    }
    report = build_report(df, meta)
    assert "Testes de hipótese (energia de treino)" in report
    assert "Score relativo à referência (LR)" in report
    assert "P₀ = 15.00 W" in report
    assert "⚠ tracking_mode = machine" in report
    rel = relative_summary(df)
    assert rel.loc["MLP", "dominado (fração)"] == 1.0
    meas = measurement_summary(df)
    assert meas.loc["LR", "Energia líquida < 0 (fração)"] == 0.0
    assert meas.loc["LR", "Repetições de treino (mediana)"] == 10


def test_contexts_defined(tmp_path) -> None:
    p = tmp_path / "c.csv"
    p.write_text("name,carbon_intensity_g_per_kwh\n", encoding="utf-8")
    assert not contexts_defined(p)
    p.write_text("name,carbon_intensity_g_per_kwh\nBR,100\n", encoding="utf-8")
    assert contexts_defined(p)
    assert not contexts_defined(tmp_path / "nao_existe.csv")
