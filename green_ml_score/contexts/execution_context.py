"""
Contexto de execução: onde (e quando) um modelo é executado.

Um ``ExecutionContext`` reúne os fatores que convertem energia em carbono e água:

    C = E × PUE × IC                       (kg CO2e, com IC em gCO2e/kWh ÷ 1000)
    W = E × WUE_on-site + E × PUE × EWIF   (litros)

em que WUE_on-site é a água consumida no resfriamento do data center por kWh de TI
e EWIF (fator hídrico off-site) é a água consumida na geração da eletricidade por
kWh entregue (Macknick et al., 2012). Para execução local (notebook), PUE = 1 e
WUE_on-site = 0.

Os valores numéricos dos contextos NÃO ficam no código: são lidos de um CSV cujas
linhas citam a própria fonte (ver ``load_contexts_csv``).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from green_ml_score.scoring.gms import EnvironmentalMetrics

REQUIRED_COLUMNS: tuple[str, ...] = (
    "name",
    "carbon_intensity_g_per_kwh",
    "wue_onsite_l_per_kwh",
    "offsite_water_l_per_kwh",
)
OPTIONAL_COLUMNS: tuple[str, ...] = ("hour", "pue", "source")


@dataclass(frozen=True)
class ExecutionContext:
    """
    Fatores ambientais de uma região de execução, opcionalmente em um horário.

    Atributos:
        name                       : identificador do contexto (ex.: "BR-SE").
        carbon_intensity_g_per_kwh : intensidade de carbono da rede (gCO2e/kWh).
        wue_onsite_l_per_kwh       : WUE do data center (L/kWh de TI); 0 em execução local.
        offsite_water_l_per_kwh    : água consumida na geração elétrica (L/kWh).
        hour                       : hora do dia (0–23) a que a IC se refere, se horária.
        pue                        : Power Usage Effectiveness (≥ 1); 1 em execução local.
        source                     : referência bibliográfica dos valores.
    """

    name: str
    carbon_intensity_g_per_kwh: float
    wue_onsite_l_per_kwh: float
    offsite_water_l_per_kwh: float
    hour: int | None = None
    pue: float = 1.0
    source: str | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("O contexto precisa de um nome.")
        for attr in (
            "carbon_intensity_g_per_kwh",
            "wue_onsite_l_per_kwh",
            "offsite_water_l_per_kwh",
        ):
            if getattr(self, attr) < 0:
                raise ValueError(f"{attr} não pode ser negativo ({self.name}).")
        if self.pue < 1.0:
            raise ValueError(f"PUE deve ser ≥ 1 ({self.name}).")
        if self.hour is not None and not 0 <= self.hour <= 23:
            raise ValueError(f"hour deve estar entre 0 e 23 ({self.name}).")

    @property
    def label(self) -> str:
        """Rótulo legível: nome e, se houver, horário."""
        return self.name if self.hour is None else f"{self.name}@{self.hour:02d}h"

    def carbon_kg(self, energy_kwh: float) -> float:
        """Emissões (kg CO2e) da energia de TI ``energy_kwh`` neste contexto."""
        return energy_kwh * self.pue * self.carbon_intensity_g_per_kwh / 1000.0

    def water_l(self, energy_kwh: float) -> float:
        """Água consumida (L) on-site e off-site para a energia de TI ``energy_kwh``."""
        return energy_kwh * (
            self.wue_onsite_l_per_kwh + self.pue * self.offsite_water_l_per_kwh
        )

    def metrics(self, energy_kwh: float) -> EnvironmentalMetrics:
        """Energia, carbono e água de uma execução com ``energy_kwh`` neste contexto."""
        if energy_kwh < 0:
            raise ValueError("energy_kwh não pode ser negativo.")
        return EnvironmentalMetrics(
            energy=energy_kwh,
            carbon=self.carbon_kg(energy_kwh),
            water=self.water_l(energy_kwh),
        )


def _optional(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


def load_contexts_csv(path: str | Path) -> list[ExecutionContext]:
    """
    Lê contextos de um CSV com as colunas obrigatórias ``REQUIRED_COLUMNS`` e as
    opcionais ``OPTIONAL_COLUMNS``.

    Raises:
        FileNotFoundError: se o arquivo não existir.
        ValueError: se faltar coluna, se não houver linhas, se houver rótulos
            duplicados ou valores inválidos.
    """
    path = Path(path)
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Colunas ausentes em '{path}': {sorted(missing)}")
        contexts = []
        for line, row in enumerate(reader, start=2):
            try:
                hour = _optional(row.get("hour"))
                pue = _optional(row.get("pue"))
                contexts.append(
                    ExecutionContext(
                        name=row["name"].strip(),
                        carbon_intensity_g_per_kwh=float(
                            row["carbon_intensity_g_per_kwh"]
                        ),
                        wue_onsite_l_per_kwh=float(row["wue_onsite_l_per_kwh"]),
                        offsite_water_l_per_kwh=float(row["offsite_water_l_per_kwh"]),
                        hour=int(hour) if hour is not None else None,
                        pue=float(pue) if pue is not None else 1.0,
                        source=_optional(row.get("source")),
                    )
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Linha {line} inválida em '{path}': {exc}") from exc

    if not contexts:
        raise ValueError(f"Nenhum contexto definido em '{path}'.")
    labels = [c.label for c in contexts]
    duplicated = sorted({x for x in labels if labels.count(x) > 1})
    if duplicated:
        raise ValueError(f"Contextos duplicados em '{path}': {duplicated}")
    return contexts
