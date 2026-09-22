import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Adicionar a raiz ao sys.path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from green_ml_score.scoring.gms import (
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
    calculate_gms,
)

plt.style.use(
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)
plt.rcParams.update(
    {"font.size": 11, "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight"}
)

PALETTE = {
    "Logistic_Regression": "#2ca02c",
    "Random_Forest": "#1f77b4",
    "MLP_Neural_Network": "#ff7f0e",
    "XGBoost": "#d62728",
}

FRIENDLY_NAMES = {
    "Logistic_Regression": "Regressão Logística",
    "Random_Forest": "Random Forest",
    "MLP_Neural_Network": "Rede Neural (MLP)",
    "XGBoost": "XGBoost",
}


def analyze_sensitivity(dataset_name="newsgroups"):
    csv_path = os.path.join(
        "experiments", "results", dataset_name, "comparative_results.csv"
    )
    output_dir = os.path.join("docs", "Results", dataset_name)

    if not os.path.exists(csv_path):
        print(
            f"Erro: Resultados não encontrados para o dataset {dataset_name}. Execute o experimento primeiro."
        )
        return

    df = pd.read_csv(csv_path)
    os.makedirs(output_dir, exist_ok=True)

    # 1. Definir os cenários
    scenarios = {
        "Neutro\n(w_E=33%, w_C=33%, w_W=33%)": Weights(w_E=1 / 3, w_C=1 / 3, w_W=1 / 3),
        "Matriz Fóssil\n(w_C=50%, w_E=20%, w_W=30%)": Weights(
            w_E=0.2, w_C=0.5, w_W=0.3
        ),
        "Estresse Hídrico\n(w_W=50%, w_E=30%, w_C=20%)": Weights(
            w_E=0.3, w_C=0.2, w_W=0.5
        ),
    }

    # 2. Recalcular os scores
    metrics_objs = [
        EnvironmentalMetrics(row["energy_kwh"], row["carbon_kg"], row["water_liters"])
        for _, row in df.iterrows()
    ]
    global_bounds = NormalizationBounds.from_metrics_list(metrics_objs)

    results = {scenario_name: [] for scenario_name in scenarios}
    models = df["model_name"].unique()

    for model in models:
        df_model = df[df["model_name"] == model]
        metrics_model = [
            EnvironmentalMetrics(
                row["energy_kwh"], row["carbon_kg"], row["water_liters"]
            )
            for _, row in df_model.iterrows()
        ]

        for scenario_name, weights in scenarios.items():
            scores = [
                calculate_gms(m, global_bounds, weights, scale_100=True)
                for m in metrics_model
            ]
            avg_score = np.mean(scores)
            results[scenario_name].append((model, avg_score))

    # 3. Plotar o gráfico
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(scenarios))
    width = 0.2

    multiplier = 0

    for model in models:
        model_scores = [dict(results[scenario])[model] for scenario in scenarios.keys()]
        offset = width * multiplier
        ax.bar(
            x + offset,
            model_scores,
            width,
            label=FRIENDLY_NAMES.get(model, model),
            color=PALETTE.get(model, "#000"),
        )
        multiplier += 1

    ax.set_ylabel("GreenML Score (0-100)", fontweight="bold")
    ax.set_title(
        f"Análise de Sensibilidade Contextual — Dataset: {dataset_name.upper()}",
        pad=20,
        fontweight="bold",
    )
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(scenarios.keys())

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=4)
    ax.set_ylim(0, 115)

    # Adicionar o valor exato no topo das barras
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", padding=3, fontsize=8)

    plt.tight_layout()
    for ext in ["png", "svg"]:
        fig.savefig(os.path.join(output_dir, f"sensitivity_analysis.{ext}"))
    plt.close(fig)
    print(f"[OK] Gráfico de sensibilidade gerado para o dataset {dataset_name}.")


if __name__ == "__main__":
    # Podemos iterar por todos os datasets existentes
    base_results = os.path.join("experiments", "results")
    if os.path.exists(base_results):
        datasets = [
            d
            for d in os.listdir(base_results)
            if os.path.isdir(os.path.join(base_results, d))
        ]
        for d in datasets:
            analyze_sensitivity(d)
    else:
        print("Nenhum resultado encontrado. Execute os experimentos primeiro.")
