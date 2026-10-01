"""
GreenMLTracker — rastreamento de energia e carbono via CodeCarbon.

A energia é obtida, preferencialmente, do objeto ``final_emissions_data`` que o
CodeCarbon preenche ao final de cada medição (sem depender de arquivo em disco).
Como alternativa, lê-se o ``emissions.csv``. Em nenhum caso uma falha de leitura é
convertida silenciosamente em consumo nulo: ela interrompe a execução com
``MeasurementError``, pois um zero espúrio produziria GMS = 100.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from numbers import Real
from typing import Any

import pandas as pd
from codecarbon import EmissionsTracker

from green_ml_score.estimators.carbon import calculate_carbon_emissions
from green_ml_score.estimators.water import calculate_water_usage
from green_ml_score.scoring.gms import EnvironmentalMetrics


class MeasurementError(RuntimeError):
    """Falha na obtenção de uma medição de energia válida."""


@dataclass(frozen=True)
class MeasurementDetails:
    """
    Procedência da medição reportada pelo CodeCarbon.

    Permite distinguir energia medida (RAPL/NVML) de energia estimada
    (TDP, potência constante de RAM) e auditar cada número publicado.
    """

    duration_s: float | None = None
    cpu_energy_kwh: float | None = None
    ram_energy_kwh: float | None = None
    gpu_energy_kwh: float | None = None
    cpu_power_w: float | None = None
    ram_power_w: float | None = None
    tracking_mode: str | None = None
    os: str | None = None
    cpu_model: str | None = None
    codecarbon_version: str | None = None

    @property
    def ram_share(self) -> float | None:
        """Fração da energia total atribuída à RAM (None se indisponível)."""
        parts = (self.cpu_energy_kwh, self.ram_energy_kwh, self.gpu_energy_kwh or 0.0)
        if self.cpu_energy_kwh is None or self.ram_energy_kwh is None:
            return None
        total = sum(parts)
        return self.ram_energy_kwh / total if total > 0 else None


_DETAIL_FIELDS: dict[str, str] = {
    "duration_s": "duration",
    "cpu_energy_kwh": "cpu_energy",
    "ram_energy_kwh": "ram_energy",
    "gpu_energy_kwh": "gpu_energy",
    "cpu_power_w": "cpu_power",
    "ram_power_w": "ram_power",
    "tracking_mode": "tracking_mode",
    "os": "os",
    "cpu_model": "cpu_model",
    "codecarbon_version": "codecarbon_version",
}


def _as_float(value: Any) -> float | None:
    """Converte para float apenas valores numéricos reais (rejeita mocks e NaN)."""
    if isinstance(value, Real) and not isinstance(value, bool) and value == value:
        return float(value)
    return None


def _as_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _details_from(source: Any) -> MeasurementDetails:
    """Extrai detalhes de um objeto EmissionsData ou de uma linha do CSV (Series)."""
    get = source.get if isinstance(source, (dict, pd.Series)) else (
        lambda key, default=None: getattr(source, key, default)
    )
    values: dict[str, Any] = {}
    for field_name, source_key in _DETAIL_FIELDS.items():
        raw = get(source_key, None)
        is_text = field_name in {"tracking_mode", "os", "cpu_model", "codecarbon_version"}
        values[field_name] = _as_str(raw) if is_text else _as_float(raw)
    return MeasurementDetails(**values)


class GreenMLTracker:
    """
    Rastreador principal do GreenML Score.
    Utiliza o CodeCarbon para medição de energia e carbono.
    """

    def __init__(
        self,
        wue_liters_per_kwh: float = 1.8,
        carbon_intensity_g_per_kwh: float | None = None,
        **codecarbon_kwargs: Any,
    ) -> None:
        """
        Parâmetros:
            wue_liters_per_kwh : WUE do ambiente de execução (L/kWh).
                                 Padrão 1.8 = média da indústria de data centers.
            carbon_intensity_g_per_kwh : intensidade de carbono regional (gCO2e/kWh).
                                 Se informado, C = E × IC. Se None, usa a emissão
                                 medida pelo CodeCarbon e deriva a IC efetiva.
            **codecarbon_kwargs: argumentos repassados ao EmissionsTracker.
        """
        self.wue = wue_liters_per_kwh
        self.carbon_intensity_g_per_kwh = carbon_intensity_g_per_kwh
        self.carbon_intensity = carbon_intensity_g_per_kwh or 0.0
        self.emissions_kg = 0.0
        self.energy_kwh = 0.0
        self.details = MeasurementDetails()

        codecarbon_kwargs.setdefault("log_level", "error")
        codecarbon_kwargs.setdefault("save_to_file", True)
        codecarbon_kwargs.setdefault("output_dir", ".")

        if os.environ.get("CODECARBON_OFFLINE_MODE") == "true":
            codecarbon_kwargs["offline"] = True
        if codecarbon_kwargs.get("offline") and "country_iso_code" not in codecarbon_kwargs:
            codecarbon_kwargs["country_iso_code"] = "BRA"

        self._output_dir: str = codecarbon_kwargs["output_dir"]
        self._output_file: str = codecarbon_kwargs.get("output_file", "emissions.csv")
        self.tracker = EmissionsTracker(**codecarbon_kwargs)

    def start(self) -> None:
        """Inicia a medição de energia e carbono em background."""
        self.tracker.start()

    def stop(self) -> None:
        """
        Para a medição e armazena energia, emissões e procedência.

        Carbono (Seção 4.2.2 do TCC):
          - Com carbon_intensity_g_per_kwh informado: C = E × IC_região.
          - Caso contrário: emissão medida pelo CodeCarbon e IC efetiva derivada.
        """
        measured_emissions = _as_float(self.tracker.stop()) or 0.0
        self.energy_kwh = self._collect_energy()

        if self.carbon_intensity_g_per_kwh is not None:
            self.emissions_kg = calculate_carbon_emissions(
                self.energy_kwh, self.carbon_intensity_g_per_kwh
            )
            self.carbon_intensity = self.carbon_intensity_g_per_kwh
        else:
            self.emissions_kg = measured_emissions
            self.carbon_intensity = (
                measured_emissions / self.energy_kwh * 1000.0 if self.energy_kwh > 0 else 0.0
            )

    def _collect_energy(self) -> float:
        """Obtém a energia da medição recém-encerrada (memória → CSV)."""
        data = getattr(self.tracker, "final_emissions_data", None)
        energy = _as_float(getattr(data, "energy_consumed", None))
        if energy is not None:
            self.details = _details_from(data)
            return energy
        return self._read_energy_from_csv()

    def _read_energy_from_csv(self) -> float:
        """
        Lê ``energy_consumed`` da última linha do CSV do CodeCarbon.

        Raises:
            MeasurementError: se o arquivo não existir, estiver vazio ou malformado.
        """
        csv_path = os.path.join(self._output_dir, self._output_file)
        try:
            last_row = pd.read_csv(csv_path).iloc[-1]
        except (FileNotFoundError, pd.errors.EmptyDataError, IndexError) as exc:
            raise MeasurementError(f"Medição indisponível em '{csv_path}'.") from exc

        energy = _as_float(last_row.get("energy_consumed"))
        if energy is None:
            raise MeasurementError(f"Coluna 'energy_consumed' inválida em '{csv_path}'.")
        self.details = _details_from(last_row)
        return energy

    def get_metrics(self) -> EnvironmentalMetrics:
        """Retorna energia, carbono e água (via WUE). Deve ser chamado após stop()."""
        return EnvironmentalMetrics(
            energy=self.energy_kwh,
            carbon=self.emissions_kg,
            water=calculate_water_usage(self.energy_kwh, self.wue),
        )
