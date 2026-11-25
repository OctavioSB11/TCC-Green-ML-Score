"""
state.py: cache do Streamlit e estado compartilhado entre as páginas.

Envolve as funções puras de ``data.py`` com ``st.cache_data`` para que trocar de página
ou mexer nos controles não releia os CSVs.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.core import data

DATASET_KEY = "dataset"


@st.cache_data(show_spinner=False)
def datasets() -> list[str]:
    return data.available_datasets()


@st.cache_data(show_spinner=False)
def summary(dataset: str, context_name: str = data.REFERENCE_CONTEXT) -> pd.DataFrame:
    return data.model_summary(dataset, data.get_context(context_name))


@st.cache_data(show_spinner=False)
def runs(dataset: str) -> pd.DataFrame:
    return data.load_runs(dataset)


@st.cache_data(show_spinner=False)
def contexts_table() -> pd.DataFrame:
    return data.contexts_table()


@st.cache_data(show_spinner=False)
def decision(dataset: str, context_name: str = data.REFERENCE_CONTEXT) -> pd.DataFrame:
    return data.decision_table(dataset, data.get_context(context_name))


def selected_dataset() -> str:
    """Dataset escolhido na barra lateral (padrão: o primeiro disponível)."""
    options = datasets()
    if (
        DATASET_KEY not in st.session_state
        or st.session_state[DATASET_KEY] not in options
    ):
        st.session_state[DATASET_KEY] = options[0]
    return st.session_state[DATASET_KEY]


def dataset_selector() -> str:
    """Seletor de dataset na barra lateral, compartilhado por todas as páginas."""
    options = datasets()
    selected_dataset()
    return st.sidebar.selectbox(
        "Conjunto de dados",
        options,
        format_func=data.dataset_label,
        key=DATASET_KEY,
        help="20 Newsgroups é o estudo de caso principal; os outros dois são a verificação de robustez.",
    )


@st.cache_data(show_spinner=False)
def seeds(dataset: str) -> pd.DataFrame:
    return data.seed_points(dataset)


@st.cache_data(show_spinner=False)
def relative(dataset: str) -> pd.DataFrame:
    return data.relative_table(data.model_summary(dataset))


@st.cache_data(show_spinner=False)
def simulation(dataset: str, weights: tuple[float, float, float]) -> dict:
    return data.simulate(dataset, data.make_weights(*weights))


@st.cache_data(show_spinner=False)
def card(dataset: str, model: str, context_name: str, profile: str):
    from app.core import card as card_module

    return card_module.build_card(dataset, model, context_name, profile)


@st.cache_data(show_spinner=False)
def example_csv(dataset: str) -> bytes:
    from app.core import upload

    return upload.example_csv(dataset)


@st.cache_data(show_spinner=False, max_entries=20)
def uploaded(raw: bytes, unit: str):
    from app.core import upload

    return upload.read_upload(raw, unit)


@st.cache_data(show_spinner=False, max_entries=50)
def upload_evaluation(
    raw: bytes,
    unit: str,
    reference: str,
    context_name: str,
    weights: tuple[float, float, float],
):
    from app.core import upload

    runs = upload.read_upload(raw, unit).runs
    return upload.evaluate(runs, reference, context_name, data.make_weights(*weights))
