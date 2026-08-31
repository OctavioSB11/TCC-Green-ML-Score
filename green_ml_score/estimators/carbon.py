def calculate_carbon_emissions(
    energy_kwh: float, carbon_intensity_g_per_kwh: float
) -> float:
    """
    Calcula as emissões de carbono a partir da fórmula do TCC:
        C = E (kWh) × IC_região (gCO2e/kWh)

    Referência: Seção 4.2.2 do TCC — GreenML Score.

    A intensidade de carbono (IC) depende da matriz elétrica da região de
    execução. Valores aproximados (International Energy Agency, 2024):
        Brasil          ~100 a 150 gCO2e/kWh
        União Europeia  ~250 a 300 gCO2e/kWh
        Estados Unidos  ~370 a 400 gCO2e/kWh
        China           ~580 a 600 gCO2e/kWh
        Índia           ~700 a 750 gCO2e/kWh

    Parâmetros:
        energy_kwh                 : energia consumida em kWh
        carbon_intensity_g_per_kwh : intensidade de carbono regional (gCO2e/kWh)

    Retorno:
        float: emissões estimadas em kg CO2e
    """
    if energy_kwh < 0:
        raise ValueError("energy_kwh não pode ser negativo.")
    if carbon_intensity_g_per_kwh < 0:
        raise ValueError("carbon_intensity_g_per_kwh não pode ser negativo.")

    # IC em gCO2e/kWh → divide por 1000 para retornar em kg CO2e
    return energy_kwh * carbon_intensity_g_per_kwh / 1000.0
