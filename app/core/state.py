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


@st.cache_data(show_spinner=False)
def profiles(dataset: str) -> pd.DataFrame:
    return data.profile_summary(dataset)


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
