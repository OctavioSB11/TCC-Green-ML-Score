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
import os
import sys
import time
from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neural_network import MLPClassifier

# Garante que a raiz do projeto esteja no sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mlflow

from experiments.config import config
from experiments.dataset import load_dataset, preprocess_features
from green_ml_score.integrations.mlflow import log_greenml_run
from green_ml_score.integrations.sklearn import GreenMLSklearnWrapper
from green_ml_score.scoring.gms import (
    EnvironmentalMetrics,
    NormalizationBounds,
    Weights,
    calculate_gms,
)


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
        "--dataset",
        type=str,
        default="all",
        choices=["all", "newsgroups", "breast_cancer", "covtype"],
        help="Dataset a ser utilizado. Padrão: 'all' (executa todos).",
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


def get_models_dict(include_all: bool = True, random_state: int = 42) -> dict[str, Any]:
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
    datasets_to_run = (
        config.AVAILABLE_DATASETS if args.dataset == "all" else [args.dataset]
    )

    # N repetições de fit/predict por seed para aumentar a carga e a precisão da medição
    workload_loops = 1 if args.quick_run else 10

    # Perfis Regionais para demonstrar independência das dimensões da métrica
    regional_scenarios = {
        "Brasil_SP": {
            "carbon_intensity": config.CARBON_INTENSITY_SAO_PAULO, # 120.0 gCO2e/kWh
            "wue": config.WUE_GOOGLE_2024,                        # 0.52 L/kWh
        },
        "EUA_East": {
            "carbon_intensity": config.CARBON_INTENSITY_US_GRID,   # 380.0 gCO2e/kWh
            "wue": 1.1,                                           # 1.1 L/kWh (Azure / US avg)
        },
        "Alemanha": {
            "carbon_intensity": 480.0,                             # 480.0 gCO2e/kWh (Alta dependência de carvão/gás)
            "wue": config.WUE_INDUSTRY_AVG,                       # 1.8 L/kWh (Resfriamento tradicional)
        }
    }

    print("=" * 70)
    print("[*] INICIANDO EXPERIMENTO COMPARATIVO GREENML SCORE (REVISED & ROBUST)")
    print(f"Modo: {'QUICK RUN (Rápido)' if args.quick_run else 'COMPLETO (Workload Loop N=' + str(workload_loops) + ')'}")
    print(f"Cenários Regionais: {list(regional_scenarios.keys())}")
    print(f"Seeds: {seeds}")
    print(f"Datasets: {datasets_to_run}")
    print("=" * 70)

    # Configuração do MLflow
    mlflow.set_experiment(config.MLFLOW_EXPERIMENT_NAME)

    for dataset_name in datasets_to_run:
        print(f"\n{'='*50}\n>>> PROCESSANDO DATASET: {dataset_name.upper()}\n{'='*50}")

        # 1. Carregamento dos dados
        X_train_raw, X_test_raw, y_train, y_test, is_text = load_dataset(
            name=dataset_name, quick_run=args.quick_run, random_state=seeds[0]
        )
        X_train_processed, X_test_processed, _ = preprocess_features(
            X_train_raw, X_test_raw, is_text
        )

        print(
            f"Dataset {dataset_name} carregado: {len(X_train_raw)} treino | {len(X_test_raw)} teste"
        )

        raw_results = []
        env_metrics_list = []

        sample_models = get_models_dict(
            include_all=include_all_models, random_state=seeds[0]
        )

        for model_name in sample_models.keys():
            for seed in seeds:
                print(f"\n Treinando {model_name} (Seed: {seed}, Workload Loops: {workload_loops}) no {dataset_name}...")

                model_instances = get_models_dict(
                    include_all=include_all_models, random_state=seed
                )
                base_model = model_instances[model_name]

                # Usaremos o cenário de SP como baseline para coleta primária de energia
                base_env = regional_scenarios["Brasil_SP"]
                temp_bounds = NormalizationBounds(
                    energy_max=1.0, carbon_max=1.0, water_max=1.0
                )
                tracker_kwargs = {
                    "carbon_intensity_g_per_kwh": base_env["carbon_intensity"],
                    "wue_liters_per_kwh": base_env["wue"],
                    "log_level": "error",
                }

                green_model = GreenMLSklearnWrapper(
                    model=base_model, bounds=temp_bounds, tracker_kwargs=tracker_kwargs
                )

                start_time = time.time()

                with mlflow.start_run(
                    run_name=f"{dataset_name}_{model_name}_seed_{seed}"
                ):
                    green_model.tracker.start()
                    try:
                        # Executa o loop de carga de trabalho para acumular tempo e energia mensuráveis
                        for loop_idx in range(workload_loops):
                            # Reinicia o modelo a cada iteração do loop se necessário ou ajusta parcial
                            if loop_idx > 0:
                                model_instances_loop = get_models_dict(
                                    include_all=include_all_models, random_state=seed + loop_idx
                                )
                                base_model_loop = model_instances_loop[model_name]
                                base_model_loop.fit(X_train_processed, y_train)
                                y_pred = base_model_loop.predict(X_test_processed)
                            else:
                                green_model.model.fit(X_train_processed, y_train)
                                y_pred = green_model.model.predict(X_test_processed)
                    finally:
                        green_model.tracker.stop()

                    elapsed_time = time.time() - start_time
                    acc = accuracy_score(y_test, y_pred)
                    f1 = f1_score(y_test, y_pred, average="macro")

                    metrics: EnvironmentalMetrics = green_model.tracker.get_metrics()
                    env_metrics_list.append(metrics)

                    mlflow.log_metric("accuracy", acc)
                    mlflow.log_metric("f1_macro", f1)
                    mlflow.log_metric("train_time_seconds", elapsed_time)
                    mlflow.log_param("model_name", model_name)
                    mlflow.log_param("dataset", dataset_name)
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

        # 4. Normalização Global Relativa e Cenas Regionais do GMS
        global_bounds = NormalizationBounds.from_metrics_list(env_metrics_list)
        uniform_weights = Weights()

        print("\n" + "-" * 50)
        print(f"[*] RECALCULANDO GMS GLOBAL PARA {dataset_name.upper()}")
        print(
            f"Limites Max: Energia={global_bounds.energy_max:.6f}kWh | Carbono={global_bounds.carbon_max:.6f}kg | Água={global_bounds.water_max:.6f}L"
        )
        print("-" * 50)

        final_rows = []
        for res in raw_results:
            # Cálculo no cenário Brasil
            gms_br = calculate_gms(
                metrics=res["metrics_obj"],
                bounds=global_bounds,
                weights=uniform_weights,
                scale_100=True,
            )

            # Cálculo de cenários simulados EUA e Alemanha (demonstrando ortogonalidade)
            e_kwh = res["energy_kwh"]
            c_us = e_kwh * (regional_scenarios["EUA_East"]["carbon_intensity"] / 1000.0)
            w_us = e_kwh * regional_scenarios["EUA_East"]["wue"]
            metrics_us = EnvironmentalMetrics(energy=e_kwh, carbon=c_us, water=w_us)
            
            # Limites adaptados para EUA
            bounds_us = NormalizationBounds(
                energy_max=global_bounds.energy_max,
                carbon_max=global_bounds.energy_max * (regional_scenarios["EUA_East"]["carbon_intensity"] / 1000.0),
                water_max=global_bounds.energy_max * regional_scenarios["EUA_East"]["wue"],
            )
            gms_us = calculate_gms(metrics=metrics_us, bounds=bounds_us, weights=uniform_weights, scale_100=True)

            res["GMS_Brasil"] = gms_br
            res["GMS_EUA"] = gms_us

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
                    "GreenML Score (BR)": gms_br,
                    "GreenML Score (US)": gms_us,
                }
            )

        df_results = pd.DataFrame(final_rows)

        # 5. Agregação Estatística
        summary_list = []
        for model_name_group, group in df_results.groupby("Modelo"):
            summary_list.append(
                {
                    "Modelo": model_name_group,
                    "Acurácia (Média)": round(group["Acurácia"].mean(), 4),
                    "Acurácia (Std)": (
                        round(group["Acurácia"].std(), 4) if len(group) > 1 else 0.0
                    ),
                    "F1-Score (Média)": round(group["F1-Score"].mean(), 4),
                    "Tempo s (Média)": round(group["Tempo (s)"].mean(), 2),
                    "Energia kWh (Média)": round(group["Energia (kWh)"].mean(), 6),
                    "Carbono kg (Média)": round(group["Carbono (kg)"].mean(), 6),
                    "Água L (Média)": round(group["Água (L)"].mean(), 6),
                    "GreenML Score (Média)": round(group["GreenML Score (BR)"].mean(), 2),
                    "GreenML Score (Std)": (
                        round(group["GreenML Score (BR)"].std(), 2)
                        if len(group) > 1
                        else 0.0
                    ),
                }
            )

        df_summary = pd.DataFrame(summary_list).sort_values(
            by="GreenML Score (Média)", ascending=False
        )

        print(f"\n--- RESUMO {dataset_name.upper()} ---")
        print(df_summary.to_string(index=False))

        # 6. Gravação dos Resultados
        output_dir = os.path.join("experiments", "results")
        os.makedirs(output_dir, exist_ok=True)

        csv_detailed = os.path.join(output_dir, "comparative_results.csv")
        csv_summary = os.path.join(output_dir, "summary_metrics.csv")
        md_summary = os.path.join(output_dir, "summary_table.md")

        df_results.round(6).to_csv(csv_detailed, index=False)
        df_summary.to_csv(csv_summary, index=False)

        with open(md_summary, "w", encoding="utf-8") as f:
            f.write(f"# Resumo Estatístico - Dataset {dataset_name.upper()}\n\n")
            f.write(df_summary.to_markdown(index=False))
            f.write("\n")

    print("\n[OK] Experimento concluído com sucesso!")


if __name__ == "__main__":
    run_experiment()
