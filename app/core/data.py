"""
data.py: camada de dados do GreenML Dashboard.

Lê os resultados da execução completa (``experiments/results/<dataset>/full``) e os
contextos de execução (``experiments/contexts/contexts.csv``) e calcula tudo o que o
painel exibe. Não depende do Streamlit, para poder ser testada na CI.

Carbono e água são sempre recalculados a partir da energia medida e dos fatores do
contexto escolhido (por padrão, o BR-local, local real de medição). As colunas
``carbon_kg`` e ``water_liters`` dos CSVs brutos, gravadas com fatores provisórios,
não são usadas.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd

from green_ml_score.contexts import (
    ContextEvaluation,
    ExecutionContext,
    evaluate_configurations,
    load_contexts_csv,
)
from green_ml_score.scoring.gms import Weights
from green_ml_score.scoring.relative import pareto_dominated

# Mesmos rótulos de experiments/labels.py (um teste garante a igualdade). Ficam
# copiados aqui porque importar o pacote experiments carrega o scikit-learn inteiro
# (cerca de 7 s), o que deixaria a abertura do painel lenta.
DATASET_NAMES: dict[str, str] = {
    "newsgroups": "20 Newsgroups",
    "breast_cancer": "Breast Cancer",
    "covtype": "Covertype",
}
MODEL_NAMES: dict[str, str] = {
    "Logistic_Regression": "Regressão Logística",
    "Random_Forest": "Random Forest",
    "MLP_Neural_Network": "MLP",
    "XGBoost": "XGBoost",
}

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "experiments" / "results"
CONTEXTS_CSV = REPO_ROOT / "experiments" / "contexts" / "contexts.csv"

MODEL_ORDER: tuple[str, ...] = (
    "Logistic_Regression",
    "Random_Forest",
    "XGBoost",
    "MLP_Neural_Network",
)
REFERENCE_MODEL = "Logistic_Regression"
REFERENCE_CONTEXT = "BR-local"

# Coordenadas aproximadas usadas apenas para posicionar os contextos no mapa.
# Contextos locais: o notebook de medição (Jaguariúna, SP) e, nos contrafactuais,
# a capital do país cuja rede elétrica é simulada.
COORDINATES: dict[str, tuple[float, float]] = {
    "BR-local": (-22.70, -46.99),
    "FR-local": (48.86, 2.35),
    "IN-local": (28.61, 77.21),
    "AWS-SaoPaulo": (-23.55, -46.63),
    "AWS-Virginia": (39.04, -77.49),
    "AWS-Frankfurt": (50.11, 8.68),
    "AWS-Stockholm": (59.33, 18.07),
}
CONTEXT_KIND: dict[str, str] = {
    "BR-local": "Local (Brasil)",
    "FR-local": "Local (França, contrafactual)",
    "IN-local": "Local (Índia, contrafactual)",
}

# Perfis de peso (w_E, w_C, w_W) discutidos no artigo.
PROFILES: dict[str, tuple[float, float, float]] = {
    "Pesos iguais": (1 / 3, 1 / 3, 1 / 3),
    "Só energia": (1.0, 0.0, 0.0),
    "Só carbono": (0.0, 1.0, 0.0),
    "Só água": (0.0, 0.0, 1.0),
    "Carbono priorizado": (0.2, 0.5, 0.3),
    "Água priorizada": (0.3, 0.2, 0.5),
}

KWH_TO_MWH = 1e6
KWH_TO_J = 3.6e6


# ------------------------------------------------------------------ leitura
def available_datasets(mode: str = "full") -> list[str]:
    """Datasets com ``comparative_results.csv`` no modo indicado, na ordem do artigo."""
    found = [
        d
        for d in DATASET_NAMES
        if (RESULTS_DIR / d / mode / "comparative_results.csv").exists()
    ]
    return found


def dataset_label(dataset: str) -> str:
    """Nome de exibição do dataset."""
    return DATASET_NAMES.get(dataset, dataset)


def model_label(model: str) -> str:
    """Nome de exibição do modelo."""
    return MODEL_NAMES.get(model, model)


def load_runs(dataset: str, mode: str = "full") -> pd.DataFrame:
    """Execuções (uma linha por modelo e semente) de um dataset."""
    path = RESULTS_DIR / dataset / mode / "comparative_results.csv"
    if not path.exists():
        raise FileNotFoundError(f"Resultados não encontrados: {path}")
    df = pd.read_csv(path)
    missing = {"model_name", "seed", "energy_kwh", "f1_macro", "gms"} - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes em {path}: {sorted(missing)}")
    return df


def load_contexts() -> list[ExecutionContext]:
    """Contextos de execução do ``contexts.csv``."""
    return load_contexts_csv(CONTEXTS_CSV)


def get_context(
    name: str, contexts: Sequence[ExecutionContext] | None = None
) -> ExecutionContext:
    """Contexto pelo nome (por exemplo, ``BR-local``)."""
    for ctx in contexts or load_contexts():
        if ctx.name == name:
            return ctx
    raise KeyError(f"Contexto inexistente: {name}")


def contexts_table(contexts: Sequence[ExecutionContext] | None = None) -> pd.DataFrame:
    """Fatores de cada contexto, com tipo e coordenadas para o mapa."""
    rows = []
    for ctx in contexts or load_contexts():
        lat, lon = COORDINATES.get(ctx.name, (np.nan, np.nan))
        rows.append(
            {
                "contexto": ctx.name,
                "tipo": CONTEXT_KIND.get(ctx.name, "Nuvem (AWS)"),
                "ic_g_kwh": ctx.carbon_intensity_g_per_kwh,
                "pue": ctx.pue,
                "wue_l_kwh": ctx.wue_onsite_l_per_kwh,
                "agua_geracao_l_kwh": ctx.offsite_water_l_per_kwh,
                "carbono_efetivo_g_kwh": ctx.pue * ctx.carbon_intensity_g_per_kwh,
                "agua_efetiva_l_kwh": ctx.wue_onsite_l_per_kwh
                + ctx.pue * ctx.offsite_water_l_per_kwh,
                "lat": lat,
                "lon": lon,
                "fonte": ctx.source or "",
            }
        )
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ métricas por modelo
def model_summary(
    dataset: str,
    context: ExecutionContext | None = None,
    mode: str = "full",
) -> pd.DataFrame:
    """
    Resumo por modelo (índice) de um dataset, na ordem do artigo.

    Colunas: F1 (média, desvio), energia em mWh (média, desvio, mediana), tempo de
    treino, GMS de contexto único (média, desvio, mediana), carbono (mg CO2e) e água
    (µL) no contexto informado a partir da energia média, posições nos rankings,
    razão de energia e ΔF1 frente à Regressão Logística (medianas por semente), custo
    marginal em J por ponto de F1 (mediana nas sementes em que o modelo supera a
    referência), fração de sementes em que é dominado e se integra a fronteira de
    Pareto das medianas.
    """
    ctx = context or get_context(REFERENCE_CONTEXT)
    df = load_runs(dataset, mode)
    g = df.groupby("model_name")
    out = pd.DataFrame(
        {
            "f1_mean": g.f1_macro.mean(),
            "f1_std": g.f1_macro.std(),
            "energy_mwh_mean": g.energy_kwh.mean() * KWH_TO_MWH,
            "energy_mwh_std": g.energy_kwh.std() * KWH_TO_MWH,
            "energy_mwh_median": g.energy_kwh.median() * KWH_TO_MWH,
            "time_s_mean": g.train_wall_time_s.mean(),
            "gms_mean": g.gms.mean(),
            "gms_std": g.gms.std(),
            "gms_median": g.gms.median(),
            "n_seeds": g.seed.nunique(),
        }
    )
    energy_kwh_mean = out.energy_mwh_mean / KWH_TO_MWH
    out["carbon_mg"] = [ctx.carbon_kg(e) * 1e6 for e in energy_kwh_mean]
    out["water_ul"] = [ctx.water_l(e) * 1e6 for e in energy_kwh_mean]
    out["rank_f1"] = out.f1_mean.rank(ascending=False, method="min").astype(int)
    out["rank_energy"] = out.energy_mwh_mean.rank(method="min").astype(int)
    out["rank_gms"] = out.gms_mean.rank(ascending=False, method="min").astype(int)

    if {"energy_ratio_ref", "delta_f1_points"} <= set(df.columns):
        out["energy_ratio_ref"] = g.energy_ratio_ref.median()
        out["delta_f1_points"] = g.delta_f1_points.median()
        better = df[df.delta_f1_points > 0]
        out["marginal_cost_j"] = better.groupby(
            "model_name"
        ).marginal_cost_j_per_f1_point.median()
    if "dominated" in df.columns:
        out["dominated_share"] = g.dominated.mean()
    out["pareto"] = ~pareto_dominated(
        out.energy_mwh_median.to_numpy(), out.f1_mean.to_numpy()
    )
    order = [m for m in MODEL_ORDER if m in out.index] + [
        m for m in out.index if m not in MODEL_ORDER
    ]
    return out.loc[order]


def decision_table(
    dataset: str, context: ExecutionContext | None = None
) -> pd.DataFrame:
    """
    Modelo escolhido por cada critério e o custo da escolha (energia mediana, carbono
    e água no contexto informado).
    """
    ctx = context or get_context(REFERENCE_CONTEXT)
    s = model_summary(dataset, ctx)
    choices = {
        "Maior F1-Score": s.f1_mean.idxmax(),
        "Menor energia": s.energy_mwh_median.idxmin(),
        "Maior GMS": s.gms_median.idxmax(),
    }
    front = s.index[s.pareto].tolist()
    rows = [{"criterio": c, "modelo": m} for c, m in choices.items()]
    rows += [
        {"criterio": "Fronteira de Pareto", "modelo": m}
        for m in sorted(front, key=lambda m: s.energy_mwh_median[m])
    ]
    out = pd.DataFrame(rows)
    out["f1"] = out.modelo.map(s.f1_mean)
    out["energia_mwh"] = out.modelo.map(s.energy_mwh_median)
    out["carbono_mg"] = [ctx.carbon_kg(e / KWH_TO_MWH) * 1e6 for e in out.energia_mwh]
    out["agua_ul"] = [ctx.water_l(e / KWH_TO_MWH) * 1e6 for e in out.energia_mwh]
    return out


# ------------------------------------------------------------------ contextos
def make_weights(w_e: float, w_c: float, w_w: float) -> Weights:
    """Pesos normalizados para somar 1 (ao menos um deve ser positivo)."""
    raw = np.array([w_e, w_c, w_w], dtype=float)
    if (raw < 0).any() or raw.sum() <= 0:
        raise ValueError("Os pesos devem ser não negativos e ao menos um positivo.")
    w = raw / raw.sum()
    return Weights(float(w[0]), float(w[1]), float(w[2]))


def median_energy_kwh(dataset: str, mode: str = "full") -> dict[str, float]:
    """Energia mediana de treinamento (kWh) por modelo."""
    return load_runs(dataset, mode).groupby("model_name").energy_kwh.median().to_dict()


def evaluate_context(
    dataset: str,
    weights: Weights,
    contexts: Sequence[ExecutionContext] | None = None,
    simplex_step: float = 0.05,
) -> ContextEvaluation:
    """GMS de todas as configurações modelo × contexto com os pesos informados."""
    return evaluate_configurations(
        median_energy_kwh(dataset),
        list(contexts or load_contexts()),
        weights=weights,
        simplex_step=simplex_step,
    )


def k_factors(
    configurations: pd.DataFrame,
    contexts: Sequence[ExecutionContext],
    weights: Weights,
) -> pd.Series:
    """Fator k_r de cada contexto (GMS_ir = 1 − E_i · k_r), na escala de 0 a 1."""
    e_max = configurations.energy_kwh.max()
    c_max = configurations.carbon_kg.max()
    w_max = configurations.water_l.max()
    return pd.Series(
        {
            c.name: weights.w_E / e_max
            + weights.w_C * c.pue * c.carbon_intensity_g_per_kwh / 1000 / c_max
            + weights.w_W
            * (c.wue_onsite_l_per_kwh + c.pue * c.offsite_water_l_per_kwh)
            / w_max
            for c in contexts
        }
    )


def inversions(configurations: pd.DataFrame, tol: float = 1e-12) -> pd.DataFrame:
    """
    Pares em que um modelo de maior energia obtém GMS maior que um de menor energia.

    Retorna uma linha por par, com o modelo mais caro (``vencedor``) e o mais
    econômico (``superado``) e seus contextos.
    """
    c = configurations.reset_index(drop=True)
    e = c.energy_kwh.to_numpy()
    s = c.gms.to_numpy()
    i, j = np.nonzero((e[:, None] < e[None, :]) & (s[None, :] > s[:, None] + tol))
    return pd.DataFrame(
        {
            "vencedor": c.model.to_numpy()[j],
            "contexto_vencedor": c.context.to_numpy()[j],
            "gms_vencedor": s[j],
            "superado": c.model.to_numpy()[i],
            "contexto_superado": c.context.to_numpy()[i],
            "gms_superado": s[i],
        }
    )


def profile_summary(dataset: str) -> pd.DataFrame:
    """τ_b, pares invertidos e melhor e pior contexto em cada perfil de peso."""
    contexts = load_contexts()
    rows = []
    for name, w in PROFILES.items():
        ev = evaluate_context(dataset, make_weights(*w), contexts)
        cfg = ev.configurations
        ref = cfg[cfg.model == REFERENCE_MODEL].sort_values("gms")
        rows.append(
            {
                "perfil": name,
                "tau_b": ev.kendall_tau,
                "pares_invertidos": len(inversions(cfg)),
                "melhor_contexto": ref.iloc[-1].context,
                "pior_contexto": ref.iloc[0].context,
                "melhor_configuracao": f"{cfg.iloc[0].model} | {cfg.iloc[0].context}",
            }
        )
    return pd.DataFrame(rows)
