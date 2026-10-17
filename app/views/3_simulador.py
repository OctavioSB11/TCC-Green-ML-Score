"""Simulador de contexto: pesos, mapa das regiões e GMS ao vivo (tarefa T4)."""

from __future__ import annotations

import streamlit as st

from app.core import charts, data, state, theme

PROFILE_KEY = "sim_perfil"
SLIDER_KEYS = ("sim_we", "sim_wc", "sim_ww")
CUSTOM = "Personalizado"


def _set_sliders(weights: tuple[float, float, float]) -> None:
    total = sum(weights)
    for key, w in zip(SLIDER_KEYS, weights):
        st.session_state[key] = int(round(100 * w / total))


def _apply_profile() -> None:
    name = st.session_state.get(PROFILE_KEY)
    if name in data.PROFILES:
        _set_sliders(data.PROFILES[name])


def _mark_custom() -> None:
    st.session_state[PROFILE_KEY] = CUSTOM


if PROFILE_KEY not in st.session_state:
    st.session_state[PROFILE_KEY] = "Pesos iguais"
if any(key not in st.session_state for key in SLIDER_KEYS):
    _set_sliders(data.PROFILES["Pesos iguais"])

dataset = state.selected_dataset()
label = data.dataset_label(dataset)

st.title(f"Simulador de contexto: {label}")
st.markdown(
    "Escolha quanto pesa cada dimensão no GMS e veja, ao vivo, como as 28 "
    "configurações (4 modelos em 7 regiões) se reorganizam. O GMS de cada "
    "configuração é 1 − E·k: a energia do modelo vezes o fator k da região."
)

st.segmented_control(
    "Perfil de pesos",
    [*data.PROFILES, CUSTOM],
    key=PROFILE_KEY,
    on_change=_apply_profile,
)
c_e, c_c, c_w = st.columns(3)
c_e.slider("Energia", 0, 100, key=SLIDER_KEYS[0], on_change=_mark_custom)
c_c.slider("Carbono", 0, 100, key=SLIDER_KEYS[1], on_change=_mark_custom)
c_w.slider("Água", 0, 100, key=SLIDER_KEYS[2], on_change=_mark_custom)

raw = tuple(float(st.session_state[k]) for k in SLIDER_KEYS)
if sum(raw) == 0:
    st.error("Pelo menos um peso precisa ser maior que zero.")
    st.stop()
weights = data.make_weights(*raw)
st.caption(
    f"Pesos normalizados para somar 1: energia {theme.fmt(weights.w_E, 2)} · "
    f"carbono {theme.fmt(weights.w_C, 2)} · água {theme.fmt(weights.w_W, 2)}"
)

sim = state.simulation(dataset, (weights.w_E, weights.w_C, weights.w_W))
best, base = sim["best"], sim["baseline"]

# ---- avisos
ref_inv = sim["reference_inversions"]
if not ref_inv.empty:
    top = ref_inv.iloc[0]
    st.warning(
        f"**O contexto mudou a escolha do modelo.** Com estes pesos, "
        f"{data.model_label(top.vencedor)} em {top.contexto_vencedor} "
        f"({theme.fmt(top.gms_vencedor, 1)}) supera {data.model_label(top.superado)} em "
        f"{top.contexto_superado} ({theme.fmt(top.gms_superado, 1)}), apesar de gastar "
        "mais energia. Há "
        f"{len(ref_inv)} {'par' if len(ref_inv) == 1 else 'pares'} assim contra a "
        "Regressão Logística.",
        icon=":material/swap_horiz:",
    )
elif len(sim["inversions"]):
    st.info(
        f"Há {len(sim['inversions'])} pares em que um modelo mais caro supera um mais "
        "econômico, mas nenhum deles passa à frente da Regressão Logística.",
        icon=":material/info:",
    )
else:
    st.success(
        "Nenhuma inversão: o GMS ordena os modelos exatamente como a energia.",
        icon=":material/check_circle:",
    )
if (best.model, best.context) != (base["best"].model, base["best"].context):
    st.info(
        f"A configuração vencedora mudou de {data.model_label(base['best'].model)} em "
        f"{base['best'].context} (pesos iguais) para {data.model_label(best.model)} em "
        f"{best.context}.",
        icon=":material/emoji_events:",
    )

# ---- indicadores
k1, k2, k3, k4 = st.columns(4)
k1.markdown(
    theme.kpi_html(
        "Configuração vencedora",
        data.model_label(best.model),
        f"em {best.context} · GMS {theme.fmt(best.gms, 1)}",
    ),
    unsafe_allow_html=True,
)
k2.markdown(
    theme.kpi_html(
        "Região mais favorável",
        sim["k"].index[0],
        f"pior: {sim['k'].index[-1]} ({theme.fmt(sim['k'].iloc[-1] / sim['k'].iloc[0], 1)} vezes o k)",
    ),
    unsafe_allow_html=True,
)
k3.markdown(
    theme.kpi_html(
        "τ_b frente à energia",
        theme.fmt(sim["tau"], 3),
        f"pesos iguais: {theme.fmt(base['tau'], 3)} · patamar sem inversão: "
        f"{theme.fmt(sim['tau_plateau'], 3)}",
    ),
    unsafe_allow_html=True,
)
k4.markdown(
    theme.kpi_html(
        "Pares invertidos entre modelos",
        str(len(sim["inversions"])),
        f"pesos iguais: {base['inversions']}",
    ),
    unsafe_allow_html=True,
)
st.write("")

