"""
GreenML Score (GMS)
Biblioteca para cálculo de impacto ambiental em modelos de Machine Learning

Autor: Projeto TCC - GreenML
"""

from dataclasses import dataclass


# =========================
# MODELOS DE DADOS
# =========================

@dataclass
class EnvironmentalMetrics:
    """
    Dados ambientais do modelo
    """
    energy: float   # kWh
    carbon: float   # kg CO2
    water: float    # litros


@dataclass
class NormalizationBounds:
    """
    Limites máximos para normalização
    """
    energy_max: float
    carbon_max: float
    water_max: float


@dataclass
class Weights:
    """
    Pesos das dimensões ambientais
    """
    w_E: float = 0.4
    w_C: float = 0.4
    w_W: float = 0.2

    def validate(self):
        total = self.w_E + self.w_C + self.w_W
        if not abs(total - 1.0) < 1e-6:
            raise ValueError("Os pesos devem somar 1.")

        if any(w < 0 for w in [self.w_E, self.w_C, self.w_W]):
            raise ValueError("Os pesos não podem ser negativos.")


# =========================
# FUNÇÕES INTERNAS
# =========================

def _validate_inputs(metrics: EnvironmentalMetrics,
                     bounds: NormalizationBounds):
    if metrics.energy < 0 or metrics.carbon < 0 or metrics.water < 0:
        raise ValueError("Valores ambientais não podem ser negativos.")

    if bounds.energy_max <= 0 or bounds.carbon_max <= 0 or bounds.water_max <= 0:
        raise ValueError("Valores máximos devem ser maiores que zero.")


def _normalize(value: float, max_value: float) -> float:
    """
    Normalização inversa (quanto menor o consumo, melhor o score)
    """
    return 1 - (value / max_value)


# =========================
# FUNÇÃO PRINCIPAL
# =========================

def calculate_gms(metrics: EnvironmentalMetrics,
                  bounds: NormalizationBounds,
                  weights: Weights = Weights(),
                  scale_100: bool = False) -> float:
    """
    Calcula o GreenML Score (GMS)

    Parâmetros:
        metrics: dados ambientais do modelo
        bounds: valores máximos para normalização
        weights: pesos das dimensões
        scale_100: retorna score de 0 a 100 se True

    Retorno:
        float: score entre 0 e 1 (ou 0 a 100)
    """

    weights.validate()
    _validate_inputs(metrics, bounds)

    E_norm = _normalize(metrics.energy, bounds.energy_max)
    C_norm = _normalize(metrics.carbon, bounds.carbon_max)
    W_norm = _normalize(metrics.water, bounds.water_max)

    gms = (
        weights.w_E * E_norm +
        weights.w_C * C_norm +
        weights.w_W * W_norm
    )

    # Garantir limites
    gms = max(0.0, min(1.0, gms))

    return gms * 100 if scale_100 else gms

# =========================
# FUNÇÃO DEBUG (OPCIONAL)
# =========================

def explain_gms(metrics: EnvironmentalMetrics,
                bounds: NormalizationBounds,
                weights: Weights = Weights()):
    """
    Retorna decomposição do GMS (ótimo para análise e TCC)
    """

    weights.validate()
    _validate_inputs(metrics, bounds)

    E_norm = _normalize(metrics.energy, bounds.energy_max)
    C_norm = _normalize(metrics.carbon, bounds.carbon_max)
    W_norm = _normalize(metrics.water, bounds.water_max)

    result = {
        "E_norm": E_norm,
        "C_norm": C_norm,
        "W_norm": W_norm,
        "weighted_energy": weights.w_E * E_norm,
        "weighted_carbon": weights.w_C * C_norm,
        "weighted_water": weights.w_W * W_norm,
        "GMS": (
            weights.w_E * E_norm +
            weights.w_C * C_norm +
            weights.w_W * W_norm
        )
    }

    return result