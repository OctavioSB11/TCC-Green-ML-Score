"""
test_sklearn_wrapper.py — Testes unitários para o GreenMLSklearnWrapper.

Aplica o padrão CTFL / ISTQB:
- Testes estruturais (Caixa-Branca): Garante cobertura dos blocos try/finally e delegação de chamadas.
- Teste de segurança contra falhas (Exception Handling / Robustness): O tracker deve parar mesmo se o fit() lançar exceção.
- Mocks para Scikit-Learn base estimator e MLflow.
"""

from unittest.mock import MagicMock, patch
import pytest

from green_ml_score.integrations.sklearn import GreenMLSklearnWrapper


def test_wrapper_fit_lifecycle_success(sample_bounds):
    """Garante que .fit() inicia o tracker, treina o modelo base e para o tracker."""
    # Arrange
    mock_base_model = MagicMock()
    wrapper = GreenMLSklearnWrapper(model=mock_base_model, bounds=sample_bounds)
    wrapper.tracker = MagicMock()

    X = [[1, 2], [3, 4]]
    y = [0, 1]

    # Act
    result = wrapper.fit(X, y)

    # Assert
    assert result is wrapper
    wrapper.tracker.start.assert_called_once()
    mock_base_model.fit.assert_called_once_with(X, y)
    wrapper.tracker.stop.assert_called_once()


def test_wrapper_fit_stops_tracker_on_exception(sample_bounds):
    """Garante que o tracker é finalizado (try/finally) mesmo se o fit() falhar."""
    mock_base_model = MagicMock()
    mock_base_model.fit.side_effect = RuntimeError(
        "Erro simulado durante o treinamento"
    )

    wrapper = GreenMLSklearnWrapper(model=mock_base_model, bounds=sample_bounds)
    wrapper.tracker = MagicMock()

    # Act & Assert
    with pytest.raises(RuntimeError, match="Erro simulado"):
        wrapper.fit([[1, 2]], [0])

    wrapper.tracker.start.assert_called_once()
    wrapper.tracker.stop.assert_called_once()


@patch("green_ml_score.integrations.sklearn.log_greenml_run")
@patch("mlflow.active_run")
def test_wrapper_fit_triggers_mlflow_log_when_active(
    mock_active_run, mock_log_greenml_run, sample_bounds
):
    """Garante que o log no MLflow é acionado automaticamente se houver uma run ativa."""
    # Arrange
    mock_active_run.return_value = MagicMock()  # Simula run ativa
    mock_base_model = MagicMock()

    wrapper = GreenMLSklearnWrapper(model=mock_base_model, bounds=sample_bounds)
    wrapper.tracker = MagicMock()

    # Act
    wrapper.fit([[1, 2]], [0])

    # Assert
    mock_log_greenml_run.assert_called_once_with(wrapper.tracker, sample_bounds)


def test_wrapper_delegation_predict_and_getattr(sample_bounds):
    """Garante que o wrapper repassa transparentemente predict() e outros atributos."""
    mock_base_model = MagicMock()
    mock_base_model.predict.return_value = [1, 0]
    mock_base_model.custom_attribute = "valor_especifico"

    wrapper = GreenMLSklearnWrapper(model=mock_base_model, bounds=sample_bounds)

    assert wrapper.predict([[1, 2]]) == [1, 0]
    mock_base_model.predict.assert_called_once_with([[1, 2]])
    assert wrapper.custom_attribute == "valor_especifico"
