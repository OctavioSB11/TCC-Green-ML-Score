"""
comparative_experiment.py — Script Principal de Execução do Experimento Comparativo (Seção 5 do TCC).

Treina e compara múltiplos modelos de Machine Learning (Green AI vs. Red AI),
capturando consumo energético (kWh), emissões de carbono (kg CO2e), pegada hídrica (L)
e calculando o GreenML Score (GMS) normalizado.

Uso:
    python experiments/comparative_experiment.py --quick-run
    python experiments/comparative_experiment.py --models sklearn
    python experiments/comparative_experiment.py --models all --seeds 42 123 2024
"""

import argparse
import time
import os
import sys
from typing import Dict, Any

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score

# Garante que a raiz do projeto esteja no sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mlflow
from green_ml_score.integrations.sklearn import GreenMLSklearnWrapper
from green_ml_score.scoring.gms import (
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
    calculate_gms,
)
from green_ml_score.integrations.mlflow import log_greenml_run

from experiments.config import config
from experiments.dataset import load_benchmark_dataset, get_tfidf_features


def parse_args():
    parser = argparse.ArgumentParser(
        description="Executa o experimento comparativo do GreenML Score (TCC Seção 5)."
    )
    parser.add_argument(
        "--quick-run",
        action="store_true",
        help="Executa em modo rápido (subset reduzido e 1 seed) para testes agéis.",
    )
    parser.add_argument(
        "--models",
        type=str,
        default="all",
        choices=["sklearn", "all"],
        help="Família de modelos a executar: 'sklearn' (rápido/clássico) ou 'all' (completo com XGBoost e MLP).",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=None,
        help="Sementes aleatórias para execução (ex: 42 123 2024).",
    )
    parser.add_argument(
        "--carbon-intensity",
        type=float,
        default=config.CARBON_INTENSITY_SAO_PAULO,
        help="Intensidade de carbono regional (gCO2e/kWh). Padrão: 120.0 (São Paulo).",
    )
    parser.add_argument(
        "--wue",
        type=float,
        default=config.WUE_GOOGLE_2024,
        help="WUE do ambiente em L/kWh. Padrão: 0.52 (Google 2024).",
    )
    return parser.parse_args()


