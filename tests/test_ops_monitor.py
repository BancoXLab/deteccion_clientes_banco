import os
import json
import importlib
from pathlib import Path

import src.ops.monitor as monitor


def test_parse_logs_and_metrics(tmp_path, monkeypatch):
    # Prepare a temporary log file and patch LOG_PATH
    log_file = tmp_path / "app.log"
    lines = [
        "INFO latency=120 status=200 request=/foo",
        "ERROR latency=600 status=500 Exception: boom",
        "INFO latency=300 status=200 request=/bar",
    ]
    log_file.write_text("\n".join(lines))
    monkeypatch.setattr(monitor, "LOG_PATH", log_file)

    entries = monitor.parse_logs()
    assert isinstance(entries, list)
    assert len(entries) == 3
    assert entries[1]["level"] == "ERROR"

    # compute error rate
    err = monitor.compute_error_rate(entries)
    assert err == (1 / 3) * 100.0

    # compute p95 latency on small sample
    p95 = monitor.compute_p95_latency(entries)
    assert isinstance(p95, float)


def test_publish_metrics_and_emit_alert(monkeypatch, tmp_path):
    calls = {"metrics": [], "alerts": [], "notified": []}

    def fake_save_metric(name, value):
        calls["metrics"].append((name, float(value)))

    def fake_save_alert(*args, **kwargs):
        calls["alerts"].append((args, kwargs))

    def fake_notify(msg):
        calls["notified"].append(msg)

    # Patch functions
    monkeypatch.setattr(monitor, "save_metric", fake_save_metric)
    monkeypatch.setattr(monitor, "save_alert", fake_save_alert)
    monkeypatch.setattr(monitor, "notify_slack", fake_notify)

    # Publish metrics should call save_metric twice
    monitor.publish_metrics(123.4, 0.7)
    assert any(m[0] == "p95_latency" for m in calls["metrics"]) 

    # Patch ALERTS file path to tmp and emit a CRITICAL alert
    monkeypatch.setattr(monitor, "ALERTS", tmp_path / "alerts.log")
    monitor.emit_alert("CRITICAL", "latency", 999, ">=500", "detail")
    # emit_alert should attempt to persist (we captured via fake_save_alert)
    assert len(calls["alerts"]) >= 1
    # for CRITICAL it should notify
    assert len(calls["notified"]) >= 1


def test_compute_drift_no_sample(tmp_path, monkeypatch):
    # Ensure function returns 0.0 when sample or baseline missing
    monkeypatch.setattr(monitor, "SAMPLE", tmp_path / "nope.csv")
    monkeypatch.setattr(monitor, "DRIFT_BASELINE", tmp_path / "nope.json")
    drift = monitor.compute_drift()
    assert drift == 0.0
