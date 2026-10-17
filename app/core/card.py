"""
card.py: cartão ambiental de um modelo em um contexto de execução.

O cartão da biblioteca (``green_ml_score.reporting.card``) usa um único fator de
carbono e de água e é gravado durante o experimento; aqui o cartão é montado para
qualquer região e perfil de pesos do painel, com carbono e água recalculados pelos
fatores do ``contexts.csv``. Exporta Markdown, CSV e PNG (matplotlib, sem internet).
"""

from __future__ import annotations

import io
from dataclasses import asdict, dataclass, field

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from app.core import data, theme  # noqa: E402

# Energia de uma carga de smartphone: 0,019 kWh (EPA, Greenhouse Gas Equivalencies
# Calculator, Calculations and References, atualizado em 4 ago. 2026, com dados do
# U.S. DOE). Única equivalência usada, por ter fonte oficial verificada.
SMARTPHONE_CHARGE_KWH = 0.019
SMARTPHONE_SOURCE = (
    "U.S. EPA. Greenhouse Gas Equivalencies Calculator: Calculations and References "
    "(0,019 kWh por carga de smartphone, com dados do U.S. DOE). Atualizado em 4 ago. "
    "2026. https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator-"
    "calculations-and-references"
)


@dataclass
class CardData:
    """Conteúdo de um cartão ambiental (valores por treinamento, salvo indicação)."""

    dataset: str
    model: str
    context: str
    context_kind: str
    profile: str
    weights: tuple[float, float, float]
    n_seeds: int
    f1_mean: float
    f1_std: float
    accuracy_mean: float
    accuracy_std: float
    energy_mwh_median: float
    energy_mwh_iqr: float
    time_s_median: float
    infer_j_per_1k_median: float | None
    carbon_mg: float
    water_ul: float
    gms_context: float
    rank_context: int
    n_configurations: int
    gms_single: float
    pareto: bool
    is_reference: bool
    energy_ratio_ref: float | None
    delta_f1_points: float | None
    marginal_cost_j: float | None
    dominated_share: float | None
    trainings_per_charge: float
    tracking_modes: list[str] = field(default_factory=list)
    ram_share_median: float | None = None
    idle_power_w: float | None = None
    sources: list[str] = field(default_factory=list)


def build_card(
    dataset: str,
    model: str,
    context_name: str = data.REFERENCE_CONTEXT,
    profile: str = "Pesos iguais",
) -> CardData:
    """Monta o cartão de ``model`` em ``dataset``, executado em ``context_name``."""
    ctx = data.get_context(context_name)
    runs = data.load_runs(dataset)
    r = runs[runs.model_name == model]
    if r.empty:
        raise KeyError(f"Modelo inexistente em {dataset}: {model}")
    summary = data.model_summary(dataset, ctx)
    s = summary.loc[model]
    weights = data.make_weights(*data.PROFILES[profile])
    sim = data.simulate(dataset, weights)
    cfg = sim["configurations"]
    pos = cfg.index[(cfg.model == model) & (cfg.context == context_name)][0]
    energy_kwh = r.energy_kwh.median()
    q1, q3 = r.energy_kwh.quantile([0.25, 0.75])
    is_ref = model == data.REFERENCE_MODEL

    def opt(col: str) -> float | None:
        if col not in s.index or is_ref:
            return None
        value = float(s[col])
        return None if value != value else value

    return CardData(
        dataset=dataset,
        model=model,
        context=context_name,
        context_kind=data.CONTEXT_KIND.get(context_name, "Nuvem (AWS)"),
        profile=profile,
        weights=(weights.w_E, weights.w_C, weights.w_W),
        n_seeds=int(r.seed.nunique()),
        f1_mean=float(r.f1_macro.mean()),
        f1_std=float(r.f1_macro.std()),
        accuracy_mean=float(r.accuracy.mean()),
        accuracy_std=float(r.accuracy.std()),
        energy_mwh_median=energy_kwh * data.KWH_TO_MWH,
        energy_mwh_iqr=(q3 - q1) * data.KWH_TO_MWH,
        time_s_median=float(r.train_wall_time_s.median()),
        infer_j_per_1k_median=(
            float(r.infer_energy_j_per_1k.median())
            if "infer_energy_j_per_1k" in r
            else None
        ),
        carbon_mg=ctx.carbon_kg(energy_kwh) * 1e6,
        water_ul=ctx.water_l(energy_kwh) * 1e6,
        gms_context=float(cfg.loc[pos, "gms"]),
        rank_context=int(pos) + 1,
        n_configurations=len(cfg),
        gms_single=float(s.gms_median),
        pareto=bool(s.pareto),
        is_reference=is_ref,
        energy_ratio_ref=opt("energy_ratio_ref"),
        delta_f1_points=opt("delta_f1_points"),
        marginal_cost_j=opt("marginal_cost_j"),
        dominated_share=None if is_ref else float(s.get("dominated_share", 0.0)),
        trainings_per_charge=SMARTPHONE_CHARGE_KWH / energy_kwh,
        tracking_modes=sorted(r.tracking_mode.dropna().unique().tolist()),
        ram_share_median=(
            float(r.ram_energy_share.median()) if "ram_energy_share" in r else None
        ),
        idle_power_w=float(r.idle_power_w.median()) if "idle_power_w" in r else None,
        sources=[
            part.strip() for part in (ctx.source or "").split("|") if part.strip()
        ],
    )


