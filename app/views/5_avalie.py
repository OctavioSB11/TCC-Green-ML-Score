"""Avalie seu modelo: envio de um CSV com resultados próprios e cálculo do GMS (tarefa T6)."""

from __future__ import annotations

import streamlit as st

from app.core import charts, data, state, theme, upload

SOURCE_KEY = "av_fonte"
EXAMPLE = "Dados de exemplo"
OWN = "Enviar meu CSV"

dataset = state.selected_dataset()

st.title("Avalie seu modelo")
st.markdown(
    "Envie um CSV com uma linha por treinamento (modelo, F1-Score e energia) e veja, "
    "com as mesmas fórmulas do estudo, o GMS de cada modelo em cada região, a "
    "fronteira de Pareto, o custo frente a um modelo de referência e a leitura da "
    "regra D4 da hipótese H2."
)
st.info(
    "Os resultados dependem de como a energia foi medida. O estudo usou o CodeCarbon "
    "em modo machine (máquina inteira); comparar com os modelos do estudo só faz "
    "sentido se a sua medição seguir o mesmo método, de preferência no mesmo tipo "
    "de máquina.",
    icon=":material/info:",
)

# ---- 1. dados
st.subheader("1. Dados")
source = st.segmented_control(
    "Origem dos dados", [EXAMPLE, OWN], default=EXAMPLE, key=SOURCE_KEY
)
template = state.example_csv(dataset)
label = data.dataset_label(dataset)
c_up, c_help = st.columns([3, 2])
with c_help:
    st.markdown(
        "**Formato do arquivo**\n"
        "- `modelo`: nome do modelo\n"
        "- `f1`: F1-Score entre 0 e 1\n"
        "- `energia`: energia de um treinamento (kWh, Wh ou J)\n"
        "- `semente`: opcional\n\n"
        "Separador `;` ou `,`; vírgula ou ponto decimal."
    )
    st.download_button(
        "Baixar CSV modelo",
        template,
        file_name=f"greenml_exemplo_{dataset}.csv",
        mime="text/csv",
        width="stretch",
        help=f"Resultados do {label} do estudo (uma linha por modelo e semente, "
        "energia em kWh), no formato aceito pela página.",
    )
with c_up:
    if source == OWN:
        file = st.file_uploader("Arquivo CSV", type=["csv", "txt"])
        unit = st.radio(
            "Unidade da coluna de energia",
            list(upload.UNITS),
            horizontal=True,
            help="Se o nome da coluna já indicar a unidade (energia_kwh ou energia_j), "
            "ela prevalece sobre esta escolha.",
        )
        if file is None:
            st.caption("Envie um arquivo para continuar.")
            st.stop()
        raw = file.getvalue()
    else:
        st.write(
            f"Usando os resultados do {label} do estudo, o conjunto escolhido na "
            "barra lateral. Com eles, a página reproduz os números do painel e do "
            "artigo; para avaliar os seus, escolha Enviar meu CSV."
        )
        raw, unit = template, "kWh"

try:
    loaded = state.uploaded(raw, unit)
except upload.UploadError as exc:
    st.error(f"**Não foi possível usar o arquivo.** {exc}", icon=":material/error:")
    st.stop()
for note in loaded.notes:
    st.caption(note)
st.caption(
    f"{len(loaded.runs)} treinamentos de {len(loaded.models)} modelo(s) lidos; "
    f"energia em {loaded.unit}."
)

# ---- 2. escolhas
st.subheader("2. Referência, região e pesos")
models = loaded.models
c1, c2, c3 = st.columns(3)
reference = c1.selectbox(
    "Modelo de referência",
    models,
    index=models.index(upload.default_reference(loaded.runs)),
    format_func=data.model_label,
    help="Padrão: o de menor energia mediana, como a Regressão Logística no estudo.",
)
contexts = state.contexts_table().contexto.tolist()
context_name = c2.selectbox(
    "Região de execução",
    contexts,
    index=contexts.index(data.REFERENCE_CONTEXT),
    key="av_regiao",
)
profile = c3.selectbox("Perfil de pesos do GMS", list(data.PROFILES), key="av_perfil")
weights = data.make_weights(*data.PROFILES[profile])

ev = state.upload_evaluation(
    raw, unit, reference, context_name, (weights.w_E, weights.w_C, weights.w_W)
)
s = ev.summary
ref_label = data.model_label(reference)

# ---- 3. resultado
st.subheader("3. Resultado")
best = s.gms.idxmax()
front = [data.model_label(m) for m in s.index[s.pareto]]
others = s.drop(index=reference)
contrary = others.index[others.h2 == "Contraria H2"]
k1, k2, k3, k4 = st.columns(4)
k1.markdown(
    theme.kpi_html(
        "Modelos avaliados",
        str(len(s)),
        f"{len(loaded.runs)} treinamentos · referência: {ref_label}",
    ),
    unsafe_allow_html=True,
)
k2.markdown(
    theme.kpi_html(
        f"Maior GMS em {context_name}",
        data.model_label(best),
        f"GMS {theme.fmt(s.gms[best], 1)} · {s.rank_context[best]}º de "
        f"{len(ev.configurations)} configurações",
    ),
    unsafe_allow_html=True,
)
k3.markdown(
    theme.kpi_html(
        "Fronteira de Pareto",
        f"{len(front)} de {len(s)}",
        ", ".join(front),
    ),
    unsafe_allow_html=True,
)
k4.markdown(
    theme.kpi_html(
        "Regra D4 (H2)",
        "Contrariada" if len(contrary) else "Compatível",
        (
            "por " + ", ".join(data.model_label(m) for m in contrary)
            if len(contrary)
            else f"nenhum modelo na fronteira com menos de 10 vezes a energia de {ref_label}"
        ),
    ),
    unsafe_allow_html=True,
)
st.write("")

