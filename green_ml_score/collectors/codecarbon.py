"""
GreenMLTracker — rastreamento de energia e carbono via CodeCarbon.
"""

import os

import pandas as pd
from codecarbon import EmissionsTracker

from green_ml_score.estimators.carbon import calculate_carbon_emissions
from green_ml_score.estimators.water import calculate_water_usage
from green_ml_score.scoring.gms import EnvironmentalMetrics


class GreenMLTracker:
    """
    Rastreador principal do GreenML Score.
    Utiliza o CodeCarbon para medição real de energia e carbono.

    A energia é lida do emissions.csv gerado pelo CodeCarbon —
    abordagem robusta que não depende de atributos internos da biblioteca,
    os quais mudam entre versões.
    """

    def __init__(
        self,
        wue_liters_per_kwh: float = 1.8,
        carbon_intensity_g_per_kwh: float = None,
        **codecarbon_kwargs
    ):
        """
        Parâmetros:
            wue_liters_per_kwh : WUE do ambiente de execução (L/kWh).
                                 Padrão 1.8 = média da indústria de data centers.
                                 Para Google Cloud (2024) use 0.52; Azure use 1.1.
                                 Em máquina local, o valor é uma estimativa.
            carbon_intensity_g_per_kwh : intensidade de carbono regional (gCO2e/kWh),
                                 conforme Seção 4.2.2 do TCC (C = E × IC_região).
                                 Se informado, o carbono é calculado pela fórmula do
                                 TCC. Se None, usa a emissão medida pelo CodeCarbon e
                                 deriva a IC efetiva a partir de emissão/energia.
                                 Ex.: São Paulo ≈ 120; Estados Unidos ≈ 380.
            **codecarbon_kwargs: argumentos repassados ao EmissionsTracker.
        """
        self.wue = wue_liters_per_kwh
        self.carbon_intensity_g_per_kwh = carbon_intensity_g_per_kwh
        self.carbon_intensity = carbon_intensity_g_per_kwh or 0.0
        self.emissions_kg = 0.0
        self.energy_kwh = 0.0

        # Suprime logs verbosos por padrão
        if "log_level" not in codecarbon_kwargs:
            codecarbon_kwargs["log_level"] = "error"

        # Garante gravação do CSV — é a fonte confiável de energy_consumed
        if "save_to_file" not in codecarbon_kwargs:
            codecarbon_kwargs["save_to_file"] = True
        if "output_dir" not in codecarbon_kwargs:
            codecarbon_kwargs["output_dir"] = "."

        # Resiliência para CI/headless: se CODECARBON_OFFLINE_MODE estiver ativo ou offline for True
        if os.environ.get("CODECARBON_OFFLINE_MODE") == "true":
            codecarbon_kwargs["offline"] = True

        if (
            codecarbon_kwargs.get("offline")
            and "country_iso_code" not in codecarbon_kwargs
        ):
            codecarbon_kwargs["country_iso_code"] = "BRA"

        self._output_dir = codecarbon_kwargs["output_dir"]
        self.tracker = EmissionsTracker(**codecarbon_kwargs)

    def start(self):
        """Inicia a medição de energia e carbono em background."""
        self.tracker.start()

    def stop(self):
        """
        Para a medição e armazena energia e emissões.

        A energia vem da última linha do emissions.csv — mais confiável que
        acessar tracker._total_energy, cujo comportamento mudou no CodeCarbon 2.x.

        Carbono (Seção 4.2.2 do TCC):
          - Se carbon_intensity_g_per_kwh foi informado, aplica a fórmula
            C = E × IC_região, garantindo coerência com a metodologia do TCC.
          - Caso contrário, usa a emissão medida pelo CodeCarbon e deriva a IC
            efetiva (emissão/energia) para registro, evitando logar IC = 0.
        """
        measured_emissions = self.tracker.stop() or 0.0
        self.energy_kwh = self._read_energy_from_csv()

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

    def _read_energy_from_csv(self) -> float:
        """
        Lê energy_consumed da última linha do emissions.csv.
        Retorna 0.0 com segurança se o arquivo não existir ou estiver malformado.
        """
        csv_path = os.path.join(self._output_dir, "emissions.csv")
        try:
            df = pd.read_csv(csv_path)
            if "energy_consumed" in df.columns and not df.empty:
                return float(df.iloc[-1]["energy_consumed"])
        except Exception:
            pass
        return 0.0

    def get_metrics(self) -> EnvironmentalMetrics:
        """
        Retorna EnvironmentalMetrics com energia, carbono e água estimada via WUE.
        Deve ser chamado após stop().
        """
        water_liters = calculate_water_usage(self.energy_kwh, self.wue)

        return EnvironmentalMetrics(
            energy=self.energy_kwh,
            carbon=self.emissions_kg,
            water=water_liters,
        )
