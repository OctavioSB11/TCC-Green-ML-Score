"""
generate_results.py — Gerador de Visualizações e Tabelas Científicas (Semana 5 do TCC).

Transforma os resultados brutos dos experimentos em:
1. Gráficos de alta resolução (300 DPI + SVG vetorial para Banner e Apresentação).
   - Bar Chart: GreenML Score por modelo com barras de erro (std das seeds).
   - Scatter Plot: Fronteira de Pareto (Acurácia vs. GreenML Score - Trade-off Green AI).
   - Radar Chart (Spider Plot): Comparação multidimensional dos modelos.
   - Dual Bar Chart: Consumo Energético (kWh) vs. Tempo de Treinamento (s).
2. Tabela formal em LaTeX (pronta com booktabs para inclusão direta no artigo).
3. Documentação analítica com discussão dos resultados para o TCC.
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configuração de estilo visual acadêmico e profissional
plt.style.use(
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 14,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)

# Paleta cromática ecológica / Green AI
PALETTE = {
    "Logistic_Regression": "#2ca02c",  # Verde vibrante (Sustentável)
    "Random_Forest": "#1f77b4",  # Azul clássico
    "MLP_Neural_Network": "#ff7f0e",  # Laranja (Neural)
    "XGBoost": "#d62728",  # Vermelho (Maior consumo)
}

FRIENDLY_NAMES = {
    "Logistic_Regression": "Regressão Logística",
    "Random_Forest": "Random Forest",
    "MLP_Neural_Network": "Rede Neural (MLP)",
    "XGBoost": "XGBoost",
}


def load_data(results_dir):
    detailed_csv = os.path.join(results_dir, "comparative_results.csv")
    summary_csv = os.path.join(results_dir, "summary_metrics.csv")

    if not os.path.exists(detailed_csv) or not os.path.exists(summary_csv):
        return None, None

    df_detailed = pd.read_csv(detailed_csv)
    df_summary = pd.read_csv(summary_csv)
    return df_detailed, df_summary


def plot_gms_barchart(df_summary, output_dir):
    """Gera gráfico de barras do GreenML Score com desvio padrão das seeds."""
    df_sorted = df_summary.sort_values(by="GreenML Score (Média)", ascending=True)

    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    models = df_sorted["Modelo"].tolist()
    labels = [FRIENDLY_NAMES.get(m, m) for m in models]
    scores = df_sorted["GreenML Score (Média)"].tolist()
    stds = df_sorted["GreenML Score (Std)"].tolist()
    colors = [PALETTE.get(m, "#4c72b0") for m in models]

    bars = ax.barh(
        labels,
        scores,
        xerr=stds,
        capsize=6,
        color=colors,
        edgecolor="black",
        alpha=0.88,
        height=0.6,
    )

    # Margem confortável para que os textos fiquem fora da barra e dos whiskers de erro
    ax.set_xlim(0, 120)
    ax.set_xlabel(
        "GreenML Score (0 a 100) — Quanto maior, mais sustentável", fontweight="bold"
    )
    ax.set_title(
        "Ranking de Sustentabilidade: GreenML Score Médio por Modelo (3 Seeds)", pad=16
    )

    # Rótulos numéricos posicionados após a barra de erro (whisker)
    for bar, score, std in zip(bars, scores, stds):
        width = bar.get_width()
        # Posiciona o texto após o limite máximo do erro
        x_text = width + std + 3.0
        text = f"{score:.1f} ± {std:.1f}" if std > 0 else f"{score:.1f}"
        ax.text(
            x_text,
            bar.get_y() + bar.get_height() / 2,
            text,
            va="center",
            ha="left",
            fontsize=10.5,
            fontweight="bold",
            color="#1c1c1c",
        )

    ax.grid(axis="x", linestyle="--", alpha=0.6)
    plt.tight_layout()

    for ext in ["png", "svg"]:
        fig.savefig(os.path.join(output_dir, f"gms_comparison_barchart.{ext}"))
    plt.close(fig)
    print(" Gráfico de barras do GMS gerado (sem sobreposição).")


def plot_pareto_scatter(df_summary, output_dir):
    """Gera gráfico de dispersão Acurácia vs GreenML Score (Fronteira de Pareto)."""
    fig, ax = plt.subplots(figsize=(9.5, 6.2))

    # Destaque da Região Ótima (Green AI Quadrant) ao fundo
    ax.axvspan(
        0.90,
        0.94,
        ymin=0.55,
        ymax=0.98,
        color="#2ca02c",
        alpha=0.08,
        label="Região Ótima (Alta Acurácia & Alto GMS)",
    )

    # Mapeamento manual de offsets de texto para cada modelo
    custom_offsets = {
        "Logistic_Regression": {"dx": -0.002, "dy": 4.5, "ha": "right", "va": "bottom"},
        "Rede Neural (MLP)": {"dx": 0.003, "dy": -3.0, "ha": "left", "va": "top"},
        "MLP_Neural_Network": {"dx": 0.003, "dy": -3.0, "ha": "left", "va": "top"},
        "Random_Forest": {"dx": 0.003, "dy": 3.0, "ha": "left", "va": "bottom"},
        "XGBoost": {"dx": 0.004, "dy": 2.0, "ha": "left", "va": "center"},
    }

    for _, row in df_summary.iterrows():
        m = row["Modelo"]
        x = row["Acurácia (Média)"]
        y = row["GreenML Score (Média)"]
        x_err = row["Acurácia (Std)"]
        y_err = row["GreenML Score (Std)"]
        color = PALETTE.get(m, "#4c72b0")
        label = FRIENDLY_NAMES.get(m, m)

        ax.errorbar(
            x,
            y,
            xerr=x_err,
            yerr=y_err,
            fmt="o",
            markersize=11,
            color=color,
            ecolor=color,
            capsize=5,
            elinewidth=1.6,
            markeredgecolor="black",
            label=label,
            zorder=4,
        )

        offset = custom_offsets.get(
            m, {"dx": 0.003, "dy": 2.0, "ha": "left", "va": "bottom"}
        )
        ax.annotate(
            f"{label}\n(GMS: {y:.1f} | Acc: {x*100:.1f}%)",
            xy=(x, y),
            xytext=(x + offset["dx"], y + offset["dy"]),
            fontsize=9.5,
            fontweight="bold",
            ha=offset["ha"],
            va=offset["va"],
            bbox=dict(
                boxstyle="round,pad=0.35", fc="white", ec=color, alpha=0.92, lw=1.2
            ),
            zorder=5,
        )

    ax.set_xlabel("Performance Preditiva — Acurácia Média", fontweight="bold")
    ax.set_ylabel("Sustentabilidade — GreenML Score Médio (0 a 100)", fontweight="bold")
    ax.set_title("Trade-off de Sustentabilidade: Acurácia vs. GreenML Score", pad=14)
    ax.set_xlim(0.850, 0.940)
    ax.set_ylim(-5, 115)
    ax.grid(True, linestyle="--", alpha=0.5)

    # Legenda limpa e externa na parte inferior (padrão de artigo científico IEEE)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.13),
        ncol=3,
        frameon=True,
        framealpha=0.95,
        edgecolor="#cccccc",
    )

    plt.tight_layout()
    for ext in ["png", "svg"]:
        fig.savefig(os.path.join(output_dir, f"pareto_tradeoff_scatter.{ext}"))
    plt.close(fig)
    print(" Gráfico de dispersão (Trade-off de Pareto) gerado (sem sobreposição).")


def plot_radar_chart(df_summary, output_dir):
    """Gera gráfico de radar (Spider Chart) multidimensional normalizado com margens amplas."""
    categories = [
        "Acurácia",
        "F1-Score",
        "Eficiência\nEnergética",
        "Baixa Emissão\nde Carbono",
        "Baixo Consumo\nHídrico",
    ]
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Fecha o polígono

    e_max = df_summary["Energia kWh (Média)"].max()
    c_max = df_summary["Carbono kg (Média)"].max()
    w_max = df_summary["Água L (Média)"].max()

    fig, ax = plt.subplots(figsize=(8.5, 8.5), subplot_kw=dict(polar=True))

    for _, row in df_summary.iterrows():
        m = row["Modelo"]
        acc = row["Acurácia (Média)"]
        f1 = row["F1-Score (Média)"]
        e_norm = 1.0 - (row["Energia kWh (Média)"] / e_max) if e_max > 0 else 1.0
        c_norm = 1.0 - (row["Carbono kg (Média)"] / c_max) if c_max > 0 else 1.0
        w_norm = 1.0 - (row["Água L (Média)"] / w_max) if w_max > 0 else 1.0

        values = [acc, f1, e_norm, c_norm, w_norm]
        values += values[:1]

        color = PALETTE.get(m, "#4c72b0")
        label = FRIENDLY_NAMES.get(m, m)

        ax.plot(
            angles, values, linewidth=2.2, linestyle="solid", label=label, color=color
        )
        ax.fill(angles, values, color=color, alpha=0.12)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Pad equilibrado para os nomes das categorias
    ax.tick_params(axis="x", pad=12)
    plt.xticks(angles[:-1], categories, size=10.5, weight="bold")

    # Posiciona os marcadores radiais em 45 graus com tamanho discreto
    ax.set_rlabel_position(45)
    plt.yticks(
        [0.2, 0.4, 0.6, 0.8, 1.0],
        ["0.2", "0.4", "0.6", "0.8", "1.0"],
        color="#666666",
        size=8.5,
    )
    ax.set_ylim(0, 1.15)

    # Título posicionado no topo com suptitle para não colidir com o label 'Acurácia'
    fig.suptitle(
        "Comparação Multidimensional dos Modelos (Normalizada)",
        size=13.5,
        weight="bold",
        y=0.98,
    )
    plt.legend(loc="upper right", bbox_to_anchor=(1.25, 1.08), frameon=True)

    plt.tight_layout()
    for ext in ["png", "svg"]:
        fig.savefig(os.path.join(output_dir, f"radar_multidimensional_chart.{ext}"))
    plt.close(fig)
    print(" Gráfico de radar (Spider Chart) gerado (sem sobreposição).")


def plot_energy_time_barchart(df_summary, output_dir):
    """Gera gráfico comparativo de Consumo Energético e Tempo de Treinamento."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    models = df_summary["Modelo"].tolist()
    labels = [FRIENDLY_NAMES.get(m, m) for m in models]
    colors = [PALETTE.get(m, "#4c72b0") for m in models]

    # Subplot 1: Energia em uWh (para facilitar visualização em números legíveis)
    # 1 kWh = 1.000.000 mWh (a versão anterior rotulava, por engano, como micro-Wh)
    energy_mwh = [e * 1e6 for e in df_summary["Energia kWh (Média)"]]
    bars1 = ax1.bar(labels, energy_mwh, color=colors, edgecolor="black", alpha=0.88)
    ax1.set_ylabel("Energia de treino por repetição (mWh)", fontweight="bold")
    ax1.set_title("Consumo de Energia por Modelo", pad=10)
    ax1.tick_params(axis="x", rotation=25)
    for bar, val in zip(bars1, energy_mwh):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            f"{val:.2f} mWh",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    # Subplot 2: Tempo de Treino em Segundos
    times = df_summary["Tempo s (Média)"].tolist()
    bars2 = ax2.bar(labels, times, color=colors, edgecolor="black", alpha=0.88)
    ax2.set_ylabel("Tempo de Treinamento (segundos)", fontweight="bold")
    ax2.set_title("Tempo de Execução por Modelo", pad=10)
    ax2.tick_params(axis="x", rotation=25)
    for bar, val in zip(bars2, times):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.1,
            f"{val:.2f}s",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    for ext in ["png", "svg"]:
        fig.savefig(os.path.join(output_dir, f"energy_and_time_comparison.{ext}"))
    plt.close(fig)
    print(" Gráfico de consumo de energia e tempo gerado.")


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def generate_latex_table(df_summary, output_dir):
    """Gera tabela formal em LaTeX com padrão booktabs para o artigo do TCC."""
    tex_path = os.path.join(output_dir, "summary_table.tex")

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        r"\caption{Resultados experimentais comparativos entre acurácia preditiva e métricas ambientais (Média $\pm$ Desvio Padrão sobre 3 sementes).}",
        r"\label{tab:resultados_greenml}",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r"\textbf{Modelo} & \textbf{Acurácia} & \textbf{F1-Score} & \textbf{Tempo (s)} & \textbf{Energia (kWh)} & \textbf{Carbono (kg)} & \textbf{GreenML Score} \\",
        r"\midrule",
    ]

    for _, row in df_summary.iterrows():
        name = FRIENDLY_NAMES.get(row["Modelo"], row["Modelo"])
        acc = f"{row['Acurácia (Média)']:.4f}"
        if row["Acurácia (Std)"] > 0:
            acc += f" $\\pm$ {row['Acurácia (Std)']:.4f}"

        f1 = f"{row['F1-Score (Média)']:.4f}"
        tempo = f"{row['Tempo s (Média)']:.2f}"
        energia = f"{row['Energia kWh (Média)']*1e6:.2f}~mWh"
        carbono = f"{row['Carbono kg (Média)']*1e6:.1f}~mg"

        gms = f"\\textbf{{{row['GreenML Score (Média)']:.1f}}}"
        if row["GreenML Score (Std)"] > 0:
            gms += f" $\\pm$ {row['GreenML Score (Std)']:.1f}"

        lines.append(
            f"{name} & {acc} & {f1} & {tempo} & {energia} & {carbono} & {gms} \\\\"
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
    )

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[OK] Tabela LaTeX gerada em: {tex_path}")


