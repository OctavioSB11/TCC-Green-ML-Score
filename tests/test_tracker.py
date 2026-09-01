"""
test_tracker.py — Testes unitários para o módulo GreenMLTracker (CodeCarbon Collector).

Aplica o padrão CTFL / ISTQB:
- Testes isolados de hardware utilizando Mocks/Stubs para EmissionsTracker.
- Partição de equivalência para cálculo de carbono (regional explícito vs. derivado do CodeCarbon).
- Teste de robustez e tratamento de exceção (resiliência caso emissions.csv não exista).
"""

from unittest.mock import MagicMock, patch
import pytest

from green_ml_score.collectors.codecarbon import GreenMLTracker
from green_ml_score.scoring.gms import EnvironmentalMetrics


def test_tracker_initialization_defaults():
    """Valida valores e configurações padrão na instanciação do GreenMLTracker."""
    tracker = GreenMLTracker(output_dir=".")

    assert tracker.wue == 1.8
    assert tracker.carbon_intensity_g_per_kwh is None
    assert tracker.carbon_intensity == 0.0
    assert tracker.emissions_kg == 0.0
    assert tracker.energy_kwh == 0.0


@patch("green_ml_score.collectors.codecarbon.EmissionsTracker")
def test_tracker_start_and_stop_lifecycle(mock_emissions_tracker_cls):
    """Testa o ciclo de vida start -> stop delegando para o CodeCarbon subjacente."""
    # Arrange
    mock_instance = MagicMock()
    mock_instance.stop.return_value = 0.0005
    mock_emissions_tracker_cls.return_value = mock_instance

    tracker = GreenMLTracker(output_dir=".")
    tracker._read_energy_from_csv = MagicMock(return_value=0.002)

    # Act
    tracker.start()
    tracker.stop()
    metrics = tracker.get_metrics()

    # Assert
    mock_instance.start.assert_called_once()
    mock_instance.stop.assert_called_once()
    assert tracker.energy_kwh == 0.002
    assert isinstance(metrics, EnvironmentalMetrics)
    assert metrics.energy == 0.002
    assert metrics.carbon == 0.0005
    assert metrics.water == pytest.approx(0.002 * 1.8)


def test_tracker_read_energy_from_csv_success(mock_emissions_csv_path):
    """Testa a leitura correta de energy_consumed do arquivo emissions.csv real."""
    tracker = GreenMLTracker(output_dir=mock_emissions_csv_path)

    energy = tracker._read_energy_from_csv()

    # No mock_emissions_csv_path, o valor de energy_consumed é 0.0015
    assert energy == pytest.approx(0.0015)


def test_tracker_read_energy_missing_csv_safe_fallback(tmp_path):
    """Testa a resiliência do tracker quando o arquivo emissions.csv não existe (retorna 0.0)."""
    tracker = GreenMLTracker(output_dir=str(tmp_path))

    energy = tracker._read_energy_from_csv()

    assert energy == 0.0


@patch("green_ml_score.collectors.codecarbon.EmissionsTracker")
def test_tracker_with_regional_carbon_intensity(mock_emissions_tracker_cls):
    """Testa cálculo de carbono com IC regional fornecido (fórmula C = E * IC / 1000)."""
    # Arrange
    mock_instance = MagicMock()
    mock_instance.stop.return_value = (
        0.999  # Valor bruto que deve ser sobrescrito pela fórmula
    )
    mock_emissions_tracker_cls.return_value = mock_instance

    tracker = GreenMLTracker(
        carbon_intensity_g_per_kwh=120.0,
        wue_liters_per_kwh=0.52,
        output_dir=".",
    )
    tracker._read_energy_from_csv = MagicMock(return_value=2.0)

    # Act
    tracker.start()
    tracker.stop()
    metrics = tracker.get_metrics()

    # Assert
    # 2.0 kWh * 120 g/kWh / 1000 = 0.24 kg CO2e
    assert metrics.carbon == pytest.approx(0.24)
    assert tracker.carbon_intensity == 120.0
    # 2.0 kWh * 0.52 L/kWh = 1.04 L
    assert metrics.water == pytest.approx(1.04)


@patch("green_ml_score.collectors.codecarbon.EmissionsTracker")
def test_tracker_derived_effective_carbon_intensity(mock_emissions_tracker_cls):
    """Testa cálculo de intensidade efetiva quando IC_região não é passado (IC = emissões / energia * 1000)."""
    mock_instance = MagicMock()
    mock_instance.stop.return_value = 0.0003  # 0.0003 kg = 0.3g
    mock_emissions_tracker_cls.return_value = mock_instance

    tracker = GreenMLTracker(output_dir=".")
    tracker._read_energy_from_csv = MagicMock(return_value=0.001)  # 0.001 kWh

    tracker.stop()

    assert tracker.emissions_kg == 0.0003
    # IC efetiva = (0.0003 / 0.001) * 1000 = 300.0 gCO2e/kWh
    assert tracker.carbon_intensity == pytest.approx(300.0)
