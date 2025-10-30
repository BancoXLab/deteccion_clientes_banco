# Servidor mínimo para visualizar scr/ops/alerts.log en /alerts
from flask import Flask, Response
from pathlib import Path

ALERTS = Path("scr/ops/alerts.log")
app = Flask(__name__)

@app.route("/alerts")
def alerts():
    if not ALERTS.exists():
        return Response("No alerts\n", mimetype="text/plain")
    return Response(ALERTS.read_text(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)