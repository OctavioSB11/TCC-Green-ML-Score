"""Qualidade × custo: fronteira de Pareto e custo marginal (tarefa T3)."""

from __future__ import annotations

import streamlit as st

from app.core import charts, data, state, theme

dataset = state.selected_dataset()
label = data.dataset_label(dataset)
summary = state.summary(dataset)

st.title(f"Qualidade × custo: {label}")
st.markdown(
    "Cada modelo aparece pela mediana da energia e pela média do F1-Score das dez "
    "sementes; os pontos claros são as sementes. Um modelo é **dominado** quando outro "
    "tem F1-Score maior ou igual com energia menor ou igual. A linha pontilhada liga os "
    "modelos que ficam na **fronteira de Pareto**. Passe o mouse sobre um modelo para "
    "ver quanto ele custa em relação à Regressão Logística."
)

show_seeds = st.toggle("Mostrar as dez sementes", value=True)
st.plotly_chart(
    charts.pareto_chart(summary, state.seeds(dataset) if show_seeds else None),
    width="stretch",
)

front = [data.model_label(m) for m in summary.index[summary.pareto]]
dominated = [data.model_label(m) for m in summary.index[~summary.pareto]]
c1, c2 = st.columns(2)
c1.success("Na fronteira: " + ", ".join(front))
if dominated:
    c2.error("Dominados: " + ", ".join(dominated))

st.subheader("Custo em relação à Regressão Logística")
st.caption(
    "Razão de energia e ΔF1 são medianas por semente. O custo marginal é a mediana, "
    "entre as sementes em que o modelo supera a referência, da energia extra dividida "
    "pelo ganho de F1."
)
rel = state.relative(dataset)
st.dataframe(
    theme.br_table(
        rel.drop(index=data.model_label(data.REFERENCE_MODEL), errors="ignore"),
        {
            "E/E_RL (mediana)": ("E/E_RL (mediana)", 1),
            "ΔF1 (pontos, mediana)": ("ΔF1 (pontos, mediana)", "+1"),
            "Custo marginal (J por ponto de F1)": (
                "Custo marginal (J por ponto de F1)",
                2,
            ),
            "Sementes em que é dominado": ("Sementes em que é dominado", "pct"),
            "Na fronteira de Pareto": ("Na fronteira de Pareto", "bool"),
        },
    ).replace({True: "Sim", False: "Não"}),
    width="stretch",
)

st.subheader("O que cada critério escolheria")
contexts = state.contexts_table()
context_name = st.selectbox(
    "Contexto para carbono e água",
    contexts.contexto.tolist(),
    index=contexts.contexto.tolist().index(data.REFERENCE_CONTEXT),
    key="qc_contexto",
)
decision = state.decision(dataset, context_name).copy()
decision["modelo"] = decision.modelo.map(data.model_label)
st.dataframe(
    theme.br_table(
        decision,
        {
            "criterio": ("Critério", "texto"),
            "modelo": ("Modelo escolhido", "texto"),
            "f1": ("F1-Score", 3),
            "energia_mwh": ("Energia (mWh, mediana)", 3),
            "carbono_mg": ("Carbono (mg CO₂e)", 3),
            "agua_ul": ("Água (µL)", 1),
        },
    ),
    hide_index=True,
    width="stretch",
)

st.subheader("Comparar dois modelos")
models = list(summary.index)
left, right = st.columns(2)
base = left.selectbox(
    "Modelo de partida",
    models,
    index=models.index(data.REFERENCE_MODEL),
    format_func=data.model_label,
)
alt_options = [m for m in models if m != base]
# Começa pelo modelo de menor custo marginal frente à referência, o caso mais
# interessante de comparar (no Covertype, o XGBoost).
costs = summary.loc[alt_options].get("marginal_cost_j")
default_alt = (
    costs.idxmin() if costs is not None and costs.notna().any() else alt_options[0]
)
alternative = right.selectbox(
    "Trocar por",
    alt_options,
    index=alt_options.index(default_alt),
    format_func=data.model_label,
)
cmp = data.compare_models(summary, base, alternative, data.get_context(context_name))
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Ganho de F1", f"{theme.fmt(cmp['delta_f1_points'], 1)} pontos")
m2.metric("Energia", f"{theme.fmt(cmp['energy_ratio'], 1)} vezes")
m3.metric("Energia extra por treino", theme.fmt_auto(cmp["extra_energy_j"], "J"))
m4.metric(
    "Custo marginal (J/ponto)",
    (
        theme.fmt(cmp["marginal_cost_j"], 2)
        if cmp["marginal_cost_j"] is not None
        else "n.a."
    ),
    help="Energia extra por treinamento dividida pelo ganho de F1. Não se aplica (n.a.) "
    "quando a troca não melhora o F1-Score.",
)
m5.metric(
    f"Carbono extra ({context_name})", theme.fmt_auto(cmp["extra_carbon_mg"], "mg")
)

name_b, name_a = data.model_label(alternative), data.model_label(base)
if cmp["delta_f1_points"] > 0 and cmp["extra_energy_j"] > 0:
    st.info(
        f"Trocar {name_a} por {name_b} melhora o F1-Score em "
        f"{theme.fmt(cmp['delta_f1_points'], 1)} pontos ao custo de "
        f"{theme.fmt_auto(cmp['extra_energy_j'])} J por treinamento "
        f"({theme.fmt(cmp['marginal_cost_j'], 2)} J por ponto)."
    )
elif cmp["delta_f1_points"] > 0:
    st.success(f"{name_b} é mais preciso e também mais econômico que {name_a}.")
elif cmp["extra_energy_j"] > 0:
    st.error(f"{name_b} é menos preciso e mais caro que {name_a}: não compensa.")
else:
    st.warning(
        f"{name_b} economiza energia, mas perde "
        f"{theme.fmt(-cmp['delta_f1_points'], 1)} pontos de F1 em relação a {name_a}."
    )
st.caption(
    "Comparação pelas medianas de energia e pelas médias de F1; por isso a razão de "
    "energia pode diferir um pouco da mediana por semente mostrada na tabela acima."
)