def get_models_dict(include_all: bool = True, random_state: int = 42) -> Dict[str, Any]:
    """Retorna o dicionário de modelos instanciados para avaliação."""
    models = {
        "Logistic_Regression": LogisticRegression(
            max_iter=1000, random_state=random_state
        ),
        "Random_Forest": RandomForestClassifier(
            n_estimators=100, random_state=random_state, n_jobs=-1
        ),
    }

    if include_all:
        try:
            from xgboost import XGBClassifier

            models["XGBoost"] = XGBClassifier(
                n_estimators=100,
                random_state=random_state,
                n_jobs=-1,
                eval_metric="logloss",
            )
        except ImportError:
            print("[AVISO] XGBoost não encontrado. Instale com: pip install xgboost")

        # Adiciona modelo de Rede Neural (MLPClassifier) representando aproximação com Redes Profundas
        models["MLP_Neural_Network"] = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            max_iter=200,
            random_state=random_state,
            early_stopping=True,
        )

    return models


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_experiment():
    args = parse_args()
    seeds = args.seeds or ([42] if args.quick_run else config.SEEDS)
    include_all_models = args.models == "all"

    print("=" * 70)
    print("[*] INICIANDO EXPERIMENTO COMPARATIVO GREENML SCORE (TCC SEÇÃO 5)")
    print(f"Modo: {'QUICK RUN (Rápido)' if args.quick_run else 'COMPLETO'}")
    print(f"Intensidade Carbono (IC): {args.carbon_intensity} gCO2e/kWh")
    print(f"Fator WUE Hídrico: {args.wue} L/kWh")
    print(f"Seeds: {seeds}")
    print("=" * 70)

    # 1. Carregamento dos dados
    X_train_raw, X_test_raw, y_train, y_test = load_benchmark_dataset(
        quick_run=args.quick_run, random_state=seeds[0]
    )
    X_train_tfidf, X_test_tfidf, _ = get_tfidf_features(X_train_raw, X_test_raw)

    print(f"Dataset carregado: {len(X_train_raw)} treino | {len(X_test_raw)} teste")

    # 2. Configuração do MLflow
    mlflow.set_experiment(config.MLFLOW_EXPERIMENT_NAME)

    raw_results = []
    env_metrics_list = []

    # 3. Treinamento e Coleta de Métricas por Modelo e Seed
    # Usamos o primeiro dicionário para iterar pelos nomes dos modelos
    sample_models = get_models_dict(
        include_all=include_all_models, random_state=seeds[0]
    )

    for model_name in sample_models.keys():
        for seed in seeds:
            print(f"\n Treinando {model_name} (Seed: {seed})...")

            # Instancia o modelo especificando a seed atual
            model_instances = get_models_dict(
                include_all=include_all_models, random_state=seed
            )
            base_model = model_instances[model_name]

            temp_bounds = NormalizationBounds(
                energy_max=1.0, carbon_max=1.0, water_max=1.0
            )
            tracker_kwargs = {
                "carbon_intensity_g_per_kwh": args.carbon_intensity,
                "wue_liters_per_kwh": args.wue,
                "log_level": "error",
            }

            green_model = GreenMLSklearnWrapper(
                model=base_model, bounds=temp_bounds, tracker_kwargs=tracker_kwargs
            )

            start_time = time.time()

            with mlflow.start_run(run_name=f"{model_name}_seed_{seed}"):
                green_model.fit(X_train_tfidf, y_train)
                y_pred = green_model.predict(X_test_tfidf)

                elapsed_time = time.time() - start_time
                acc = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average="macro")

                metrics: EnvironmentalMetrics = green_model.tracker.get_metrics()
                env_metrics_list.append(metrics)

                mlflow.log_metric("accuracy", acc)
                mlflow.log_metric("f1_macro", f1)
                mlflow.log_metric("train_time_seconds", elapsed_time)
                mlflow.log_param("model_name", model_name)
                mlflow.log_param("seed", seed)

                raw_results.append(
                    {
                        "model_name": model_name,
                        "seed": seed,
                        "accuracy": acc,
                        "f1_macro": f1,
                        "train_time_s": elapsed_time,
                        "energy_kwh": metrics.energy,
                        "carbon_kg": metrics.carbon,
                        "water_liters": metrics.water,
                        "metrics_obj": metrics,
                        "tracker": green_model.tracker,
                    }
                )

                print(
                    f"   [OK] Acurácia: {acc:.4f} | F1-Score: {f1:.4f} | Tempo: {elapsed_time:.2f}s | Energia: {metrics.energy:.6f} kWh"
                )

    # 4. Normalização Global Relativa e Cálculo do GMS Final (Seção 4 do TCC)
    global_bounds = NormalizationBounds.from_metrics_list(env_metrics_list)
    uniform_weights = Weights()

    print("\n" + "=" * 70)
    print("[*] RECALCULANDO GREENML SCORE (GMS) COM LIMITES GLOBAIS DE NORMALIZAÇÃO")
    print(
        f"Limites Globais: Energia Max={global_bounds.energy_max:.6f}kWh | Carbono Max={global_bounds.carbon_max:.6f}kg | Água Max={global_bounds.water_max:.6f}L"
    )
    print("=" * 70)

    final_rows = []
    for res in raw_results:
        gms_100 = calculate_gms(
            metrics=res["metrics_obj"],
            bounds=global_bounds,
            weights=uniform_weights,
            scale_100=True,
        )
        res["GMS"] = gms_100

        with mlflow.start_run(run_name=f"{res['model_name']}_seed_{res['seed']}"):
            log_greenml_run(res["tracker"], global_bounds, uniform_weights)

        final_rows.append(
            {
                "Modelo": res["model_name"],
                "Seed": res["seed"],
                "Acurácia": res["accuracy"],
                "F1-Score": res["f1_macro"],
                "Tempo (s)": res["train_time_s"],
                "Energia (kWh)": res["energy_kwh"],
                "Carbono (kg)": res["carbon_kg"],
                "Água (L)": res["water_liters"],
                "GreenML Score": gms_100,
            }
        )

    df_results = pd.DataFrame(final_rows)

    # 5. Agregação Estatística (Média e Desvio Padrão por Modelo)
    summary_list = []
    for model_name, group in df_results.groupby("Modelo"):
        summary_list.append(
            {
                "Modelo": model_name,
                "Acurácia (Média)": round(group["Acurácia"].mean(), 4),
                "Acurácia (Std)": (
                    round(group["Acurácia"].std(), 4) if len(group) > 1 else 0.0
                ),
                "F1-Score (Média)": round(group["F1-Score"].mean(), 4),
                "Tempo s (Média)": round(group["Tempo (s)"].mean(), 2),
                "Energia kWh (Média)": round(group["Energia (kWh)"].mean(), 6),
                "Carbono kg (Média)": round(group["Carbono (kg)"].mean(), 6),
                "Água L (Média)": round(group["Água (L)"].mean(), 6),
                "GreenML Score (Média)": round(group["GreenML Score"].mean(), 2),
                "GreenML Score (Std)": (
                    round(group["GreenML Score"].std(), 2) if len(group) > 1 else 0.0
                ),
            }
        )

    df_summary = pd.DataFrame(summary_list).sort_values(
        by="GreenML Score (Média)", ascending=False
    )

    print("\n--- RESULTADOS INDIVIDUAIS POR SEED ---")
    print(df_results.round(4).to_string(index=False))

    print("\n--- RESUMO ESTATÍSTICO DOS MODELOS (ORDENADO POR GMS) ---")
    print(df_summary.to_string(index=False))

    # 6. Gravação dos Resultados em Arquivos
    output_dir = os.path.join("experiments", "results")
    os.makedirs(output_dir, exist_ok=True)

    csv_detailed = os.path.join(output_dir, "comparative_results.csv")
    csv_summary = os.path.join(output_dir, "summary_metrics.csv")
    md_summary = os.path.join(output_dir, "summary_table.md")

    df_results.round(6).to_csv(csv_detailed, index=False)
    df_summary.to_csv(csv_summary, index=False)

    with open(md_summary, "w", encoding="utf-8") as f:
        f.write(
            "# 📊 Resumo Estatístico dos Experimentos Comparativos — GreenML Score\n\n"
        )
        f.write(df_summary.to_markdown(index=False))
        f.write("\n")

    print(f"\n Resultados individuais salvos em: {csv_detailed}")
    print(f" Resumo estatístico salvo em: {csv_summary}")
    print(f" Tabela Markdown salva em: {md_summary}")
    print("Execute 'mlflow ui' no terminal para visualizar a dashboard interativa!")


if __name__ == "__main__":
    run_experiment()
