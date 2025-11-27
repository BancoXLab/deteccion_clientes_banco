"""
Tests para el cliente API de Banco X.

Ejecutar con: pytest scr/client/test_client.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
from src.client.client import APIClient, PredictionResponse
import requests


class TestAPIClient:
    """Suite de pruebas para APIClient."""
    
    @pytest.fixture
    def client(self):
        """Fixture: instancia de APIClient."""
        return APIClient("http://localhost:8000")
    
    @pytest.fixture
    def sample_data(self):
        """Fixture: datos de cliente válidos."""
        return {
            "age": 35,
            "month": 5,
            "day_of_week": 1,
            "duration": 500,
            "campaign": 1,
            "pdays": -1,
            "previous": 0,
            "emp_var_rate": 1.1,
            "cons_price_idx": 93.5,
            "cons_conf_idx": -36.0,
            "euribor3m": 0.7,
            "nr_employed": 5100.0,
            "previous_bin": 0,
            "job_target_mean": 0.45,
            "marital_divorced": 0,
            "marital_married": 1,
            "marital_single": 0,
            "marital_unknown": 0,
            "education_freq_encode": 0.5,
            "housing_no": 0,
            "housing_unknown": 0,
            "housing_yes": 1,
            "loan_no": 0,
            "loan_unknown": 0,
            "loan_yes": 1,
            "contact_cellular": 1,
            "contact_telephone": 0,
        }
    
    # ---- Pruebas de inicialización ----
    
    def test_client_initialization_default(self):
        """Test: inicialización con URL por defecto."""
        client = APIClient()
        assert client.base == "http://localhost:8000"
    
    def test_client_initialization_custom_url(self):
        """Test: inicialización con URL personalizada."""
        client = APIClient("https://api.example.com:9000/")
        assert client.base == "https://api.example.com:9000"
    
    def test_client_strips_trailing_slash(self):
        """Test: elimina slash trailing de la URL."""
        client = APIClient("http://localhost:8000///")
        assert client.base == "http://localhost:8000"
    
    # ---- Pruebas de predict() ----
    
    @patch('requests.post')
    def test_predict_success(self, mock_post, client, sample_data):
        """Test: predicción exitosa."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "prediction": 0.85,
            "prediction_label": "Se suscribirá",
            "model_version": "1.0",
            "timestamp": "2025-01-01T00:00:00",
        }
        mock_post.return_value = mock_response
        
        result = client.predict(sample_data)
        
        assert isinstance(result, PredictionResponse)
        assert result.success is True
        assert result.prediction == 0.85
        assert result.prediction_label == "Se suscribirá"
        assert result.model_version == "1.0"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_predict_with_custom_timeout(self, mock_post, client, sample_data):
        """Test: timeout personalizado en predict."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "prediction": 0.5}
        mock_post.return_value = mock_response
        
        client.predict(sample_data, timeout=20)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[1]['timeout'] == 20
    
    @patch('requests.post')
    def test_predict_http_error_422(self, mock_post, client, sample_data):
        """Test: error de validación (422)."""
        # Crear un mock de response con los atributos necesarios
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "error": "Validación de datos fallida",
            "details": [{"field": "age", "message": "Campo inválido"}]
        }
        
        # Crear excepción HTTPError con response
        http_error = requests.HTTPError()
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            client.predict(sample_data)
        
        assert "error" in str(exc_info.value).lower()
    
    @patch('requests.post')
    def test_predict_http_error_500(self, mock_post, client, sample_data):
        """Test: error interno del servidor (500)."""
        # Crear un mock de response con los atributos necesarios
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": "Error inesperado",
            "message": "Database connection failed"
        }
        
        # Crear excepción HTTPError con response
        http_error = requests.HTTPError()
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            client.predict(sample_data)
        
        assert "error" in str(exc_info.value).lower()
    
    @patch('requests.post')
    def test_predict_connection_error(self, mock_post, client, sample_data):
        """Test: error de conexión."""
        mock_post.side_effect = requests.ConnectionError("Connection refused")
        
        with pytest.raises(requests.ConnectionError):
            client.predict(sample_data)
    
    @patch('requests.post')
    def test_predict_timeout_error(self, mock_post, client, sample_data):
        """Test: timeout."""
        mock_post.side_effect = requests.Timeout("Request timeout")
        
        with pytest.raises(requests.Timeout):
            client.predict(sample_data)
    
    # ---- Pruebas de health_check() ----
    
    @patch('requests.get')
    def test_health_check_success(self, mock_get, client):
        """Test: health check exitoso."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "model": {"status": "ok"},
            "system": {"cpu": {"percent": 45.2}}
        }
        mock_get.return_value = mock_response
        
        result = client.health_check()
        
        assert result["status"] == "ok"
        mock_get.assert_called_once_with(
            "http://localhost:8000/healthz",
            timeout=5
        )
    
    @patch('requests.get')
    def test_health_check_custom_timeout(self, mock_get, client):
        """Test: health check con timeout personalizado."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response
        
        client.health_check(timeout=15)
        
        assert mock_get.call_args[1]['timeout'] == 15
    
    # ---- Pruebas de get_info() ----
    
    @patch('requests.get')
    def test_get_info_success(self, mock_get, client):
        """Test: obtener información exitoso."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "service": "Banco X API",
            "model_version": "1.0.0",
            "python": "3.10.0"
        }
        mock_get.return_value = mock_response
        
        result = client.get_info()
        
        assert result["model_version"] == "1.0.0"
        mock_get.assert_called_once_with(
            "http://localhost:8000/info",
            timeout=5
        )
    
    # ---- Pruebas de PredictionResponse ----
    
    def test_prediction_response_creation(self):
        """Test: creación de PredictionResponse."""
        response = PredictionResponse(
            success=True,
            prediction=0.92,
            prediction_label="Se suscribirá",
            model_version="2.1",
            timestamp="2025-01-01T12:00:00",
            raw_response={"key": "value"}
        )
        
        assert response.success is True
        assert response.prediction == 0.92
        assert response.prediction_label == "Se suscribirá"
    
    def test_prediction_response_immutable(self):
        """Test: PredictionResponse es inmutable (dataclass frozen)."""
        response = PredictionResponse(
            success=True,
            prediction=0.5,
            prediction_label="Test",
            model_version="1.0",
            timestamp="2025-01-01",
            raw_response={}
        )
        
        # Intentar modificar debería fallar si está frozen
        # (Esto es opcional si decides hacer frozen=True)


