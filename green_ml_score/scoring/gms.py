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
    Dados ambientais de um modelo.
    """

    energy: float  # kWh
    carbon: float  # kg CO2
    water: float  # litros


@dataclass
class NormalizationBounds:
    """
    Limites máximos para normalização inversa.

    Pode ser instanciado manualmente ou calculado automaticamente
    a partir de uma lista de métricas via from_metrics_list().
    """

    energy_max: float
    carbon_max: float
    water_max: float

    @staticmethod
    def from_metrics_list(
        metrics_list: list[EnvironmentalMetrics],
    ) -> "NormalizationBounds":
        """
        Calcula os bounds automaticamente a partir dos dados reais dos modelos.

        Uso recomendado para o experimento comparativo — elimina a necessidade
        de definir valores máximos arbitrários antes do experimento.

        Exemplo:
            bounds = NormalizationBounds.from_metrics_list([metrics_a, metrics_b, metrics_c])
        """
        if not metrics_list:
            raise ValueError("A lista de métricas não pode estar vazia.")

        return NormalizationBounds(
            energy_max=max(m.energy for m in metrics_list),
            carbon_max=max(m.carbon for m in metrics_list),
            water_max=max(m.water for m in metrics_list),
        )


@dataclass
class Weights:
    """
    Pesos das dimensões ambientais.

    Padrão: distribuição uniforme (w_E = w_C = w_W = 1/3), conforme
    definido na Seção 6 do TCC — reflete abordagem neutra onde energia,
    carbono e água têm igual relevância.

    Exemplos de configurações contextuais (conforme Seção 7 do TCC):
        Alta intensidade de carbono → Weights(w_E=0.2, w_C=0.5, w_W=0.3)
        Estresse hídrico            → Weights(w_E=0.3, w_C=0.2, w_W=0.5)
    """

    w_E: float = 1 / 3
    w_C: float = 1 / 3
    w_W: float = 1 / 3

    def validate(self):
        total = self.w_E + self.w_C + self.w_W
        if not abs(total - 1.0) < 1e-6:
            raise ValueError("Os pesos devem somar 1.")
        if any(w < 0 for w in [self.w_E, self.w_C, self.w_W]):
            raise ValueError("Os pesos não podem ser negativos.")


# =========================
# FUNÇÕES INTERNAS
# =========================


def _validate_inputs(metrics: EnvironmentalMetrics, bounds: NormalizationBounds):
    if metrics.energy < 0 or metrics.carbon < 0 or metrics.water < 0:
        raise ValueError("Valores ambientais não podem ser negativos.")
    if bounds.energy_max <= 0 or bounds.carbon_max <= 0 or bounds.water_max <= 0:
        raise ValueError("Valores máximos devem ser maiores que zero.")


def _normalize(value: float, max_value: float) -> float:
    """
    Normalização inversa: quanto menor o consumo, maior o score.
    Fórmula: X_norm = 1 - (X / X_max)
    """
    return 1.0 - (value / max_value)


# =========================
# FUNÇÃO PRINCIPAL
# =========================


def calculate_gms(
    metrics: EnvironmentalMetrics,
    bounds: NormalizationBounds,
    weights: Weights = None,
    scale_100: bool = False,
) -> float:
    """
    Calcula o GreenML Score (GMS).

    Parâmetros:
        metrics   : dados ambientais do modelo
        bounds    : valores máximos para normalização
        weights   : pesos das dimensões (padrão: uniforme 1/3 cada)
        scale_100 : retorna score de 0 a 100 se True

    Retorno:
        float: score entre 0 e 1 (ou 0 a 100)
    """
    if weights is None:
        weights = Weights()

    weights.validate()
    _validate_inputs(metrics, bounds)

    E_norm = _normalize(metrics.energy, bounds.energy_max)
    C_norm = _normalize(metrics.carbon, bounds.carbon_max)
    W_norm = _normalize(metrics.water, bounds.water_max)

    gms = weights.w_E * E_norm + weights.w_C * C_norm + weights.w_W * W_norm

    gms = max(0.0, min(1.0, gms))

    return gms * 100 if scale_100 else gms


# =========================
# FUNÇÃO DE DECOMPOSIÇÃO
# =========================


def explain_gms(
    metrics: EnvironmentalMetrics, bounds: NormalizationBounds, weights: Weights = None
) -> dict:
    """
    Retorna a decomposição completa do GMS por dimensão.
    Útil para análise, debug e tabelas do TCC.
    """
    if weights is None:
        weights = Weights()

    weights.validate()
    _validate_inputs(metrics, bounds)

    E_norm = _normalize(metrics.energy, bounds.energy_max)
    C_norm = _normalize(metrics.carbon, bounds.carbon_max)
    W_norm = _normalize(metrics.water, bounds.water_max)

    return {
        "E_norm": round(E_norm, 6),
        "C_norm": round(C_norm, 6),
        "W_norm": round(W_norm, 6),
        "weighted_energy": round(weights.w_E * E_norm, 6),
        "weighted_carbon": round(weights.w_C * C_norm, 6),
        "weighted_water": round(weights.w_W * W_norm, 6),
        "GMS": round(
            weights.w_E * E_norm + weights.w_C * C_norm + weights.w_W * W_norm, 6
        ),
    }
