import pytest
import src.app.routes.general_routes as gr

def test_log_prediction_to_prefect(monkeypatch):
    # Patch get_run_logger to a fake logger
    class FakeLogger:
        def info(self, msg):
            pass
    monkeypatch.setattr(gr, "get_run_logger", lambda: FakeLogger())
    # Should not raise
    gr.log_prediction_to_prefect({"foo": 1}, 0.5)

def test_inference_flow(monkeypatch):
    called = {}
    def fake_log(input_data, prediction):
        called["input"] = input_data
        called["prediction"] = prediction
    monkeypatch.setattr(gr, "log_prediction_to_prefect", fake_log)
    gr.inference_flow({"bar": 2}, 1.0)
    assert called["input"] == {"bar": 2}
    assert called["prediction"] == 1.0