costs = others.marginal_cost_j.dropna()
if not costs.empty:
    cheapest = costs.idxmin()
    st.success(
        f"Entre os modelos mais precisos que {ref_label}, o de menor custo marginal é "
        f"{data.model_label(cheapest)}: {theme.fmt(costs[cheapest], 2)} J por ponto de "
        f"F1, com {theme.fmt(s.energy_ratio_ref[cheapest], 1)} vezes a energia e "
        f"{theme.fmt(s.delta_f1_points[cheapest], 1)} pontos a mais de F1.",
        icon=":material/bolt:",
    )
elif len(others):
    st.warning(
        f"Nenhum modelo supera o F1-Score de {ref_label}: o custo marginal não se aplica.",
        icon=":material/warning:",
    )

st.markdown("**Qualidade × custo**")
t1, t2 = st.columns(2)
show_seeds = t1.toggle("Mostrar cada treinamento", value=True, key="av_sementes")
compare = t2.toggle(
    f"Comparar com os modelos do estudo ({label})",
    value=False,
    key="av_estudo",
    disabled=source != OWN,
    help="Disponível ao enviar um CSV próprio; o conjunto de dados do estudo é o "
    "escolhido na barra lateral.",
)
fig = charts.pareto_chart(
    s,
    upload.seed_points(loaded.runs) if show_seeds else None,
    reference=reference,
    reference_short="ref",
)
if compare:
    charts.add_study_points(fig, state.summary(dataset), dataset)
st.plotly_chart(fig, width="stretch")
st.caption(
    "Energia mediana e F1 médio de cada modelo; a linha pontilhada liga os modelos da "
    "fronteira de Pareto. Razão de energia e custo marginal usam essas medianas e "
    "médias, por isso podem diferir um pouco das medianas por semente da Tabela 3 do "
    "artigo."
)

st.markdown(f"**Ranking em {context_name}**")
table = s.assign(modelo=[data.model_label(m) for m in s.index]).sort_values(
    "gms", ascending=False
)
table["fronteira"] = table.pareto.map({True: "Sim", False: "Não"})
st.dataframe(
    theme.br_table(
        table,
        {
            "modelo": ("Modelo", "texto"),
            "n_seeds": ("Treinos", "int"),
            "f1_mean": ("F1-Score", 3),
            "energy_mwh_median": ("Energia (mWh)", 3),
            "carbon_mg": ("Carbono (mg)", 3),
            "water_ul": ("Água (µL)", 1),
            "gms": ("GMS", 1),
            "rank_context": (f"Posição (de {len(ev.configurations)})", "int"),
            "energy_ratio_ref": ("E/E_ref", 1),
            "delta_f1_points": ("ΔF1 (pontos)", "+1"),
            "marginal_cost_j": ("J por ponto de F1", 2),
            "fronteira": ("Na fronteira", "texto"),
            "h2": ("Regra D4 (H2)", "texto"),
        },
    ),
    hide_index=True,
    width="stretch",
)
st.caption(
    "Energia mediana por treinamento; carbono em mg CO₂e; posição entre todas as "
    "configurações modelo × região; J por ponto de F1 é o custo marginal frente à "
    "referência. Regra D4: um modelo dominado é compatível com H2; um modelo na fronteira só é "
    "compatível se gastar pelo menos 10 vezes a energia da referência (uma ordem de "
    "grandeza). Carbono e água usam os fatores da região escolhida."
)

st.markdown("**Posição no simulador de contexto**")
best_cfg = ev.configurations.iloc[0]
st.write(
    f"Com o perfil {profile.lower()}, a melhor configuração é "
    f"{data.model_label(best_cfg.model)} em {best_cfg.context} "
    f"(GMS {theme.fmt(best_cfg.gms, 1)}). "
    + (
        "Não há pares"
        if ev.inversions.empty
        else f"Há {len(ev.inversions)} "
        + ("par" if len(ev.inversions) == 1 else "pares")
    )
    + " em que um modelo mais caro supera um mais econômico por estar numa região "
    "melhor."
)
st.plotly_chart(
    charts.gms_heatmap(ev.configurations, list(ev.k.index)), width="stretch"
)
st.caption("Regiões ordenadas do menor para o maior fator k. ★ marca a vencedora.")

st.download_button(
    "Baixar o resultado (CSV)",
    upload.result_csv(ev, weights),
    file_name=f"greenml_resultado_{context_name}.csv",
    mime="text/csv",
    icon=":material/download:",
)
