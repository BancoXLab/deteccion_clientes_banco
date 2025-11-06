# tests/test_app_api.py
import os
import sys
import pytest
from fastapi.testclient import TestClient
import numpy as np

# Asegurar que scr está en el PYTHONPATH
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, repo_root)

from scr.app.main import app

client = TestClient(app)

# 1. Tests de API Endpoints
def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "model_version" in response.json()

def test_ping_endpoint():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}

def test_info_endpoint():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "model_version" in data
    assert "python" in data

# 2. Tests de Predicción
@pytest.fixture
def valid_client_data():
    return {
        "age": 41.0,
        "month": 5,
        "day_of_week": 2,
        "duration": 261.0,
        "campaign": 1.0,
        "pdays": -1.0,
        "previous": 0.0,
        "emp_var_rate": -1.8,
        "cons_price_idx": 92.893,
        "cons_conf_idx": -46.2,
        "euribor3m": 1.266,
        "nr_employed": 5099.1,
        "previous_bin": 0,
        "job_target_mean": 0.15,
        "marital_divorced": 0,
        "marital_married": 1,
        "marital_single": 0,
        "marital_unknown": 0,
        "education_freq_encode": 0.25,
        "housing_no": 0,
        "housing_unknown": 0,
        "housing_yes": 1,
        "loan_no": 1,
        "loan_unknown": 0,
        "loan_yes": 0,
        "contact_cellular": 1,
        "contact_telephone": 0
    }

def test_predict_endpoint_valid_data(valid_client_data):
    response = client.post("/predict", json=valid_client_data)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "model_version" in data
    assert isinstance(data["prediction"], int)
    assert data["prediction"] in [0, 1]

# 3. Tests de Validación de Datos
@pytest.mark.parametrize("field,invalid_value", [
    ("age", "invalid"),  # tipo incorrecto
    ("month", 13),      # valor fuera de rango
    ("day_of_week", 8), # valor fuera de rango
])
def test_predict_endpoint_invalid_data(valid_client_data, field, invalid_value):
    invalid_data = valid_client_data.copy()
    invalid_data[field] = invalid_value
    response = client.post("/predict", json=invalid_data)
    assert response.status_code in [422, 500]

def test_predict_endpoint_missing_field(valid_client_data):
    invalid_data = valid_client_data.copy()
    del invalid_data["age"]
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422

# 4. Tests de Health/Readiness
def test_healthz_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    if "model" in data:
        assert "status" in data["model"]

def test_readyz_endpoint():
    response = client.get("/readyz")
    assert response.status_code in [200, 503]
    data = response.json()
    if response.status_code == 200:
        assert data["ready"] is True
    else:
        assert "ready" in data
        assert "reason" in data

# 5. Tests de Manejo de Errores
def test_predict_endpoint_model_error(valid_client_data):
    # Datos que deberían causar error en el modelo
    # Valores que están dentro del rango permitido pero causarán problemas al modelo
    bad_data = dict(valid_client_data)
    bad_data['age'] = -1  # edad negativa, debería ser rechazada por Pydantic
    response = client.post("/predict", json=bad_data)
    assert response.status_code == 422  # Unprocessable Entity
    assert "age" in response.json()["detail"][0]["loc"]  # el error menciona el campo age