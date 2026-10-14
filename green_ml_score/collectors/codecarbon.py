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


class ProvenanceWarning(UserWarning):
    """A energia reportada é (parcialmente) estimada, e não medida."""


# Acima desta fração, a energia atribuída à RAM domina a medição e as diferenças
# entre modelos passam a refletir sobretudo o tempo de execução.
RAM_SHARE_WARNING_THRESHOLD: float = 0.5


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

    def provenance_warnings(self) -> list[str]:
        """
        Avisos sobre a procedência desta medição isolada.

        Constância da potência de RAM só é detectável entre medições: ver
        ``provenance_warnings_for``.
        """
        warnings_: list[str] = []
        if self.tracking_mode == "machine":
            warnings_.append(
                "tracking_mode = machine: a energia inclui todos os processos da "
                "máquina, não apenas o processo medido."
            )
        share = self.ram_share
        if share is not None and share > RAM_SHARE_WARNING_THRESHOLD:
            warnings_.append(
                f"A RAM responde por {share:.0%} da energia (> "
                f"{RAM_SHARE_WARNING_THRESHOLD:.0%}); diferenças entre modelos "
                "refletem sobretudo o tempo de execução."
            )
        return warnings_


def provenance_warnings_for(details: list[MeasurementDetails]) -> list[str]:
    """
    Avisos de procedência de um conjunto de medições (sem repetição).

    Agrega os avisos individuais (um por tipo) e, quando há ao menos duas medições,
    alerta se a potência de RAM foi idêntica em todas — sinal de que o CodeCarbon
    usou um valor constante estimado, e não uma medição.
    """
    found: list[str] = []
    modes = {d.tracking_mode for d in details}
    if "machine" in modes:
        found.append(
            "tracking_mode = machine: a energia inclui todos os processos da "
            "máquina, não apenas o processo medido."
        )
    shares = [s for d in details if (s := d.ram_share) is not None]
    high = [s for s in shares if s > RAM_SHARE_WARNING_THRESHOLD]
    if high:
        found.append(
            f"A RAM responde por mais de {RAM_SHARE_WARNING_THRESHOLD:.0%} da energia "
            f"em {len(high)} de {len(shares)} medições (máx. {max(high):.0%}); "
            "diferenças entre modelos refletem sobretudo o tempo de execução."
        )
    ram = {d.ram_power_w for d in details if d.ram_power_w is not None}
    n_ram = sum(d.ram_power_w is not None for d in details)
    if n_ram >= 2 and len(ram) == 1:
        found.append(
            f"Potência de RAM constante ({ram.pop():.3f} W) em {n_ram} medições: "
            "valor estimado pelo CodeCarbon, não medido."
        )
    return found


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
    get = (
        source.get
        if isinstance(source, (dict, pd.Series))
        else (lambda key, default=None: getattr(source, key, default))
    )
    values: dict[str, Any] = {}
    for field_name, source_key in _DETAIL_FIELDS.items():
        raw = get(source_key, None)
        is_text = field_name in {
            "tracking_mode",
            "os",
            "cpu_model",
            "codecarbon_version",
        }
        values[field_name] = _as_str(raw) if is_text else _as_float(raw)
    return MeasurementDetails(**values)


def _file_signature(path: str) -> tuple[int, int] | None:
    """Retorna (mtime em ns, tamanho) do arquivo, ou None se ele não existir."""
    try:
        stat = os.stat(path)
    except FileNotFoundError:
        return None
    return stat.st_mtime_ns, stat.st_size


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
        if (
            codecarbon_kwargs.get("offline")
            and "country_iso_code" not in codecarbon_kwargs
        ):
            codecarbon_kwargs["country_iso_code"] = "BRA"

        self._output_dir: str = codecarbon_kwargs["output_dir"]
        self._output_file: str = codecarbon_kwargs.get("output_file", "emissions.csv")
        self._csv_signature_at_start: tuple[int, int] | None = None
        self.tracker = EmissionsTracker(**codecarbon_kwargs)

    @property
    def _csv_path(self) -> str:
        return os.path.join(self._output_dir, self._output_file)

    def start(self) -> None:
        """Inicia a medição de energia e carbono em background."""
        # Estado do CSV antes da medição: permite detectar, na leitura alternativa,
        # que o arquivo não recebeu a linha desta medição (linha antiga ≠ medição).
        self._csv_signature_at_start = _file_signature(self._csv_path)
        self.tracker.start()

    def stop(self) -> None:
        """
        Para a medição e armazena energia, emissões e procedência.

        Carbono (Seção 4.2.2 do TCC):
          - Com carbon_intensity_g_per_kwh informado: C = E × IC_região.
          - Caso contrário: emissão medida pelo CodeCarbon e IC efetiva derivada.
        """
        measured_emissions = _as_float(self.tracker.stop())
        if measured_emissions is None:
            # O CodeCarbon retorna None quando não mediu (tracker não iniciado ou
            # outra instância em execução); emissão nula seria um valor espúrio.
            raise MeasurementError(
                "O CodeCarbon não retornou emissões ao encerrar a medição."
            )
        self.energy_kwh = self._collect_energy()

        if self.carbon_intensity_g_per_kwh is not None:
            self.emissions_kg = calculate_carbon_emissions(
                self.energy_kwh, self.carbon_intensity_g_per_kwh
            )
            self.carbon_intensity = self.carbon_intensity_g_per_kwh
        else:
            self.emissions_kg = measured_emissions
            self.carbon_intensity = (
                measured_emissions / self.energy_kwh * 1000.0
                if self.energy_kwh > 0
                else 0.0
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
            MeasurementError: se o arquivo não existir, estiver vazio, malformado
                ou não tiver sido modificado desde ``start()`` (a última linha
                seria de uma medição anterior).
        """
        csv_path = self._csv_path
        signature = _file_signature(csv_path)
        if signature is not None and signature == self._csv_signature_at_start:
            raise MeasurementError(
                f"'{csv_path}' não foi atualizado durante a medição; "
                "a última linha pertence a uma execução anterior."
            )
        try:
            last_row = pd.read_csv(csv_path).iloc[-1]
        except (FileNotFoundError, pd.errors.EmptyDataError, IndexError) as exc:
            raise MeasurementError(f"Medição indisponível em '{csv_path}'.") from exc

        energy = _as_float(last_row.get("energy_consumed"))
        if energy is None:
            raise MeasurementError(
                f"Coluna 'energy_consumed' inválida em '{csv_path}'."
            )
        self.details = _details_from(last_row)
        return energy

    def get_metrics(self) -> EnvironmentalMetrics:
        """Retorna energia, carbono e água (via WUE). Deve ser chamado após stop()."""
        return EnvironmentalMetrics(
            energy=self.energy_kwh,
            carbon=self.emissions_kg,
            water=calculate_water_usage(self.energy_kwh, self.wue),
        )
