"""
Score relativo a um modelo de referência.

O GMS é relativo ao conjunto avaliado (depende do pior modelo). Para uma leitura
absoluta e interpretável, cada modelo é comparado a uma referência fixa por
dataset (ex.: Regressão Logística):

    razão de energia      r  = E_modelo / E_ref
    custo marginal        CM = (E_modelo − E_ref) / ΔF1     [J por ponto de F1]

com ΔF1 = 100 · (F1_modelo − F1_ref), em pontos percentuais. O custo marginal só é
definido quando o modelo é mais preciso que a referência (ΔF1 > 0).

Dominância (``pareto_dominated``) segue o sentido de Pareto nos eixos F1 e energia,
sobre TODOS os modelos de uma mesma execução (dataset e semente): um modelo é
dominado se outro tem F1 maior ou igual E energia menor ou igual, sendo
estritamente melhor em ao menos um dos dois. Assim, a marcação coincide com a
fronteira de Pareto das figuras; um modelo menos preciso porém mais econômico não
é dominado, pois representa um compromisso legítimo entre os dois eixos.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

KWH_TO_J: float = 3.6e6

# Posição do modelo em relação à referência (quadrantes do plano F1 × energia)
REFERENCE = "referencia"
WORSE = "pior_que_referencia"  # ΔF1 ≤ 0 e E ≥ E_ref
BETTER = "melhor_que_referencia"  # ΔF1 ≥ 0 e E ≤ E_ref (ao menos uma estrita)
COSTLIER_BETTER = "mais_caro_mais_preciso"  # ΔF1 > 0 e E > E_ref
CHEAPER_WORSE = "mais_barato_menos_preciso"  # ΔF1 < 0 e E < E_ref


@dataclass(frozen=True)
class RelativeScore:
    """
    Comparação de um modelo com a referência.

    Atributos:
        energy_ratio          : E_modelo / E_ref (adimensional).
        delta_f1_points       : 100 · (F1_modelo − F1_ref).
        marginal_cost_j_per_f1_point : (E_modelo − E_ref) em J dividido por ΔF1;
                                ``nan`` quando ΔF1 ≤ 0 ou para a própria referência.
        position              : quadrante em relação à referência (``REFERENCE``,
                                ``WORSE``, ``BETTER``, ``COSTLIER_BETTER``,
                                ``CHEAPER_WORSE``).
        is_reference          : True para o próprio modelo de referência.
    """

    energy_ratio: float
    delta_f1_points: float
    marginal_cost_j_per_f1_point: float
    position: str
    is_reference: bool = False


def _position(delta_f1: float, energy: float, reference_energy: float) -> str:
    better = delta_f1 > 0
    worse = delta_f1 < 0
    cheaper = energy < reference_energy
    costlier = energy > reference_energy
    if not better and not cheaper:
        return WORSE
    if not worse and not costlier:
        return BETTER
    return COSTLIER_BETTER if better else CHEAPER_WORSE


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
        return RelativeScore(ratio, delta, math.nan, REFERENCE, is_reference=True)
    position = _position(delta, energy_kwh, reference_energy_kwh)
    cost = (
        (energy_kwh - reference_energy_kwh) * KWH_TO_J / delta
        if delta > 0
        else math.nan
    )
    return RelativeScore(ratio, delta, cost, position)


def pareto_dominated(energy: Sequence[float], f1: Sequence[float]) -> np.ndarray:
    """
    Máscara de dominância de Pareto (minimizar energia, maximizar F1).

    O elemento i é dominado se existe j com E_j ≤ E_i e F1_j ≥ F1_i, sendo ao
    menos uma das desigualdades estrita. Pontos idênticos não se dominam.
    """
    e, f = np.asarray(energy, float), np.asarray(f1, float)
    if e.shape != f.shape or e.ndim != 1:
        raise ValueError("energy e f1 devem ser vetores de mesmo tamanho.")
    no_worse = (e[None, :] <= e[:, None]) & (f[None, :] >= f[:, None])
    strictly = (e[None, :] < e[:, None]) | (f[None, :] > f[:, None])
    return (no_worse & strictly).any(axis=1)
