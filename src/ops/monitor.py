# Simple monitor doméstico: lee /tmp/app.log y data/sample.csv, evalúa reglas y escribe alerts.log
import re
import json
from statistics import mean
from pathlib import Path
import pandas as pd
import time

LOG_PATH = Path("/tmp/app.log")
ALERTS = Path("scr/ops/alerts.log")
DRIFT_BASELINE = Path("scr/ops/drift_baseline.json")
SAMPLE = Path("data/samples/sample_data.csv")

def parse_logs():
    if not LOG_PATH.exists():
        return []
    lines = LOG_PATH.read_text().splitlines()
    entries = []
    for ln in lines:
        # ejemplo: "2025-10-30 12:00:00,000 INFO Processor ... latency=123 status=200"
        m_lat = re.search(r"latency=(\d+\.?\d*)", ln)
        m_st = re.search(r"status=(\d{3})", ln)
        level = "INFO"
        if "ERROR" in ln:
            level = "ERROR"
        entries.append({
            "line": ln,
            "latency": float(m_lat.group(1)) if m_lat else None,
            "status": int(m_st.group(1)) if m_st else None,
            "level": level
        })
    return entries

def compute_error_rate(entries, window=None):
    total = sum(1 for e in entries if e.get("status") is not None)
    errors = sum(1 for e in entries if e.get("status") and e["status"] >= 500)
    if total == 0:
        return 0.0
    return errors / total * 100.0

def compute_p95_latency(entries):
    lat = [e["latency"] for e in entries if e["latency"] is not None]
    if not lat:
        return 0.0
    lat_sorted = sorted(lat)
    idx = int(0.95 * len(lat_sorted)) - 1
    idx = max(0, min(idx, len(lat_sorted)-1))
    return lat_sorted[idx]

def compute_drift():
    if not SAMPLE.exists() or not DRIFT_BASELINE.exists():
        return 0.0
    df = pd.read_csv(SAMPLE)
    if "saldo" not in df.columns:
        return 0.0
    current_mean = df["saldo"].astype(float).mean()
    base = json.loads(DRIFT_BASELINE.read_text())
    base_mean = base.get("saldo_mean", current_mean)
    if base_mean == 0:
        return 0.0
    rel_change = abs(current_mean - base_mean) / base_mean * 100.0
    return rel_change

def emit_alert(level, metric, value, threshold, details=""):
    ALERTS.parent.mkdir(parents=True, exist_ok=True)
    line = f"{level} | {metric} | value={value} | threshold={threshold} | {details}\n"
    ALERTS.write_text(ALERTS.read_text() + line if ALERTS.exists() else line, append=False)

def run_checks():
    entries = parse_logs()
    err_rate = compute_error_rate(entries)
    p95 = compute_p95_latency(entries)
    drift = compute_drift()

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
    print("Starting monitor service...")
    while True:
        run_checks()
        print("Checks executed. Alerts written to scr/ops/alerts.log (if any).")
        time.sleep(60)  # espera 60 segundos antes de volver a ejecutar