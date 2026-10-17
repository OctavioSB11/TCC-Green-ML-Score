def calculate_water_usage(energy_kwh: float, wue_liters_per_kwh: float = 1.8) -> float:
    """
    Estima o consumo hídrico com base na equação do TCC:
        W ≈ Energia (kWh) × WUE (litros/kWh)

    Referência: Seção 2.8 do TCC — GreenML Score.

    Parâmetros:
        energy_kwh         : energia consumida em kWh
        wue_liters_per_kwh : WUE do ambiente (litros por kWh).
                             Valores de referência:
                               Microsoft, média global FY24 = 0.30 L/kWh
                               Média indústria      ≈ 1.8 L/kWh
                               Instalações otimizadas (ar) ≈ 0.2 L/kWh

    Retorno:
        float: estimativa de água consumida em litros
    """
    if energy_kwh < 0:
        raise ValueError("energy_kwh não pode ser negativo.")
    if wue_liters_per_kwh < 0:
        raise ValueError("wue_liters_per_kwh não pode ser negativo.")

    return energy_kwh * wue_liters_per_kwh