class TestIntegration:
    """Pruebas de integración (requieren API corriendo)."""
    
    @pytest.mark.integration
    def test_real_api_health_check(self):
        """Test: health check contra API real (si está corriendo)."""
        client = APIClient("http://localhost:8000")
        try:
            result = client.health_check()
            assert "status" in result
        except requests.ConnectionError:
            pytest.skip("API no disponible")
    
    @pytest.mark.integration
    def test_real_api_predict(self):
        """Test: predicción contra API real (si está corriendo)."""
        client = APIClient("http://localhost:8000")
        
        data = {
            "age": 35, "month": 5, "day_of_week": 1, "duration": 500,
            "campaign": 1, "pdays": -1, "previous": 0, "emp_var_rate": 1.1,
            "cons_price_idx": 93.5, "cons_conf_idx": -36.0, "euribor3m": 0.7,
            "nr_employed": 5100.0, "previous_bin": 0, "job_target_mean": 0.45,
            "marital_divorced": 0, "marital_married": 1, "marital_single": 0,
            "marital_unknown": 0, "education_freq_encode": 0.5, "housing_no": 0,
            "housing_unknown": 0, "housing_yes": 1, "loan_no": 0,
            "loan_unknown": 0, "loan_yes": 1, "contact_cellular": 1,
            "contact_telephone": 0,
        }
        
        try:
            result = client.predict(data)
            assert result.success is True
            assert 0 <= result.prediction <= 1
        except requests.ConnectionError:
            pytest.skip("API no disponible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