def annual_projection(card: CardData, trainings_per_day: float) -> dict[str, float]:
    """Energia (kWh), carbono (kg CO₂e) e água (L) de um ano de treinamentos."""
    n = 365 * trainings_per_day
    return {
        "energia_kwh": n * card.energy_mwh_median / data.KWH_TO_MWH,
        "carbono_kg": n * card.carbon_mg / 1e6,
        "agua_l": n * card.water_ul / 1e6,
    }


# ------------------------------------------------------------------ conteúdo
def _rows(card: CardData) -> list[tuple[str, str, str]]:
    """Linhas (seção, indicador, valor) comuns ao Markdown, ao CSV e ao PNG."""
    f = theme.fmt
    w = card.weights
    rows = [
        ("Identificação", "Conjunto de dados", data.dataset_label(card.dataset)),
        ("Identificação", "Modelo", data.model_label(card.model)),
        (
            "Identificação",
            "Região de execução",
            f"{card.context}, {card.context_kind}",
        ),
        (
            "Identificação",
            "Pesos do GMS",
            f"{card.profile}: energia {f(w[0], 2)}, carbono {f(w[1], 2)}, água {f(w[2], 2)}",
        ),
        ("Identificação", "Sementes", str(card.n_seeds)),
        (
            "Desempenho",
            "F1-Score (macro)",
            f"{f(card.f1_mean, 3)} ± {f(card.f1_std, 3)}",
        ),
        (
            "Desempenho",
            "Acurácia",
            f"{f(card.accuracy_mean, 3)} ± {f(card.accuracy_std, 3)}",
        ),
        (
            "Custo por treinamento",
            "Energia (mediana)",
            f"{theme.fmt_auto(card.energy_mwh_median)} mWh "
            f"(IQR {theme.fmt_auto(card.energy_mwh_iqr)} mWh)",
        ),
        (
            "Custo por treinamento",
            "Carbono",
            f"{theme.fmt_auto(card.carbon_mg)} mg CO₂e",
        ),
        ("Custo por treinamento", "Água", f"{theme.fmt_auto(card.water_ul)} µL"),
        (
            "Custo por treinamento",
            "Tempo de treino (mediana)",
            f"{theme.fmt_auto(card.time_s_median)} s",
        ),
    ]
    if card.infer_j_per_1k_median is not None:
        rows.append(
            (
                "Custo por treinamento",
                "Inferência (mediana)",
                f"{theme.fmt_auto(card.infer_j_per_1k_median)} J por 1.000 amostras",
            )
        )
    rows += [
        (
            "GreenML Score",
            "GMS nesta região",
            f"{f(card.gms_context, 1)} ({card.rank_context}º de {card.n_configurations} configurações)",
        ),
        ("GreenML Score", "GMS de contexto único", f(card.gms_single, 1)),
        (
            "GreenML Score",
            "Fronteira de Pareto",
            "Sim" if card.pareto else "Não (dominado)",
        ),
    ]
    if card.is_reference:
        rows.append(
            ("Comparação com a RL", "Situação", "Este é o modelo de referência")
        )
    else:
        rows += [
            (
                "Comparação com a RL",
                "Energia frente à RL",
                f"{f(card.energy_ratio_ref, 1)} vezes",
            ),
            (
                "Comparação com a RL",
                "ΔF1 (mediana)",
                ("+" if (card.delta_f1_points or 0) > 0 else "")
                + f"{f(card.delta_f1_points, 1)} pontos",
            ),
            (
                "Comparação com a RL",
                "Custo marginal",
                (
                    f"{f(card.marginal_cost_j, 2)} J por ponto de F1"
                    if card.marginal_cost_j is not None
                    else "não se aplica (não supera a RL)"
                ),
            ),
            (
                "Comparação com a RL",
                "Sementes em que é dominado",
                theme.fmt_pct(card.dominated_share or 0.0),
            ),
        ]
    rows += [
        (
            "Equivalência",
            "Treinamentos por carga de smartphone",
            f"{theme.fmt(card.trainings_per_charge, 0)} (0,019 kWh por carga; EPA)",
        ),
        (
            "Procedência",
            "Medição",
            f"CodeCarbon, modo {', '.join(card.tracking_modes) or 'n.a.'} (máquina inteira)",
        ),
        (
            "Procedência",
            "Energia atribuída à RAM",
            theme.fmt_pct(card.ram_share_median or 0.0),
        ),
        (
            "Procedência",
            "Potência ociosa",
            f"{theme.fmt_auto(card.idle_power_w or 0.0)} W",
        ),
        (
            "Procedência",
            "Validação física (bateria)",
            "ordem entre modelos confiável; valores absolutos, não",
        ),
    ]
    return rows


