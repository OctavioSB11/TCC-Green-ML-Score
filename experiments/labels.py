"""
labels.py: rótulos em português e formatação numérica das figuras do TCC.

Compartilhado por ``generate_results.py`` e ``context_analysis.py`` para que modelos,
datasets e números apareçam da mesma forma em todas as figuras.
"""

from __future__ import annotations

from matplotlib.ticker import FuncFormatter

MODEL_NAMES: dict[str, str] = {
    "Logistic_Regression": "Regressão Logística",
    "Random_Forest": "Random Forest",
    "MLP_Neural_Network": "MLP",
    "XGBoost": "XGBoost",
}
DATASET_NAMES: dict[str, str] = {
    "newsgroups": "20 Newsgroups",
    "breast_cancer": "Breast Cancer",
    "covtype": "Covertype",
}
MODE_NAMES: dict[str, str] = {"full": "", "quick_run": "teste rápido"}


def model_name(model: str) -> str:
    """Nome do modelo em português (o identificador original, se desconhecido)."""
    return MODEL_NAMES.get(model, model)


def figure_title(dataset: str, mode: str, detail: str = "") -> str:
    """Título de figura: nome do dataset e, entre parênteses, modo não padrão e detalhe."""
    extras = [x for x in (MODE_NAMES.get(mode, mode), detail) if x]
    name = DATASET_NAMES.get(dataset, dataset)
    return f"{name} ({', '.join(extras)})" if extras else name


def comma(value: float, decimals: int = 2) -> str:
    """Número com vírgula decimal."""
    return f"{value:.{decimals}f}".replace(".", ",")


def comma_formatter(decimals: int = 2) -> FuncFormatter:
    """Formatador de eixo com vírgula decimal."""
    return FuncFormatter(lambda v, _pos: comma(v, decimals))
