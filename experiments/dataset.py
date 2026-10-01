"""
dataset.py — Carregamento e pré-processamento dos datasets de benchmark (Seção 5.2).

Não há fallback para dados sintéticos: se um dataset não puder ser obtido, a
execução é interrompida. Resultados obtidos sobre dados substitutos silenciosos
seriam inválidos e indistinguíveis dos reais nos arquivos de saída.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.datasets import fetch_20newsgroups, fetch_covtype, load_breast_cancer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .config import config


class DatasetUnavailableError(RuntimeError):
    """O dataset solicitado não pôde ser obtido (ex.: download sem rede)."""


@dataclass(frozen=True)
class RawDataset:
    """Dataset completo, antes da divisão treino/teste."""

    name: str
    X: Any  # list[str] para texto; np.ndarray para tabular
    y: np.ndarray
    is_text: bool


def _subsample(X: Any, y: np.ndarray, n: int, seed: int) -> tuple[Any, np.ndarray]:
    """Subamostragem estratificada e determinística (semente fixa de dados)."""
    if len(y) <= n:
        return X, y
    idx, _ = train_test_split(
        np.arange(len(y)), train_size=n, random_state=seed, stratify=y
    )
    X_sub = [X[i] for i in idx] if isinstance(X, list) else X[idx]
    return X_sub, y[idx]


def load_raw_dataset(name: str, quick_run: bool = False) -> RawDataset:
    """
    Carrega o dataset completo (sem divisão).

    Raises:
        ValueError: nome de dataset não suportado.
        DatasetUnavailableError: falha ao obter os dados.
    """
    if name not in config.AVAILABLE_DATASETS:
        raise ValueError(f"Dataset {name} não suportado: {config.AVAILABLE_DATASETS}")

    try:
        if name == "newsgroups":
            bunch = fetch_20newsgroups(
                subset="all",
                categories=config.NEWSGROUPS_CATEGORIES,
                remove=("headers", "footers", "quotes"),
                random_state=config.DATA_SAMPLE_SEED,
            )
            X, y, is_text = list(bunch.data), np.asarray(bunch.target), True
        elif name == "breast_cancer":
            bunch = load_breast_cancer()
            X, y, is_text = bunch.data, np.asarray(bunch.target), False
        else:  # covtype: binarizado (classe 2 vs. demais) e subamostrado
            bunch = fetch_covtype()
            X, y, is_text = bunch.data, (bunch.target == 2).astype(int), False
            X, y = _subsample(X, y, config.COVTYPE_N_SAMPLES, config.DATA_SAMPLE_SEED)
    except OSError as exc:  # inclui falhas de rede (URLError) e de disco
        raise DatasetUnavailableError(
            f"Não foi possível obter o dataset '{name}'. Verifique a conexão ou o "
            "cache do scikit-learn (~/scikit_learn_data)."
        ) from exc

    if quick_run:
        X, y = _subsample(X, y, config.QUICK_RUN_SAMPLES, config.DATA_SAMPLE_SEED)

    return RawDataset(name=name, X=X, y=y, is_text=is_text)


def split_dataset(raw: RawDataset, seed: int) -> tuple[Any, Any, np.ndarray, np.ndarray]:
    """Divisão treino/teste estratificada, dependente da semente."""
    return train_test_split(
        raw.X, raw.y, test_size=config.TEST_SIZE, random_state=seed, stratify=raw.y
    )


def preprocess_features(X_train: Any, X_test: Any, is_text: bool) -> tuple[Any, Any, Any]:
    """TF-IDF para texto e StandardScaler para dados tabulares (ajustados só no treino)."""
    if is_text:
        transformer: Any = TfidfVectorizer(
            max_features=config.MAX_TFIDF_FEATURES,
            stop_words="english",
            sublinear_tf=True,
        )
    else:
        transformer = StandardScaler()
    return transformer.fit_transform(X_train), transformer.transform(X_test), transformer
