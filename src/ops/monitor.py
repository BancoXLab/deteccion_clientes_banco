"""Monitor ligero: parsea logs, calcula métricas y emite alertas.

Lee `/tmp/app.log` (LOG_PATH) y `data/samples/sample_data.csv` (SAMPLE).
Persiste métricas/alertas usando `src.ops.db` y expone métricas Prometheus opcionalmente.
"""

import os
import re
import json
import time
import logging
from pathlib import Path
from typing import List, Dict

import pandas as pd

from src.ops.logging_config import configure_logging
from src.ops.db import init_db, save_metric, save_alert
from src.ops.notify import notify_slack

configure_logging()
logger = logging.getLogger(__name__)

LOG_PATH = Path("/tmp/app.log")
ALERTS = Path("src/ops/alerts.log")
DRIFT_BASELINE = Path("src/ops/drift_baseline.json")
SAMPLE = Path("data/samples/sample_data.csv")

# Prometheus client (opcional)
try:
    from prometheus_client import start_http_server, Gauge, Counter
    HAVE_PROM = True
except Exception:
    HAVE_PROM = False

# Inicializar métricas Prometheus o stubs
PROM_PORT = int(os.getenv("MONITOR_PROM_PORT", "8002"))
if HAVE_PROM:
    start_http_server(PROM_PORT)
    P95_LAT = Gauge('monitor_p95_latency', 'P95 latency ms')
    ERROR_RATE = Gauge('monitor_error_rate', 'Error rate percent')
    ALERTS_COUNTER = Counter('monitor_alerts_total', 'Total alerts emitted', ['level'])
else:
    class _NoOp:
        def set(self, *a, **k):
            return None

        def inc(self, *a, **k):
            return None

    P95_LAT = _NoOp()
    ERROR_RATE = _NoOp()
    ALERTS_COUNTER = _NoOp()


def parse_logs() -> List[Dict]:
    """Parsea `LOG_PATH` y devuelve una lista de entradas con keys: line, latency, status, level."""
    if not LOG_PATH.exists():
        logger.debug("Log file %s no existe. Devuelvo lista vacía.", LOG_PATH)
        return []

    lines = LOG_PATH.read_text().splitlines()
    entries = []
    for ln in lines:
        m_lat = re.search(r"latency=(\d+\.?\d*)", ln)
        m_st = re.search(r"status=(\d{3})", ln)
        level = "INFO"
        if "ERROR" in ln or "Exception" in ln:
            level = "ERROR"
        entries.append({
            "line": ln,
            "latency": float(m_lat.group(1)) if m_lat else None,
            "status": int(m_st.group(1)) if m_st else None,
            "level": level,
        })
    return entries


def compute_error_rate(entries: List[Dict]) -> float:
    total = sum(1 for e in entries if e.get("status") is not None)
    errors = sum(1 for e in entries if e.get("status") and e["status"] >= 500)
    if total == 0:
        return 0.0
    return errors / total * 100.0


def compute_p95_latency(entries: List[Dict]) -> float:
    lat = [e["latency"] for e in entries if e["latency"] is not None]
    if not lat:
        return 0.0
    lat_sorted = sorted(lat)
    idx = int(0.95 * len(lat_sorted)) - 1
    idx = max(0, min(idx, len(lat_sorted) - 1))
    return lat_sorted[idx]


def compute_drift() -> float:
    if not SAMPLE.exists() or not DRIFT_BASELINE.exists():
        return 0.0
    try:
        df = pd.read_csv(SAMPLE)
    except Exception:
        logger.exception("Error leyendo SAMPLE para drift")
        return 0.0
    if "saldo" not in df.columns:
        return 0.0
    current_mean = df["saldo"].astype(float).mean()
    try:
        base = json.loads(DRIFT_BASELINE.read_text())
    except Exception:
        logger.exception("Error leyendo DRIFT_BASELINE")
        return 0.0
    base_mean = base.get("saldo_mean", current_mean)
    if base_mean == 0:
        return 0.0
    rel_change = abs(current_mean - base_mean) / base_mean * 100.0
    return rel_change


def publish_metrics(p95: float, error_rate: float) -> None:
    try:
        P95_LAT.set(p95)
        ERROR_RATE.set(error_rate)
        save_metric('p95_latency', float(p95))
        save_metric('error_rate', float(error_rate))
    except Exception:
        logger.exception("Failed to publish metrics to DB or Prometheus")


def emit_alert(level: str, metric: str, value, threshold, details: str = "") -> None:
    try:
        ALERTS.parent.mkdir(parents=True, exist_ok=True)
        line = f"{level} | {metric} | value={value} | threshold={threshold} | {details}\n"
        # Append to alerts log
        if ALERTS.exists():
            ALERTS.write_text(ALERTS.read_text() + line)
        else:
            ALERTS.write_text(line)
        # Persist in DB
        save_alert(level, metric, value, threshold, details)
        # Prometheus counter
        try:
            ALERTS_COUNTER.labels(level=level).inc()
        except Exception:
            try:
                ALERTS_COUNTER.inc()
            except Exception:
                pass
        # Notify on critical
        if level.upper() in ("CRITICAL", "ERROR"):
            try:
                notify_slack(f"ALERT {level}: {metric}={value} threshold={threshold} {details}")
            except Exception:
                logger.exception("Failed to send Slack notification")
    except Exception:
        logger.exception("Failed to emit_alert")


def run_checks() -> None:
    entries = parse_logs()
    err_rate = compute_error_rate(entries)
    p95 = compute_p95_latency(entries)
    drift = compute_drift()

    # Publish metrics
    publish_metrics(p95, err_rate)

    # Rules / SLOs from RUNBOOK
    if err_rate >= 1.0:
        emit_alert("CRITICAL", "error_rate_5m", err_rate, ">=1%")
    elif err_rate >= 0.5:
        emit_alert("WARN", "error_rate_5m", err_rate, ">=0.5%")

    if p95 >= 500:
        emit_alert("WARN", "latency_p95_ms", p95, ">=500ms")

    if drift >= 10.0:
        emit_alert("WARN", "model_drift_percent", drift, ">=10%")


if __name__ == "__main__":
    logger.info("Starting monitor service...")
    try:
        init_db()
    except Exception:
        logger.exception("DB init failed (continuing)")
    while True:
        try:
            run_checks()
            logger.info("Checks executed. Alerts written to %s (if any).", ALERTS)
        except Exception:
            logger.exception("Error running checks")
        time.sleep(60)