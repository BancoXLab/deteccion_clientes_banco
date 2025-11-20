# tests/test_app_prefect.py
import pytest
from prefect.testing.utilities import prefect_test_harness
from src.app.main_orq import health_check_flow, check_model_status, get_system_metrics

@pytest.fixture(autouse=True)
def prefect_test_fixture():
    with prefect_test_harness():
        yield

def test_health_check_flow():
    health_status = health_check_flow()
    assert isinstance(health_status, dict)
    assert "status" in health_status
    assert "model" in health_status
    assert "system" in health_status
    assert "timestamp" in health_status

def test_check_model_status():
    status = check_model_status()
    assert isinstance(status, dict)
    assert "status" in status
    assert status["status"] in ["ok", "error"]

def test_get_system_metrics():
    metrics = get_system_metrics()
    assert isinstance(metrics, dict)
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics