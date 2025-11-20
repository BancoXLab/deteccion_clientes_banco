import pytest
from flask import Flask
import src.ops.alert_server as alert_server

def test_index_route():
    app = alert_server.app
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Alert service is running" in resp.data

def test_alerts_get(monkeypatch, tmp_path):
    app = alert_server.app
    client = app.test_client()
    # Patch ALERTS path to a temp file
    test_alerts = tmp_path / "alerts.log"
    test_alerts.write_text("WARN: test alert\n")
    monkeypatch.setattr(alert_server, "ALERTS", test_alerts)
    resp = client.get("/alerts")
    assert resp.status_code == 200
    assert b"test alert" in resp.data

def test_alerts_post(monkeypatch, tmp_path):
    app = alert_server.app
    client = app.test_client()
    # Patch ALERTS path to a temp file
    test_alerts = tmp_path / "alerts.log"
    monkeypatch.setattr(alert_server, "ALERTS", test_alerts)
    # Patch notify_slack to avoid real call
    monkeypatch.setattr(alert_server, "notify_slack", lambda msg: True)
    # Patch save_alert to avoid DB
    monkeypatch.setattr(alert_server, "save_alert", lambda **kwargs: type("A", (), {"id": 1})())
    payload = {"level": "CRITICAL", "message": "test critical", "extra": "foo"}
    resp = client.post("/alerts", json=payload)
    assert resp.status_code == 201
    assert resp.json["status"] == "ok"
    # Should write to file
    assert "CRITICAL: test critical" in test_alerts.read_text()