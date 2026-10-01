"""
Módulo de Experimentos Comparativos do GreenML Score.

Este pacote implementa o protocolo experimental descrito na Seção 5 do TCC,
garantindo comparabilidade, reprodutibilidade e rastreabilidade MLOps via MLflow.
"""

from .config import ExperimentConfig
from .dataset import load_dataset

__all__ = ["ExperimentConfig", "load_dataset"]
