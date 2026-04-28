from typing import Any, Optional
from green_ml_score.tracker.core import GreenMLTracker
from green_ml_score.greenml_mlflow import log_greenml_run
from green_ml_score.greenmlscore import NormalizationBounds

class GreenMLSklearnWrapper:
    """
    Um wrapper simples que "envolve" qualquer modelo Scikit-Learn e
    automaticamente liga/desliga o GreenMLTracker ao redor da função .fit()
    
    Exemplo:
        rf = RandomForestClassifier()
        green_rf = GreenMLSklearnWrapper(rf, bounds=my_bounds)
        green_rf.fit(X_train, y_train)
        
        # O tracker automaticamente roda durante o .fit() e as métricas 
        # são jogadas no MLflow (se ativo).
    """

    def __init__(self, model: Any, bounds: NormalizationBounds, 
                 tracker_kwargs: Optional[dict] = None):
        self.model = model
        self.bounds = bounds
        self.tracker_kwargs = tracker_kwargs or {}
        self.tracker = GreenMLTracker(**self.tracker_kwargs)

    def fit(self, X, y, **kwargs):
        self.tracker.start()
        
        try:
            self.model.fit(X, y, **kwargs)
        finally:
            self.tracker.stop()
            # Log automatico no MLflow se houver uma execuçao ativa 
            import mlflow
            if mlflow.active_run():
                log_greenml_run(self.tracker, self.bounds)

        return self

    def predict(self, X):
        return self.model.predict(X)

    def __getattr__(self, name):
        # Delega qualquer outra chamada (ex: predict_proba) direto pro modelo original
        return getattr(self.model, name)
