"""
Avaliação do conjunto de configurações modelo × contexto de execução.

Responde à pergunta de pesquisa revisada: em que medida carbono e água,
contextualizados por região e horário, alteram a seleção de configurações em
relação a um critério baseado apenas em energia.

Para cada configuração (modelo, contexto), C e W são derivados da energia do modelo
e dos fatores do contexto. O GMS é calculado com limites de normalização sobre
TODAS as configurações, de modo que modelos e contextos disputem a mesma escala.
A concordância com o critério energético é medida pelo τ_b de Kendall entre o
ranking do GMS e o ranking por energia; a robustez à escolha dos pesos, por uma
varredura no simplex (w_E, w_C, w_W).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from green_ml_score.contexts.execution_context import ExecutionContext
from green_ml_score.scoring.gms import NormalizationBounds, Weights, calculate_gms

_TIE_TOL: float = 1e-12


def kendall_tau_b(x: Sequence[float], y: Sequence[float]) -> float:
    """
    τ_b de Kendall entre ``x`` e ``y``, com correção para empates.

    Diferenças menores que ``1e-12`` (relativas à amplitude da série) são tratadas
    como empate, para que ruído de ponto flutuante não crie ordens espúrias.
    Retorna ``nan`` quando uma das séries é constante.
    """
    a, b = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("x e y devem ser vetores de mesmo tamanho.")
    if a.size < 2:
        raise ValueError("São necessários ao menos dois elementos.")

    def pair_signs(v: np.ndarray) -> np.ndarray:
        diff = v[:, None] - v[None, :]
        tol = _TIE_TOL * max(float(np.ptp(v)), 1.0)
        signs = np.sign(diff) * (np.abs(diff) > tol)
        return signs[np.triu_indices(v.size, k=1)]

    sa, sb = pair_signs(a), pair_signs(b)
    n_pairs = sa.size
    denom = np.sqrt((n_pairs - np.sum(sa == 0)) * (n_pairs - np.sum(sb == 0)))
    return float(np.sum(sa * sb) / denom) if denom > 0 else float("nan")


def simplex_grid(step: float = 0.05) -> list[Weights]:
    """Todos os pesos (w_E, w_C, w_W) múltiplos de ``step`` que somam 1."""
    k = round(1.0 / step)
    if k < 1 or not np.isclose(k * step, 1.0):
        raise ValueError("step deve dividir 1 exatamente (ex.: 0.1, 0.05).")
    return [
        Weights(i / k, j / k, (k - i - j) / k)
        for i in range(k + 1)
        for j in range(k + 1 - i)
    ]


@dataclass
class ContextEvaluation:
    """
    Resultado da avaliação modelo × contexto.

    Atributos:
        configurations : uma linha por configuração, com E, C, W, GMS e rankings.
        kendall_tau    : τ_b entre o ranking do GMS (pesos informados) e o por energia.
        sensitivity    : uma linha por ponto do simplex de pesos, com τ_b e a
                         configuração de maior GMS.
        energy_best_model : modelo de menor energia (critério só-energia).
    """

    configurations: pd.DataFrame
    kendall_tau: float
    sensitivity: pd.DataFrame
    energy_best_model: str
    weights: Weights = field(default_factory=Weights)

    @property
    def selection_change_share(self) -> float:
        """Fração do simplex em que o melhor GMS NÃO usa o modelo de menor energia."""
        return float((~self.sensitivity["best_uses_energy_best_model"]).mean())

    def summary(self) -> dict[str, float | str | int]:
        """Indicadores principais para relatório."""
        tau = self.sensitivity["kendall_tau"]
        return {
            "n_models": int(self.configurations["model"].nunique()),
            "n_contexts": int(self.configurations["context"].nunique()),
            "n_configurations": len(self.configurations),
            "kendall_tau": self.kendall_tau,
            "kendall_tau_min_simplex": float(tau.min()),
            "kendall_tau_median_simplex": float(tau.median()),
            "kendall_tau_max_simplex": float(tau.max()),
            "energy_best_model": self.energy_best_model,
            "selection_change_share": self.selection_change_share,
        }


def evaluate_configurations(
    model_energy_kwh: Mapping[str, float],
    contexts: Sequence[ExecutionContext],
    weights: Weights | None = None,
    simplex_step: float = 0.05,
) -> ContextEvaluation:
    """
    Avalia todas as configurações modelo × contexto.

    Parâmetros:
        model_energy_kwh : energia por execução de cada modelo (kWh), tipicamente a
                           mediana entre sementes.
        contexts         : contextos de execução (rótulos únicos).
        weights          : pesos do GMS principal (padrão: 1/3 cada).
        simplex_step     : resolução da varredura de pesos.
    """
    if not model_energy_kwh:
        raise ValueError("Informe a energia de ao menos um modelo.")
    if not contexts:
        raise ValueError("Informe ao menos um contexto de execução.")
    labels = [c.label for c in contexts]
    if len(set(labels)) != len(labels):
        raise ValueError("Os contextos devem ter rótulos (nome + horário) únicos.")
    weights = weights or Weights()
    weights.validate()

    keys, metrics = [], []
    for model, energy in model_energy_kwh.items():
        for ctx in contexts:
            keys.append((model, ctx))
            metrics.append(ctx.metrics(float(energy)))
    bounds = NormalizationBounds.from_metrics_list(metrics)

    configs = pd.DataFrame(
        {
            "model": [m for m, _ in keys],
            "context": [c.label for _, c in keys],
            "region": [c.name for _, c in keys],
            "hour": [c.hour for _, c in keys],
            "energy_kwh": [m.energy for m in metrics],
            "carbon_kg": [m.carbon for m in metrics],
            "water_l": [m.water for m in metrics],
            "gms": [calculate_gms(m, bounds, weights, scale_100=True) for m in metrics],
        }
    )
    configs["rank_gms"] = configs["gms"].rank(ascending=False, method="min").astype(int)
    configs["rank_energy"] = configs["energy_kwh"].rank(method="min").astype(int)

    # Componentes normalizados: GMS(w) = N · w para qualquer ponto do simplex.
    norms = 1.0 - configs[["energy_kwh", "carbon_kg", "water_l"]].to_numpy() / np.array(
        [bounds.energy_max, bounds.carbon_max, bounds.water_max]
    )
    neg_energy = -configs["energy_kwh"].to_numpy()
    energies = pd.Series(model_energy_kwh, dtype=float)
    energy_best = str(energies.idxmin())

    rows = []
    for w in simplex_grid(simplex_step):
        gms = norms @ np.array([w.w_E, w.w_C, w.w_W])
        best = int(np.argmax(gms))
        rows.append(
            {
                "w_E": w.w_E,
                "w_C": w.w_C,
                "w_W": w.w_W,
                "kendall_tau": kendall_tau_b(gms, neg_energy),
                "best_configuration": f"{keys[best][0]} | {keys[best][1].label}",
                "best_uses_energy_best_model": keys[best][0] == energy_best,
            }
        )

    return ContextEvaluation(
        configurations=configs.sort_values("rank_gms").reset_index(drop=True),
        kendall_tau=kendall_tau_b(configs["gms"], neg_energy),
        sensitivity=pd.DataFrame(rows),
        energy_best_model=energy_best,
        weights=weights,
    )
