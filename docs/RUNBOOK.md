# RUNBOOK — deteccion_clientes_banco

## 1. Propósito
Runbook mínimo para operación: despliegue, monitorización, SLOs, alertas y procedimiento de incidentes.

## 2. Despliegue (paso a paso)
1. Clonar repo: `git clone ... && cd /workspaces/deteccion_clientes_banco`
2. Crear entorno: `python -m venv .venv && source .venv/bin/activate`
3. Instalar deps: `python -m pip install --upgrade pip && pip install -r requirements.txt || pip install flask pandas numpy`
4. Levantar la API (si existe): `uvicorn scr.app.main:app --host 0.0.0.0 --port 8000`
5. Herramientas operativas: scripts en `scr/ops/`

## 3. Métricas y SLOs (T9)
Definimos 3 métricas (técnica / negocio / drift) con SLOs y umbrales.

- M1 — Disponibilidad / Error rate (técnica)
  - Descripción: % de requests con status >=500 en ventana 5m.
  - SLO: error_rate_5m < 1%
  - Alerta WARN: error_rate_5m >= 0.5%
  - Alerta CRÍTICA: error_rate_5m >= 1%

- M2 — Latencia (técnica / negocio)
  - Descripción: p95 de latencia de predicción.
  - SLO: p95 < 500 ms
  - Alerta: p95 >= 500 ms

- M3 — Model drift (negocio)
  - Descripción: cambio en media de la característica `saldo` respecto baseline.
  - SLO: cambio relativo < 10%
  - Alerta: cambio relativo >= 10%

## 4. Dónde recoger métricas
- Logs de aplicación: `/tmp/app.log` (formato: timestamp LEVEL name message ...)
- Datos de entrada muestreados: `data/sample.csv`
- Scripts de monitor: `scr/ops/monitor.py` (comprobaciones y reglas)

## 5. Alertas (canales y responsables)
- Canal primario: email del equipo (ops@example.com) / Slack #ops (configurable)
- Fallback: webhook / archivo `scr/ops/alerts.log`
- Responsable inicial: On-call dev del equipo (persona en rota)

## 6. Procedimiento de incidentes (triage → rollback)
1. Triage:
   - Identificar alerta (logs, monitor scripts, UI)
   - Clasificar: degradación, outage, seguridad
2. Contención:
   - Si es regresión de despliegue: revertir a la última imagen estable (docker-compose down && docker-compose up --no-deps --build api)
3. Diagnóstico:
   - Revisar `/tmp/app.log`, `scr/ops/alerts.log` y métricas p95/error_rate
4. Resolución:
   - Aplicar fix, tests rápidos, desplegar
5. Postmortem y actualizar RUNBOOK

## 7. Cómo simular 1 alerta (evidencia)
1. Ejecutar el script de simulación:
   - `python scr/ops/simulate_alert.py`
   - Esto generará logs de error y un dataset con drift, y ejecutará el monitor para escribir `scr/ops/alerts.log`
2. Levantar servidor de alertas para screenshot:
   - `python scr/ops/alert_server.py`
   - Abrir en host: `$BROWSER http://localhost:9000` y tomar screenshot del alerta generada (`alerts.log`)

## 8. Ubicación de evidencias
- docs/alerts_screenshots/alert1.png
- scr/ops/alerts.log
