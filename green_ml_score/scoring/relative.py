"""
Score relativo a um modelo de referência.

O GMS é relativo ao conjunto avaliado (depende do pior modelo). Para uma leitura
absoluta e interpretável, cada modelo é comparado a uma referência fixa por
dataset (ex.: Regressão Logística):

    razão de energia      r  = E_modelo / E_ref
    custo marginal        CM = (E_modelo − E_ref) / ΔF1     [J por ponto de F1]

com ΔF1 = 100 · (F1_modelo − F1_ref), em pontos percentuais. O custo marginal só é
definido quando o modelo é mais preciso que a referência (ΔF1 > 0); quando
ΔF1 ≤ 0, o modelo é marcado como dominado.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

KWH_TO_J: float = 3.6e6


@dataclass(frozen=True)
class RelativeScore:
    """
    Comparação de um modelo com a referência.

    Atributos:
        energy_ratio          : E_modelo / E_ref (adimensional).
        delta_f1_points       : 100 · (F1_modelo − F1_ref).
        marginal_cost_j_per_f1_point : (E_modelo − E_ref) em J dividido por ΔF1;
                                ``nan`` quando ΔF1 ≤ 0 ou para a própria referência.
        dominated             : True quando ΔF1 ≤ 0 (o modelo não melhora a F1 da
                                referência); False para a referência.
        is_reference          : True para o próprio modelo de referência.
    """

    energy_ratio: float
    delta_f1_points: float
    marginal_cost_j_per_f1_point: float
    dominated: bool
    is_reference: bool = False


def relative_to_reference(
    energy_kwh: float,
    f1: float,
    reference_energy_kwh: float,
    reference_f1: float,
    is_reference: bool = False,
) -> RelativeScore:
    """
    Compara um modelo (energia em kWh, F1 em [0, 1]) com a referência.

    Raises:
        ValueError: energia negativa, energia de referência não positiva ou F1
            fora de [0, 1].
    """
    if energy_kwh < 0:
        raise ValueError("energy_kwh não pode ser negativo.")
    if reference_energy_kwh <= 0:
        raise ValueError("A energia da referência deve ser maior que zero.")
    for value in (f1, reference_f1):
        if not 0.0 <= value <= 1.0:
            raise ValueError("F1 deve estar em [0, 1].")

    ratio = energy_kwh / reference_energy_kwh
    delta = 100.0 * (f1 - reference_f1)
    if is_reference:
        return RelativeScore(ratio, delta, math.nan, dominated=False, is_reference=True)
    if delta <= 0:
        return RelativeScore(ratio, delta, math.nan, dominated=True)
    cost = (energy_kwh - reference_energy_kwh) * KWH_TO_J / delta
    return RelativeScore(ratio, delta, cost, dominated=False)
