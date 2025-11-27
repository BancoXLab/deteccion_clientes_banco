# Servidor mínimo para visualizar scr/ops/alerts.log en /alerts
from flask import Flask, Response, request, abort
from pathlib import Path
import os
import logging
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    HAVE_PROM = True
except Exception:
    HAVE_PROM = False

from src.ops.logging_config import configure_logging
from src.ops.db import init_db, save_alert
from src.ops.notify import notify_slack

configure_logging()
logger = logging.getLogger(__name__)

ALERTS = Path("scr/ops/alerts.log")
app = Flask(__name__)

# minimal API key auth
API_KEY = os.getenv("ALERTS_API_KEY")

def require_api_key(fn):
    def wrapper(*args, **kwargs):
        if not API_KEY:
            return fn(*args, **kwargs)
        key = request.headers.get("X-Api-Key") or request.headers.get("Authorization")
        if key and key.startswith("Bearer "):
            key = key.split(None, 1)[1]
        if key != API_KEY:
            abort(401)
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


@app.route("/")
def index():
    return "Alert service is running", 200


@app.route("/alerts", methods=["GET"])
@require_api_key
def alerts():
    # read from DB if available, else fallback to log file
    try:
        init_db()
    except Exception:
        logger.debug("DB init failed or not configured; falling back to file read")
    if ALERTS.exists():
        return Response(ALERTS.read_text(), mimetype="text/plain")
    return Response("No alerts\n", mimetype="text/plain")


@app.route("/alerts", methods=["POST"])
@require_api_key
def create_alert():
    payload = request.get_json(force=True)
    level = payload.get("level", "INFO")
    message = payload.get("message", "")
    extra = payload.get("extra")
    # persist
    try:
        init_db()
        a = save_alert(level=level, message=message, extra=str(extra) if extra else None)
        logger.info("Saved alert %s", a.id)
    except Exception as e:
        logger.exception("Failed to save alert: %s", e)
    # also write to file for backward compatibility
    try:
        ALERTS.parent.mkdir(parents=True, exist_ok=True)
        with open(ALERTS, "a") as f:
            f.write(f"{level}: {message}\n")
    except Exception:
        logger.exception("Failed to append to alerts.log")

    # notify critical
    if level.upper() in ("CRITICAL", "ERROR"):
        notify_slack(f"ALERT [{level}]: {message}")

    return {"status": "ok"}, 201


@app.route('/metrics')
def metrics():
    if not HAVE_PROM:
        return Response("Prometheus client not installed", status=501, mimetype="text/plain")
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    # ensure DB tables exist if configured
    try:
        init_db()
    except Exception:
        logger.debug("init_db failed at startup; continuing")
    app.run(host="0.0.0.0", port=int(os.getenv("ALERT_SERVER_PORT", 9000)))