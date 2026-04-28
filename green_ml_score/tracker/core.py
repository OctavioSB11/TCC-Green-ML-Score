from codecarbon import EmissionsTracker
from .metrics import calculate_water_usage
from green_ml_score.greenmlscore import EnvironmentalMetrics

class GreenMLTracker:
    """
    Rastreador principal do GreenML Score.
    Agora potencializado pelo CodeCarbon!
    """

    def __init__(self, wue_liters_per_kwh: float = 1.8, **codecarbon_kwargs):
        self.wue = wue_liters_per_kwh
        self.carbon_intensity = 0.0 # Será preenchido pelo CodeCarbon
        
        # Desliga logs verbosos do CodeCarbon por padrão
        if "log_level" not in codecarbon_kwargs:
            codecarbon_kwargs["log_level"] = "error"
            
        self.tracker = EmissionsTracker(**codecarbon_kwargs)
        self.emissions_kg = 0.0
        self.energy_kwh = 0.0

    def start(self):
        """Inicia a medição de energia e carbono do CodeCarbon em background."""
        self.tracker.start()

    def stop(self):
        """Para a medição e armazena os resultados absolutos."""
        # CodeCarbon retorna o total de carbono em kg
        self.emissions_kg = self.tracker.stop() 
        # Podemos pegar a energia total consumida também
        self.energy_kwh = getattr(self.tracker._total_energy, "kWh", 0.0)

    def get_metrics(self) -> EnvironmentalMetrics:
        """
        Retorna o objeto EnvironmentalMetrics final com base
        na energia gasta, intensidade de carbono e eficiência hídrica.
        """
        water_liters = calculate_water_usage(self.energy_kwh, self.wue)
        
        return EnvironmentalMetrics(
            energy=self.energy_kwh,
            carbon=self.emissions_kg,
            water=water_liters
        )
