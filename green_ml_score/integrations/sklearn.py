"""
Wrapper Scikit-Learn que mede automaticamente o consumo do ``fit``.
"""

from __future__ import annotations

from typing import Any

import mlflow

from green_ml_score.collectors.codecarbon import GreenMLTracker
from green_ml_score.integrations.mlflow import log_greenml_run
from green_ml_score.scoring.gms import NormalizationBounds, Weights


class GreenMLSklearnWrapper:
    """
    Envolve qualquer estimador Scikit-Learn e liga/desliga o GreenMLTracker
    ao redor de ``fit()``.

    Exemplo:
        green_rf = GreenMLSklearnWrapper(RandomForestClassifier())
        green_rf.fit(X_train, y_train)   # métricas absolutas vão ao MLflow, se ativo

    O GMS só é calculado se ``bounds`` for informado (ver ``log_greenml_run``).
    """

    def __init__(
        self,
        model: Any,
        bounds: NormalizationBounds | None = None,
        weights: Weights | None = None,
        tracker_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.model = model
        self.bounds = bounds
        self.weights = weights
        self.tracker_kwargs = tracker_kwargs or {}
        self.tracker = GreenMLTracker(**self.tracker_kwargs)

    def fit(self, X: Any, y: Any, **kwargs: Any) -> GreenMLSklearnWrapper:
        self.tracker.start()
        try:
            self.model.fit(X, y, **kwargs)
        finally:
            self.tracker.stop()
            if mlflow.active_run():
                log_greenml_run(self.tracker, self.bounds, self.weights)
        return self

    def predict(self, X: Any) -> Any:
        return self.model.predict(X)

    def __getattr__(self, name: str) -> Any:
        # Delega demais atributos (ex.: predict_proba) ao estimador original
        return getattr(self.model, name)
