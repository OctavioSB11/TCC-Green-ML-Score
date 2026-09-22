"""
dataset.py — Carregador e Pré-processador de Dataset de Benchmark (Seção 5.2 do TCC).

Provedor de dados robusto e ágil para experimentos comparativos.
Suporta dados textuais (Newsgroups) e tabulares (Breast Cancer, Covtype).
"""

import pandas as pd
from sklearn.datasets import fetch_20newsgroups, fetch_covtype, load_breast_cancer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .config import config


def load_dataset(
    name: str = "newsgroups", quick_run: bool = False, random_state: int = 42
) -> tuple[list | pd.DataFrame, list | pd.DataFrame, list, list, bool]:
    """
    Carrega o dataset selecionado.

    Retorna:
        (X_train, X_test, y_train, y_test, is_text)
    """
    if name not in config.AVAILABLE_DATASETS:
        raise ValueError(
            f"Dataset {name} não suportado. Escolha entre: {config.AVAILABLE_DATASETS}"
        )

    is_text = False

    if name == "newsgroups":
        is_text = True
        try:
            categories = ["rec.autos", "sci.med"]
            dataset = fetch_20newsgroups(
                subset="all",
                categories=categories,
                remove=("headers", "footers", "quotes"),
                random_state=random_state,
            )
            data_x = dataset.data
            labels = dataset.target
        except Exception:
            data_x = ["Car engine speed", "Medical clinical care"] * 500
            labels = [0, 1] * 500

    elif name == "breast_cancer":
        dataset = load_breast_cancer()
        data_x = dataset.data
        labels = dataset.target

    elif name == "covtype":
        # fetch_covtype pode ser grande, limitamos
        dataset = fetch_covtype()
        data_x = dataset.data
        labels = dataset.target
        # Binarizando covtype para manter compatibilidade binária (classe 1 e 2 dominam)
        labels = (labels == 2).astype(int)

        n_samples_limit = 500 if quick_run else config.COVTYPE_N_SAMPLES
        df = pd.DataFrame(data_x)
        df["label"] = labels
        df_sampled = df.sample(n=n_samples_limit, random_state=random_state)
        data_x = df_sampled.drop(columns=["label"]).values
        labels = df_sampled["label"].values

    if quick_run and name != "covtype":
        n_samples = 500
        if isinstance(data_x, list) and len(data_x) > n_samples:
            df = pd.DataFrame({"text": data_x, "label": labels})
            df_sampled = df.sample(n=n_samples, random_state=random_state)
            data_x = df_sampled["text"].tolist()
            labels = df_sampled["label"].tolist()
        elif hasattr(data_x, "shape") and data_x.shape[0] > n_samples:
            df = pd.DataFrame(data_x)
            df["label"] = labels
            df_sampled = df.sample(n=n_samples, random_state=random_state)
            data_x = df_sampled.drop(columns=["label"]).values
            labels = df_sampled["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        data_x,
        labels,
        test_size=config.TEST_SIZE,
        random_state=random_state,
        stratify=labels if len(set(labels)) > 1 else None,
    )

    return X_train, X_test, y_train, y_test, is_text


def preprocess_features(
    X_train: list | object, X_test: list | object, is_text: bool
) -> tuple[object, object, object]:
    """
    Aplica TF-IDF para textos e StandardScaler para dados tabulares numéricos.
    """
    if is_text:
        vectorizer = TfidfVectorizer(
            max_features=config.MAX_TFIDF_FEATURES,
            stop_words="english",
            sublinear_tf=True,
        )
        X_train_processed = vectorizer.fit_transform(X_train)
        X_test_processed = vectorizer.transform(X_test)
        return X_train_processed, X_test_processed, vectorizer
    else:
        scaler = StandardScaler()
        X_train_processed = scaler.fit_transform(X_train)
        X_test_processed = scaler.transform(X_test)
        return X_train_processed, X_test_processed, scaler