def generate_discussion_readme(df_summary, output_dir):
    """
    Gera um README descritivo a partir dos dados (sem conclusões pré-redigidas).

    Interpretações e confirmação/refutação de hipóteses pertencem ao texto do TCC
    e devem ser sustentadas pelos testes estatísticos (statistical_analysis.py).
    """
    readme_path = os.path.join(output_dir, "README.md")
    cols = {
        "Modelo": "Modelo",
        "N": "N",
        "Acurácia (Média)": "Acurácia (média)",
        "Energia mWh (Mediana)": "Energia de treino, mWh (mediana)",
        "Energia mWh (IQR)": "Energia, mWh (IQR)",
        "Tempo s (Média)": "Tempo de treino, s (média)",
        "GreenML Score (Mediana)": "GMS (mediana)",
        "GreenML Score (IQR)": "GMS (IQR)",
    }
    available = [c for c in cols if c in df_summary.columns]
    table = df_summary[available].rename(columns=cols).round(4).to_markdown(index=False)

    content = f"""# Resultados — {output_dir}

Arquivos gerados automaticamente por `experiments/generate_results.py` a partir de
`summary_metrics.csv`. Valores de energia referem-se a UMA repetição de treino.

{table}

Figuras: `gms_comparison_barchart`, `pareto_tradeoff_scatter`,
`radar_multidimensional_chart`, `energy_and_time_comparison` (PNG e SVG) e
`summary_table.tex`. Para testes de hipótese, execute
`experiments/statistical_analysis.py`.
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Documentação de resultados gerada em: {readme_path}")


def main() -> None:
    """Gera figuras e tabelas para cada dataset/modo em experiments/results/<dataset>/<modo>/."""
    base_results_dir = "experiments/results"
    base_output_dir = "docs/Results"

    if not os.path.isdir(base_results_dir):
        print("Nenhum resultado encontrado. Execute o experimento primeiro.")
        return

    print("=" * 70)
    print("[*] GERANDO VISUALIZAÇÕES GRÁFICAS E TABELAS MULTI-DATASET")
    print("=" * 70)

    for dataset in sorted(os.listdir(base_results_dir)):
        dataset_dir = os.path.join(base_results_dir, dataset)
        if not os.path.isdir(dataset_dir):
            continue
        for mode in sorted(os.listdir(dataset_dir)):
            results_dir = os.path.join(dataset_dir, mode)
            if not os.path.exists(os.path.join(results_dir, "summary_metrics.csv")):
                continue
            output_dir = os.path.join(base_output_dir, dataset, mode)
            os.makedirs(output_dir, exist_ok=True)
            print(f"\nProcessando {dataset} ({mode})...")
            _, df_summary = load_data(results_dir)
            plot_gms_barchart(df_summary, output_dir)
            plot_pareto_scatter(df_summary, output_dir)
            plot_radar_chart(df_summary, output_dir)
            plot_energy_time_barchart(df_summary, output_dir)
            generate_latex_table(df_summary, output_dir)
            generate_discussion_readme(df_summary, output_dir)
            print(f"[OK] Visualizações salvas em {output_dir}")


if __name__ == "__main__":
    main()