def short_sources(card: CardData) -> str:
    """Fontes resumidas por autor e ano, para o rodapé do PNG."""
    names = {
        "EMBER": "Ember (2026)",
        "REIG": "Reig et al. (2020)",
        "AMAZON WEB SERVICES": "Amazon Web Services (2026)",
    }
    found: list[str] = []
    for source in card.sources:
        if "por definição" in source.lower():
            found.append("execução local: PUE 1 e WUE 0")
            continue
        for key, label in names.items():
            if source.upper().startswith(key) and label not in found:
                found.append(label)
    found.append("U.S. EPA (2026)")
    return "; ".join(found)


def to_dataframe(card: CardData) -> pd.DataFrame:
    """Cartão como tabela (seção, indicador, valor), com as fontes ao final."""
    rows = _rows(card) + [
        ("Fontes", f"Fonte {i}", s) for i, s in enumerate(card.sources, 1)
    ]
    rows.append(("Fontes", "Equivalência", SMARTPHONE_SOURCE))
    return pd.DataFrame(rows, columns=["Seção", "Indicador", "Valor"])


def to_csv(card: CardData) -> bytes:
    """CSV com separador ';' e codificação que o Excel abre direto."""
    return to_dataframe(card).to_csv(sep=";", index=False).encode("utf-8-sig")


def to_markdown(card: CardData) -> str:
    """Cartão em Markdown."""
    title = (
        f"# Cartão ambiental: {data.model_label(card.model)} em {card.context}\n\n"
        f"{data.dataset_label(card.dataset)} · GreenML Dashboard\n"
    )
    out = [title]
    section = None
    for sec, key, value in _rows(card):
        if sec != section:
            out += [f"\n## {sec}\n", "| Indicador | Valor |", "|---|---|"]
            section = sec
        out.append(f"| {key} | {value} |")
    out += ["\n## Fontes\n"]
    out += [f"- {s}" for s in card.sources]
    out.append(f"- {SMARTPHONE_SOURCE}")
    return "\n".join(out) + "\n"


def to_png(card: CardData, dpi: int = 150) -> bytes:
    """Cartão em PNG, desenhado com matplotlib (não precisa de internet)."""
    rows = _rows(card)
    n_sections = len({r[0] for r in rows})
    height = 1.9 + 0.32 * len(rows) + 0.38 * n_sections
    fig = plt.figure(figsize=(8.5, height), dpi=dpi)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    y = 1 - 0.35 / height
    color = theme.MODEL_COLORS.get(card.model, theme.GREEN)
    ax.add_patch(
        plt.Rectangle(
            (0, y - 0.55 / height),
            1,
            0.9 / height,
            color=theme.GREEN,
            transform=ax.transAxes,
        )
    )
    ax.text(
        0.04,
        y,
        f"Cartão ambiental: {data.model_label(card.model)} em {card.context}",
        color="white",
        fontsize=15,
        fontweight="bold",
        va="center",
        transform=ax.transAxes,
    )
    ax.text(
        0.04,
        y - 0.3 / height,
        f"{data.dataset_label(card.dataset)} · GreenML Dashboard",
        color="white",
        fontsize=10,
        va="center",
        transform=ax.transAxes,
    )
    y -= 0.85 / height
    section = None
    for sec, key, value in rows:
        if sec != section:
            y -= 0.12 / height
            ax.text(
                0.04,
                y,
                sec.upper(),
                color=color,
                fontsize=10,
                fontweight="bold",
                va="center",
                transform=ax.transAxes,
            )
            y -= 0.26 / height
            section = sec
        ax.text(
            0.06,
            y,
            key,
            color=theme.GREY,
            fontsize=9.5,
            va="center",
            transform=ax.transAxes,
        )
        ax.text(
            0.42,
            y,
            value,
            color="#111111",
            fontsize=9.5,
            va="center",
            transform=ax.transAxes,
            wrap=True,
        )
        y -= 0.32 / height
    ax.text(
        0.04,
        0.3 / height,
        "Fontes: " + short_sources(card),
        color=theme.GREY,
        fontsize=8,
        va="center",
        transform=ax.transAxes,
    )
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor="white")
    plt.close(fig)
    return buf.getvalue()


def as_dict(card: CardData) -> dict:
    """Cartão como dicionário (útil para testes e integrações)."""
    return asdict(card)
