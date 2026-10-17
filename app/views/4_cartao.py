"""Cartão ambiental: ficha de um modelo em uma região, com downloads (tarefa T5)."""

from __future__ import annotations

import streamlit as st

from app.core import card, data, state, theme

dataset = state.selected_dataset()
label = data.dataset_label(dataset)
summary = state.summary(dataset)

st.title(f"Cartão ambiental: {label}")
st.markdown(
    "Escolha o modelo, a região de execução e o perfil de pesos. O cartão reúne "
    "desempenho, custo ambiental por treinamento, posição no GMS e as fontes dos "
    "fatores, e pode ser baixado em PNG, Markdown ou CSV."
)

models = list(summary.index)
costs = summary.drop(index=data.REFERENCE_MODEL, errors="ignore").get("marginal_cost_j")
default_model = (
    costs.idxmin() if costs is not None and costs.notna().any() else models[0]
)
contexts = state.contexts_table().contexto.tolist()
c1, c2, c3 = st.columns(3)
model = c1.selectbox(
    "Modelo", models, index=models.index(default_model), format_func=data.model_label
)
context_name = c2.selectbox(
    "Região de execução", contexts, index=contexts.index(data.REFERENCE_CONTEXT)
)
profile = c3.selectbox("Perfil de pesos do GMS", list(data.PROFILES))

c = state.card(dataset, model, context_name, profile)
color = theme.MODEL_COLORS.get(model, theme.GREEN)

# ---- cabeçalho do cartão
badges = []
if c.is_reference:
    badges.append("Referência")
badges.append("Fronteira de Pareto" if c.pareto else "Dominado")
st.markdown(
    f"<div style='background:{theme.GREEN};color:white;border-radius:12px;"
    f"padding:16px 22px;margin:8px 0 14px 0;border-left:12px solid {color}'>"
    f"<div style='font-size:1.6rem;font-weight:700'>{data.model_label(model)} em "
    f"{context_name}</div>"
    f"<div style='font-size:1rem;opacity:0.9'>{label} · {c.context_kind} · "
    f"{profile} · {' · '.join(badges)}</div></div>",
    unsafe_allow_html=True,
)

k = st.columns(5)
k[0].markdown(
    theme.kpi_html("F1-Score", theme.fmt(c.f1_mean, 3), f"± {theme.fmt(c.f1_std, 3)}"),
    unsafe_allow_html=True,
)
k[1].markdown(
    theme.kpi_html(
        "Energia por treino",
        f"{theme.fmt_auto(c.energy_mwh_median)} mWh",
        f"IQR {theme.fmt_auto(c.energy_mwh_iqr)} mWh",
    ),
    unsafe_allow_html=True,
)
k[2].markdown(
    theme.kpi_html("Carbono por treino", f"{theme.fmt_auto(c.carbon_mg)} mg", "CO₂e"),
    unsafe_allow_html=True,
)
k[3].markdown(
    theme.kpi_html(
        "Água por treino", f"{theme.fmt_auto(c.water_ul)} µL", "local e geração"
    ),
    unsafe_allow_html=True,
)
k[4].markdown(
    theme.kpi_html(
        "GMS nesta região",
        theme.fmt(c.gms_context, 1),
        f"{c.rank_context}º de {c.n_configurations} configurações",
    ),
    unsafe_allow_html=True,
)
st.write("")

left, right = st.columns(2)
with left.container(border=True):
    st.markdown("**Comparação com a Regressão Logística**")
    if c.is_reference:
        st.write("Este é o modelo de referência do estudo.")
    else:
        st.markdown(
            f"- Energia: **{theme.fmt(c.energy_ratio_ref, 1)} vezes** a da RL\n"
            f"- ΔF1: **{'+' if (c.delta_f1_points or 0) > 0 else ''}"
            f"{theme.fmt(c.delta_f1_points, 1)} pontos**\n"
            f"- Custo marginal: **"
            + (
                f"{theme.fmt(c.marginal_cost_j, 2)} J por ponto de F1"
                if c.marginal_cost_j is not None
                else "não se aplica (não supera a RL)"
            )
            + f"**\n- Dominado em **{theme.fmt_pct(c.dominated_share or 0.0)}** das sementes"
        )
    st.markdown(
        f"GMS de contexto único (mesmos fatores para todos): **{theme.fmt(c.gms_single, 1)}**"
    )
with right.container(border=True):
    st.markdown("**Equivalência e procedência**")
    st.markdown(
        f"- Uma carga de smartphone (0,019 kWh, EPA) equivale a "
        f"**{theme.fmt(c.trainings_per_charge, 0)} treinamentos** deste modelo.\n"
        f"- Medição: CodeCarbon, modo {', '.join(c.tracking_modes)} (máquina inteira); "
        f"RAM com {theme.fmt_pct(c.ram_share_median or 0.0)} da energia; potência "
        f"ociosa {theme.fmt_auto(c.idle_power_w or 0.0)} W.\n"
        "- Validação pela bateria: a ordem entre modelos é confiável; os valores "
        "absolutos de energia, não."
    )

st.subheader("Projeção anual")
per_day = st.number_input(
    "Treinamentos por dia", min_value=1, max_value=1_000_000, value=100, step=10
)
proj = card.annual_projection(c, per_day)
p1, p2, p3 = st.columns(3)
p1.markdown(
    theme.kpi_html("Energia em um ano", f"{theme.fmt_auto(proj['energia_kwh'])} kWh"),
    unsafe_allow_html=True,
)
p2.markdown(
    theme.kpi_html(
        "Carbono em um ano", f"{theme.fmt_auto(proj['carbono_kg'])} kg CO₂e"
    ),
    unsafe_allow_html=True,
)
p3.markdown(
    theme.kpi_html("Água em um ano", f"{theme.fmt_auto(proj['agua_l'])} L"),
    unsafe_allow_html=True,
)
st.caption(
    "Projeção linear a partir da energia mediana por treinamento; herda a limitação da "
    "medição (valores absolutos indicativos)."
)

with st.expander("Fontes dos fatores"):
    for source in c.sources:
        st.markdown(f"- {source}")
    st.markdown(f"- {card.SMARTPHONE_SOURCE}")

st.subheader("Baixar o cartão")
base_name = f"cartao_{dataset}_{model}_{context_name}"
png = card.to_png(c)
d1, d2, d3 = st.columns(3)
d1.download_button(
    "PNG (imagem)", png, file_name=f"{base_name}.png", mime="image/png", width="stretch"
)
d2.download_button(
    "Markdown",
    card.to_markdown(c).encode("utf-8"),
    file_name=f"{base_name}.md",
    mime="text/markdown",
    width="stretch",
)
d3.download_button(
    "CSV (Excel)",
    card.to_csv(c),
    file_name=f"{base_name}.csv",
    mime="text/csv",
    width="stretch",
)
with st.expander("Pré-visualizar o PNG"):
    st.image(png, width="stretch")
