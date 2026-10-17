import time

import mlflow
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

from green_ml_score.integrations.sklearn import GreenMLSklearnWrapper
from green_ml_score.scoring import NormalizationBounds


def main():
    print("Gerando dataset...")
    X, y = make_classification(n_samples=50000, n_features=20, random_state=42)

    # 1. Definir os máximos de normalização (baseado no histórico da sua empresa)
    # Por exemplo: Sabemos que o pior modelo gastou 1.5kWh, emitiu 0.2kg de carbono e 2.7L de água
    bounds = NormalizationBounds(energy_max=1.5, carbon_max=0.2, water_max=2.7)

    print("Iniciando treinamento com GreenML Tracker...")

    # 2. Configurar o MLflow
    mlflow.set_experiment("GreenML_Demonstration")

    with mlflow.start_run():
        # 3. Envolver seu modelo Scikit-Learn com o GreenML Wrapper
        base_rf = RandomForestClassifier(n_estimators=100, n_jobs=-1)

        # O Wrapper injeta o tracker no .fit().
        # IC do Brasil em 2024 (Ember, 106,06 gCO2/kWh) e WUE da Microsoft (FY24, 0,30 L/kWh),
        # conforme protocolo experimental da Seção 5.4 do TCC.
        green_rf = GreenMLSklearnWrapper(
            base_rf,
            bounds=bounds,
            tracker_kwargs={
                "carbon_intensity_g_per_kwh": 106.06,
                "wue_liters_per_kwh": 0.30,
            },
        )

        # Para simular um treino demorado e forçar gasto energético
        start = time.time()
        green_rf.fit(X, y)
        end = time.time()

        # 4. Avaliação tradicional de performance
        accuracy = green_rf.score(X, y)
        mlflow.log_metric("accuracy", accuracy)

        print(f"Treinamento concluído em {end - start:.2f} segundos.")
        print(f"Acurácia: {accuracy:.4f}")

        # O GreenML_Score e as métricas ambientais já foram logadas automaticamente
        # pelo Wrapper na chamada green_rf.fit()!

        print("\nVerifique o MLflow UI (comando: mlflow ui) para ver o GreenML Score!")


if __name__ == "__main__":
    main()
