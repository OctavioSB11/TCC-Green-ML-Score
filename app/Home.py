"""
Home.py: ponto de entrada do GreenML Dashboard.

Uso, a partir da raiz do repositório:
    streamlit run app/Home.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from app.core import data, state, theme  # noqa: E402

PAGES_DIR = Path(__file__).resolve().parent / "views"


def inicio() -> None:
    """Página inicial: o que é o GMS, de onde vêm os dados e como navegar."""
    st.title("GreenML Dashboard")
    st.markdown(
        "Painel interativo do **GreenML Score (GMS)**, métrica que reúne energia, "
        "emissões de carbono e consumo de água no treinamento de modelos de "
        "aprendizado de máquina. Os números vêm da execução completa do TCC: quatro "
        "modelos, três conjuntos de dados, dez sementes e sete contextos de execução."
    )

    summary = state.summary(state.selected_dataset())
    contexts = state.contexts_table()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Conjuntos de dados", len(state.datasets()))
    c2.metric("Modelos", len(summary))
    c3.metric("Sementes por modelo", int(summary.n_seeds.max()))
    c4.metric("Contextos de execução", len(contexts))

    st.subheader("Como o GMS é calculado")
    st.latex(
        r"GMS = w_E\,E_{norm} + w_C\,C_{norm} + w_W\,W_{norm},\qquad "
        r"X_{norm} = 1 - \frac{X}{X_{max}}"
    )
    st.latex(
        r"C = E \cdot PUE \cdot IC \qquad W = E\,(WUE + PUE \cdot EWIF) "
        r"\qquad GMS_{ir} = 1 - E_i\,k_r"
    )
    st.markdown(
        "Com o mesmo contexto para todos os modelos, o GMS ordena os modelos como a "
        "energia. Com contextos diferentes, um modelo mais caro só passa à frente de "
        "um mais econômico quando a razão entre as energias é menor que a razão entre "
        "os fatores k dos contextos."
    )

    st.subheader("Navegação")
    st.markdown(
        "- **Visão geral**: desempenho, energia, carbono, água e rankings por modelo.\n"
        "- **Qualidade × custo**: fronteira de Pareto e custo marginal por ponto de F1.\n"
        "- **Simulador de contexto**: pesos ajustáveis, mapa das regiões e GMS ao vivo.\n"
        "- **Cartão ambiental**: ficha de um modelo para baixar.\n"
        "- **Avalie seu modelo**: envie seus resultados e compare com os do estudo."
    )

    with st.expander("Fontes dos dados"):
        st.markdown(
            "Resultados: `experiments/results/<dataset>/full/comparative_results.csv`. "
            "Contextos: `experiments/contexts/contexts.csv` (intensidade de carbono da "
            "Ember, 2025; água da geração elétrica de Reig et al., 2020; PUE e WUE das "
            "fichas de sustentabilidade da AWS, 2025). Carbono e água são recalculados "
            "a partir da energia medida e dos fatores de cada contexto; o padrão é o "
            f"contexto {data.REFERENCE_CONTEXT}, local real de medição."
        )
        st.dataframe(
            theme.br_table(
                contexts,
                {
                    "contexto": ("Contexto", "texto"),
                    "tipo": ("Tipo", "texto"),
                    "ic_g_kwh": ("IC (gCO₂e/kWh)", 2),
                    "pue": ("PUE", 2),
                    "wue_l_kwh": ("WUE (L/kWh)", 2),
                    "agua_geracao_l_kwh": ("Água da geração (L/kWh)", 2),
                },
            ),
            hide_index=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="GreenML Dashboard",
        page_icon=":material/eco:",
        layout="wide",
    )
    pages = [
        st.Page(inicio, title="Início", icon=":material/home:", default=True),
        st.Page(
            PAGES_DIR / "1_visao_geral.py",
            title="Visão geral",
            icon=":material/dashboard:",
        ),
        st.Page(
            PAGES_DIR / "2_qualidade_custo.py",
            title="Qualidade × custo",
            icon=":material/scatter_plot:",
        ),
        st.Page(
            PAGES_DIR / "3_simulador.py",
            title="Simulador de contexto",
            icon=":material/public:",
        ),
        st.Page(
            PAGES_DIR / "4_cartao.py", title="Cartão ambiental", icon=":material/badge:"
        ),
        st.Page(
            PAGES_DIR / "5_avalie.py",
            title="Avalie seu modelo",
            icon=":material/upload_file:",
        ),
    ]
    nav = st.navigation(pages)
    st.sidebar.markdown("### :material/eco: GreenML Score")
    state.dataset_selector()
    st.sidebar.caption(
        f"Carbono e água calculados no contexto {data.REFERENCE_CONTEXT}, "
        "local real de medição."
    )
    nav.run()


main()