# ---- mapa e mapa de calor
st.subheader("Regiões no mapa")
models = list(data.MODEL_ORDER)
map_model = st.selectbox(
    "GMS mostrado no mapa",
    models,
    index=models.index(ref_inv.iloc[0].vencedor) if not ref_inv.empty else 0,
    format_func=data.model_label,
)
st.plotly_chart(
    charts.context_map(data.map_table(sim, map_model), data.model_label(map_model)),
    width="stretch",
    config=charts.MAP_CONFIG,
)
st.caption(
    "Cor: fator k da região em relação ao da melhor região (1 = melhor; verde é mais "
    "limpo). A estrela marca a região de menor k, onde qualquer modelo tem seu maior GMS. O mapa de fundo é baixado do Plotly e "
    "precisa de internet; os pontos aparecem mesmo sem conexão."
)

st.subheader("GMS de cada modelo em cada região")
st.plotly_chart(
    charts.gms_heatmap(sim["configurations"], list(sim["k"].index)), width="stretch"
)
st.caption("Regiões ordenadas do menor para o maior fator k. ★ marca a vencedora.")

tab_rank, tab_inv, tab_simplex, tab_ctx = st.tabs(
    [
        "Ranking das configurações",
        "Pares invertidos",
        "Mapa de pesos",
        "Fatores das regiões",
    ]
)
with tab_rank:
    cfg = sim["configurations"].copy()
    cfg["posicao"] = range(1, len(cfg) + 1)
    cfg["modelo"] = cfg.model.map(data.model_label)
    cfg["energia_mwh"] = cfg.energy_kwh * data.KWH_TO_MWH
    cfg["carbono_mg"] = cfg.carbon_kg * 1e6
    cfg["agua_ul"] = cfg.water_l * 1e6
    cfg["k_rel"] = cfg.k / cfg.k.min()
    st.dataframe(
        theme.br_table(
            cfg,
            {
                "posicao": ("Posição", "int"),
                "modelo": ("Modelo", "texto"),
                "context": ("Região", "texto"),
                "gms": ("GMS", 1),
                "energia_mwh": ("Energia (mWh)", 3),
                "carbono_mg": ("Carbono (mg CO₂e)", 3),
                "agua_ul": ("Água (µL)", 1),
                "k_rel": ("k relativo ao melhor", 2),
            },
        ),
        hide_index=True,
        width="stretch",
        height=420,
    )
with tab_inv:
    inv = sim["inversions"].sort_values(
        ["gms_vencedor", "gms_superado"], ascending=[False, True]
    )
    if inv.empty:
        st.write("Nenhum par invertido com estes pesos.")
    else:
        st.write(
            "Pares em que o modelo da esquerda gasta mais energia, mas tem GMS maior "
            "por estar numa região melhor (condição E_j/E_i < k_r/k_s)."
        )
        inv = inv.assign(
            vencedor=inv.vencedor.map(data.model_label),
            superado=inv.superado.map(data.model_label),
        )
        st.dataframe(
            theme.br_table(
                inv,
                {
                    "vencedor": ("Modelo mais caro", "texto"),
                    "contexto_vencedor": ("Região", "texto"),
                    "gms_vencedor": ("GMS", 1),
                    "superado": ("Supera o modelo mais econômico", "texto"),
                    "contexto_superado": ("Região ", "texto"),
                    "gms_superado": ("GMS ", 1),
                },
            ),
            hide_index=True,
            width="stretch",
        )
with tab_simplex:
    st.write(
        "Cada hexágono é uma combinação de pesos (passo de 0,05, como na Figura 5 do "
        "artigo); a estrela preta marca os pesos atuais. No vértice de energia pura "
        "todas as regiões empatam, e a indicada é só a primeira da lista."
    )
    color_by = st.radio(
        "Colorir por",
        ["vencedor", "tau"],
        format_func={
            "vencedor": "Configuração vencedora",
            "tau": "τ_b frente à energia",
        }.get,
        horizontal=True,
    )
    st.plotly_chart(
        charts.simplex_chart(sim["sensitivity"], weights, color_by), width="stretch"
    )
with tab_ctx:
    table = data.map_table(sim, map_model)
    st.dataframe(
        theme.br_table(
            table.sort_values("k"),
            {
                "contexto": ("Região", "texto"),
                "tipo": ("Tipo", "texto"),
                "carbono_efetivo_g_kwh": ("Carbono por kWh de TI (g)", 1),
                "agua_efetiva_l_kwh": ("Água por kWh de TI (L)", 2),
                "k_rel": ("k relativo ao melhor", 2),
                "fonte": ("Fontes", "texto"),
            },
        ),
        hide_index=True,
        width="stretch",
    )
