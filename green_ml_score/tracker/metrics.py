def calculate_water_usage(energy_kwh: float, wue_liters_per_kwh: float = 1.8) -> float:
    """
    Calcula o uso de água baseado na equação do artigo TCC:
    W ≈ Energia (kWh) × WUE (litros/kWh)
    
    Um WUE médio de Data Centers é ~1.8 L/kWh.
    """
    return energy_kwh * wue_liters_per_kwh
