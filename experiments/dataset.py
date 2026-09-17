"""
dataset.py — Carregador e Pré-processador de Dataset de Benchmark (Seção 5.2 do TCC).

Provedor de dados robusto e ágil para experimentos de Classificação de Texto.
Garante carregamento imediato, suporte a modo rápido (quick_run) e pré-processamento
com TF-IDF para modelos clássicos de Machine Learning.
"""

import pandas as pd
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

from .config import config


def load_benchmark_dataset(
    quick_run: bool = False, n_samples: int | None = None, random_state: int = 42
) -> tuple[list, list, list, list]:
    """
    Carrega o dataset de benchmark de classificação de texto.

    Retorna:
        (X_train, X_test, y_train, y_test) como listas de strings e inteiros.
    """
    try:
        # Tenta carregar dataset binário do 20 Newsgroups (Rec.Autos vs Sci.Med)
        # Excelente substituto rápido, estável e embutido no Scikit-Learn
        categories = ["rec.autos", "sci.med"]
        dataset = fetch_20newsgroups(
            subset="all",
            categories=categories,
            remove=("headers", "footers", "quotes"),
            random_state=random_state,
        )
        data_text = dataset.data
        labels = dataset.target
    except Exception:
        # Fallback sintético em caso de ausência de conexão com internet
        data_text = [
            "Great automotive engine performance and high speed vehicle driving.",
            "Medical research study on clinical health and treatment outcome.",
            "Fast sports car with turbocharged horsepower and smooth handling.",
            "Doctor prescribed medicine for patient recovery and hospital care.",
        ] * 250
        labels = [0, 1, 0, 1] * 250

    # Trata limitação de amostras para testes ultra-rápidos
    if quick_run and n_samples is None:
        n_samples = 500

    if n_samples is not None and n_samples < len(data_text):
        df = pd.DataFrame({"text": data_text, "label": labels})
        df_sampled = df.sample(n=n_samples, random_state=random_state)
        data_text = df_sampled["text"].tolist()
        labels = df_sampled["label"].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        data_text,
        labels,
        test_size=config.TEST_SIZE,
        random_state=random_state,
        stratify=labels if len(set(labels)) > 1 else None,
    )

    return X_train, X_test, y_train, y_test


def get_tfidf_features(
    X_train: list, X_test: list, max_features: int = config.MAX_TFIDF_FEATURES
) -> tuple[object, object, TfidfVectorizer]:
    """
    Converte os textos brutos em matriz esparsa TF-IDF para modelos clássicos.

    Retorna:
        (X_train_tfidf, X_test_tfidf, vectorizer)
    """
    vectorizer = TfidfVectorizer(
        max_features=max_features, stop_words="english", sublinear_tf=True
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    return X_train_tfidf, X_test_tfidf, vectorizer
