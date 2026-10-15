"""
Cartão ambiental de um modelo, em Markdown.

Inspirado em *Model Cards* (Mitchell et al., 2019): resume, em um único documento
auditável, desempenho, custo energético (bruto e líquido de repouso), carbono,
água, comparação com a referência e procedência da medição.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

KWH_TO_J: float = 3.6e6


def _fmt(value: float | None, spec: str = ".4g", unit: str = "") -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    return f"{value:{spec}}{(' ' + unit) if unit else ''}"


def _spread(center: float | None, spread: float | None, spec: str, unit: str) -> str:
    if spread is None or (isinstance(spread, float) and math.isnan(spread)):
        return _fmt(center, spec, unit)
    return f"{_fmt(center, spec)} ± {_fmt(spread, spec)}{(' ' + unit) if unit else ''}"


@dataclass
class EnvironmentalCard:
    """
    Dados de um cartão ambiental. Energias por execução, em kWh; estatísticas
    sobre as sementes (mediana e IQR para energia; média e desvio para qualidade).
    """

    model: str
    dataset: str
    n_runs: int
    accuracy_mean: float
    accuracy_std: float | None
    f1_mean: float
    f1_std: float | None
    train_energy_median_kwh: float
    train_energy_iqr_kwh: float | None
    train_wall_time_median_s: float
    carbon_median_kg: float
    water_median_l: float
    gms_median: float
    carbon_intensity_g_per_kwh: float
    wue_l_per_kwh: float
    train_energy_net_median_kwh: float | None = None
    idle_power_w: float | None = None
    infer_energy_j_per_1k_median: float | None = None
    reference_model: str | None = None
    energy_ratio_median: float | None = None
    marginal_cost_median_j_per_f1_point: float | None = None
    dominated_share: float | None = None
    tracking_modes: list[str] = field(default_factory=list)
    ram_share_median: float | None = None
    provenance_warnings: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Renderiza o cartão em Markdown."""
        j = KWH_TO_J
        lines = [
            f"# Cartão ambiental — {self.model}",
            "",
            f"Dataset: **{self.dataset}** · execuções (sementes): **{self.n_runs}**",
            "",
            "## Desempenho",
            "",
            "| Métrica | Valor (média ± desvio) |",
            "|---|---|",
            f"| Acurácia | {_spread(self.accuracy_mean, self.accuracy_std, '.4f', '')} |",
            f"| F1 macro | {_spread(self.f1_mean, self.f1_std, '.4f', '')} |",
            "",
            "## Custo ambiental (treino, por execução)",
            "",
            "| Métrica | Mediana |",
            "|---|---|",
            f"| Energia bruta | {_fmt(self.train_energy_median_kwh * j, '.4g', 'J')} "
            f"(IQR {_fmt(None if self.train_energy_iqr_kwh is None else self.train_energy_iqr_kwh * j, '.3g', 'J')}) |",
            f"| Energia líquida de repouso (E − P₀·t) | "
            f"{_fmt(None if self.train_energy_net_median_kwh is None else self.train_energy_net_median_kwh * j, '.4g', 'J')} |",
            f"| Potência ociosa P₀ | {_fmt(self.idle_power_w, '.3g', 'W')} |",
            f"| Tempo de parede | {_fmt(self.train_wall_time_median_s, '.4g', 's')} |",
            f"| Carbono (IC = {self.carbon_intensity_g_per_kwh:g} gCO₂e/kWh) | "
            f"{_fmt(self.carbon_median_kg * 1000, '.4g', 'g CO₂e')} |",
            f"| Água (WUE = {self.wue_l_per_kwh:g} L/kWh) | "
            f"{_fmt(self.water_median_l * 1000, '.4g', 'mL')} |",
            f"| Inferência | {_fmt(self.infer_energy_j_per_1k_median, '.4g', 'J / 1.000 amostras')} |",
            f"| GreenML Score (0–100, relativo ao conjunto) | {_fmt(self.gms_median, '.2f')} |",
            "",
        ]
        if self.reference_model is not None:
            if self.reference_model == self.model:
                lines += [
                    "## Comparação com a referência",
                    "",
                    "Este é o modelo de referência do dataset.",
                    "",
                ]
            else:
                dominated = (
                    "—"
                    if self.dominated_share is None
                    else f"{self.dominated_share:.0%} das sementes"
                )
                lines += [
                    f"## Comparação com a referência ({self.reference_model})",
                    "",
                    "| Métrica | Mediana |",
                    "|---|---|",
                    f"| Razão de energia E / E_ref | {_fmt(self.energy_ratio_median, '.3g', '×')} |",
                    f"| Custo marginal | {_fmt(self.marginal_cost_median_j_per_f1_point, '.4g', 'J por ponto de F1')} |",
                    f"| Dominado (Pareto F1 × energia) | {dominated} |",
                    "",
                ]
        modes = ", ".join(self.tracking_modes) if self.tracking_modes else "—"
        lines += [
            "## Procedência da medição",
            "",
            f"- Modo do CodeCarbon: {modes}",
            f"- Fração da energia atribuída à RAM (mediana): {_fmt(None if self.ram_share_median is None else self.ram_share_median * 100, '.1f', '%')}",
        ]
        lines += [f"- ⚠ {w}" for w in self.provenance_warnings]
        lines.append("")
        return "\n".join(lines)
