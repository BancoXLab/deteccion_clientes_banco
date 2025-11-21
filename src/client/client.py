import requests
from typing import Any, Dict, Optional
from dataclasses import dataclass
import os

@dataclass
class PredictionResponse:
    """Respuesta de predicción de la API."""
    success: bool
    prediction: float
    prediction_label: str
    model_version: str
    timestamp: str
    raw_response: Dict[str, Any]


class APIClient:
    """Cliente HTTP para consumir la API de Banco X.
    
    Ejemplo de uso:
        client = APIClient("http://localhost:8000")
        
        # Con un diccionario de datos
        result = client.predict({
            "age": 35, "month": 5, "day_of_week": 1, "duration": 500,
            "campaign": 1, "pdays": -1, "previous": 0, "emp_var_rate": 1.1,
            "cons_price_idx": 93.5, "cons_conf_idx": -36.0, "euribor3m": 0.7,
            "nr_employed": 5100.0, "previous_bin": 0, "job_target_mean": 0.45,
            "marital_divorced": 0, "marital_married": 1, "marital_single": 0,
            "marital_unknown": 0, "education_freq_encode": 0.5, "housing_no": 0,
            "housing_unknown": 0, "housing_yes": 1, "loan_no": 0,
            "loan_unknown": 0, "loan_yes": 1, "contact_cellular": 1, "contact_telephone": 0
        })
        print(result)
    """
    
    def __init__(self, base_url: str = None):
        env_url = os.getenv("BANCO_X_API_URL")

    if base_url:
        self.base = base_url.rstrip("/")
    elif env_url:
        self.base = env_url.rstrip("/")
    else:
        self.base = "http://fastapi:8000"
    
    def predict(self, payload: Dict[str, Any], timeout: int = 10) -> PredictionResponse:
        """
        Realiza una predicción usando la API.
        
        Args:
            payload: Diccionario con los datos del cliente. Debe contener todos los 27 campos requeridos.
            timeout: Timeout en segundos para la petición (default: 10s)
            
        Returns:
            PredictionResponse: Objeto con la respuesta de la API
            
        Raises:
            requests.HTTPError: Si la respuesta tiene un código de error HTTP
            ValueError: Si el payload no contiene los campos requeridos
            requests.RequestException: Si hay un error de conexión
        """
        url = f"{self.base}/predict"
        
        try:
            # The API expects a list (batch) of client dicts. Accept a single
            # dict for convenience and wrap it into a list when needed.
            to_send = payload if isinstance(payload, list) else [payload]
            resp = requests.post(url, json=to_send, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()

            # Procesar respuesta exitosa
            if data.get("success", True):  # success puede estar ausente en algunas versiones
                return PredictionResponse(
                    success=True,
                    prediction=float(data.get("prediction", 0)),
                    prediction_label=data.get("prediction_label", ""),
                    model_version=data.get("model_version", ""),
                    timestamp=data.get("timestamp", ""),
                    raw_response=data
                )
            else:
                raise ValueError(f"API error: {data.get('error', 'Unknown error')}")

        except requests.HTTPError as e:
            # Manejar errores HTTP específicos
            try:
                # Si hay response, intentar parsear el JSON
                if e.response is not None:
                    error_detail = e.response.json()
                    raise ValueError(
                        f"API HTTP Error {e.response.status_code}: {error_detail.get('error', str(e))}"
                    ) from e
                else:
                    # Si no hay response (ej: en mocks), usar el mensaje del error
                    raise ValueError(f"API HTTP Error: {str(e)}") from e
            except (AttributeError, requests.JSONDecodeError):
                # AttributeError si e.response es None, JSONDecodeError si no es JSON
                raise ValueError(f"API HTTP Error: {str(e)}") from e
    
    def health_check(self, timeout: int = 5) -> Dict[str, Any]:
        """
        Verifica que la API esté saludable.
        
        Args:
            timeout: Timeout en segundos (default: 5s)
            
        Returns:
            Diccionario con el estado de salud
        """
        url = f"{self.base}/healthz"
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    
    def get_info(self, timeout: int = 5) -> Dict[str, Any]:
        """
        Obtiene información de la API.
        
        Args:
            timeout: Timeout en segundos (default: 5s)
            
        Returns:
            Diccionario con información del servicio
        """
        url = f"{self.base}/info"
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()


if __name__ == "__main__":
    # Ejemplo de uso
    client = APIClient()
    
    # Datos de ejemplo completos para una predicción
    sample_data = {
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
    
    try:
        # Verificar que la API está disponible
        print("📋 Verificando salud de la API...")
        health = client.health_check()
        print(f"✅ API saludable: {health.get('status')}\n")
        
        # Obtener información
        print("📊 Información del servicio:")
        info = client.get_info()
        print(f"  Versión: {info.get('model_version')}\n")
        
        # Realizar predicción
        print("🔮 Realizando predicción...")
        result = client.predict(sample_data)
        print(f"✅ Predicción exitosa:")
        print(f"  Resultado: {result.prediction_label}")
        print(f"  Score: {result.prediction:.4f}")
        print(f"  Versión del modelo: {result.model_version}")
        print(f"  Timestamp: {result.timestamp}")
        
    except requests.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar a la API en {client.base}")
    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")