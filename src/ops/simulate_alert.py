# Simula condiciones que disparan alertas: errores, latencia alta y drift en 'saldo'
import time
import csv
from pathlib import Path
import random
import subprocess

LOG_PATH = Path("/tmp/app.log")
SAMPLE = Path("data/samples/sample_data.csv")
BASELINE = Path("scr/ops/drift_baseline.json")

def append_log(line):
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

def generate_error_logs(n=20):
    # mezcla de status 200 y 500 con latencias
    for i in range(n):
        status = 500 if i % 3 == 0 else 200
        latency = random.uniform(600, 1200) if status >= 500 else random.uniform(50, 200)
        level = "ERROR" if status >= 500 else "INFO"
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        append_log(f"{ts} {level} Service request id={i} latency={int(latency)} status={status}")
    print(f"Wrote {n} log lines to {LOG_PATH}")

def generate_drift_dataset(base_mean=100.0, drift_mean=130.0, n=200):
    Path(SAMPLE.parent).mkdir(parents=True, exist_ok=True)
    # create a dataset with shifted `saldo`
    with open(SAMPLE, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["id","name","saldo"])
        writer.writeheader()
        for i in range(n):
            val = random.gauss(drift_mean, 10.0)
            writer.writerow({"id": i, "name": f"User {i}", "saldo": round(val,2)})
    # write baseline if missing
    if not BASELINE.exists():
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text('{"saldo_mean": %s}' % base_mean)
    print(f"Generated sample dataset at {SAMPLE} and baseline at {BASELINE}")

def run_monitor():
    subprocess.run(["python", "scr/ops/monitor.py"], check=False)

if __name__ == "__main__":
    generate_error_logs(30)
    generate_drift_dataset(base_mean=100.0, drift_mean=130.0, n=300)
    run_monitor()
    print("Simulation complete. Re-run monitor or start alert server to view alerts.")