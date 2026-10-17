"""Visão geral: desempenho, energia, carbono, água e rankings por modelo (tarefa T2)."""

from __future__ import annotations

import streamlit as st

from app.core import charts, data, state, theme


def _value(label_text: str, value: str, spread: str | None = None) -> str:
    """Bloco de métrica compacto: rótulo, valor e, se houver, o desvio padrão."""
    sd = (
        f"<span style='font-size:0.95rem;color:{theme.GREY}'> ± {spread}</span>"
        if spread
        else ""
    )
    return (
        f"<div style='margin:6px 0 10px 0'>"
        f"<div style='font-size:0.9rem;color:{theme.GREY}'>{label_text}</div>"
        f"<div style='font-size:1.7rem;font-weight:600;line-height:1.2'>{value}{sd}</div>"
        f"</div>"
    )


dataset = state.selected_dataset()
label = data.dataset_label(dataset)

st.title(f"Visão geral: {label}")
st.caption(
    "Médias das dez sementes, energia de treinamento por execução. O GMS mostrado aqui "
    "é o de contexto único (mesmos fatores ambientais para todos os modelos)."
)

contexts = state.contexts_table()
context_name = st.selectbox(
    "Contexto usado para calcular carbono e água",
    contexts.contexto.tolist(),
    index=contexts.contexto.tolist().index(data.REFERENCE_CONTEXT),
    help="BR-local é o local real de medição. Mudar o contexto altera carbono e água, "
    "mas não a energia nem o GMS de contexto único.",
)
summary = state.summary(dataset, context_name)

for finding in data.overview_findings(summary):
    st.markdown(f"- {finding}")

st.subheader("Modelos")
columns = st.columns(len(summary))
for col, (model, row) in zip(columns, summary.iterrows()):
    color = theme.MODEL_COLORS.get(model, theme.GREY)
    with col.container(border=True):
        st.markdown(
            f"<div style='border-left:8px solid {color};padding-left:10px;"
            f"font-size:1.25rem;font-weight:700'>{data.model_label(model)}</div>",
            unsafe_allow_html=True,
        )
        if model == data.REFERENCE_MODEL:
            st.badge("Referência", color="gray")
        if row.pareto:
            st.badge("Fronteira de Pareto", color="green")
        elif "dominated_share" in row and row.dominated_share > 0:
            st.badge(f"Dominado: {theme.fmt_pct(row.dominated_share)}", color="red")
        st.markdown(
            _value("F1-Score", theme.fmt(row.f1_mean, 3), theme.fmt(row.f1_std, 3))
            + _value(
                "Energia (mWh)",
                theme.fmt_auto(row.energy_mwh_mean),
                theme.fmt_auto(row.energy_mwh_std),
            )
            + _value("Carbono (mg CO₂e)", theme.fmt_auto(row.carbon_mg))
            + _value("Água (µL)", theme.fmt_auto(row.water_ul))
            + _value(
                "GMS (0 a 100)", theme.fmt(row.gms_mean, 1), theme.fmt(row.gms_std, 1)
            ),
            unsafe_allow_html=True,
        )
if "dominated_share" in summary and (summary.dominated_share > 0).any():
    st.caption(
        "Dominado: fração das sementes em que outro modelo teve F1-Score maior ou "
        "igual com energia menor ou igual."
    )

tab_rank, tab_seeds, tab_bars, tab_table = st.tabs(
    [
        "Rankings por critério",
        "Energia por semente",
        "Comparação de métricas",
        "Tabela completa",
    ]
)
with tab_rank:
    st.markdown(
        "Posição de cada modelo em cada critério. Linhas paralelas indicam critérios "
        "que concordam; cruzamentos mostram onde a escolha muda."
    )
    st.plotly_chart(charts.rank_chart(summary), width="stretch")
    st.dataframe(data.ranking_table(summary), width="stretch")
with tab_seeds:
    st.markdown(
        "Cada ponto é uma semente. A caixa mostra mediana e quartis; a escala é "
        "logarítmica porque os modelos diferem em até duas ordens de grandeza."
    )
    st.plotly_chart(charts.seed_energy_chart(state.runs(dataset)), width="stretch")
with tab_bars:
    left, right = st.columns(2)
    left.plotly_chart(
        charts.metric_bars(
            summary, "f1_mean", "F1-Score (média)", error_column="f1_std"
        ),
        width="stretch",
    )
    right.plotly_chart(
        charts.metric_bars(
            summary, "energy_mwh_mean", "Energia de treino (mWh, escala log)", log=True
        ),
        width="stretch",
    )
    left.plotly_chart(
        charts.metric_bars(
            summary, "carbon_mg", f"Carbono (mg CO₂e) em {context_name}"
        ),
        width="stretch",
    )
    right.plotly_chart(
        charts.metric_bars(summary, "water_ul", f"Água (µL) em {context_name}"),
        width="stretch",
    )
with tab_table:
    table = summary.rename(index=data.model_label)[
        [
            "f1_mean",
            "f1_std",
            "energy_mwh_mean",
            "energy_mwh_std",
            "carbon_mg",
            "water_ul",
            "gms_mean",
            "gms_std",
            "rank_f1",
            "rank_energy",
            "rank_gms",
        ]
    ]
    st.dataframe(
        theme.br_table(
            table,
            {
                "f1_mean": ("F1 (média)", 3),
                "f1_std": ("F1 (desvio)", 3),
                "energy_mwh_mean": ("Energia mWh (média)", 3),
                "energy_mwh_std": ("Energia mWh (desvio)", 3),
                "carbon_mg": ("Carbono (mg CO₂e)", 3),
                "water_ul": ("Água (µL)", 1),
                "gms_mean": ("GMS (média)", 1),
                "gms_std": ("GMS (desvio)", 1),
                "rank_f1": ("Posição F1", "int"),
                "rank_energy": ("Posição energia", "int"),
                "rank_gms": ("Posição GMS", "int"),
            },
        ),
        width="stretch",
    )
    st.download_button(
        "Baixar tabela (CSV)",
        table.to_csv(sep=";", decimal=",").encode("utf-8-sig"),
        file_name=f"visao_geral_{dataset}_{context_name}.csv",
        mime="text/csv",
    )
