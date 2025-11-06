# RUNBOOK — BancoX Model API (Staging)

Este runbook describe procedimientos operativos, playbooks de incidentes y tareas de mantenimiento para el servicio de inferencia que acompaña el proyecto de Predicción de Suscripción a Depósitos Bancarios (BancoX). Cubre el entorno de staging y los artefactos que se generan en el repositorio (notebooks, modelos, MLflow).

---

## 1) Contactos y alcance
- Dueño técnico: Facundo Casas, Javier Balda, Juan Caracoix (facundocasas@uca.edu.ar, javierbalda@uca.edu.ar, juancaracoix@uca.edu.ar)  
- Equipo de soporte / Incidentes: BancoXLab (canal de Slack/Teams: #staging-ml o el canal interno de soporte)  
- Horario operativo: Jueves 17:00–21:00 (UTC-3). Fuera de horario: soporte asíncrono / on-call según rotación.  
- Alcance: Este runbook cubre el entorno de staging de la API de inferencia y la operación local (endpoints `/healthz`, `/predict`, `/batch`). No contiene procedimientos específicos de despliegue a producción.

---

## 2) Endpoints y checks rápidos
- Health: GET /healthz  
  - Respuesta esperada 200:
    {
      "ok": true,
      "env": "staging",
      "version": "<commit-sha-or-model-version>"
    }

- Inferencia (single): POST /predict  
  - Input: JSON con features del cliente (ej. age, job, marital, education, balance, housing, loan, contact, campaign, pdays, previous, poutcome).  
  - Respuesta esperada 200:
    {
      "y_pred": "yes"|"no",
      "probability": float,
      "model_version": "<tag-or-run_id>"
    }

- Inferencia (batch): POST /batch  
  - Input: multipart/form-data con file=@archivo.csv o JSON con lista de instancias.  
  - Respuesta: CSV con columnas originales + `y_pred` + `probability`, o JSON con enlace al artefacto.

- Métricas (si expuesto): GET /metrics → contadores de requests, errores y latencias (Prometheus format si aplica).

Comandos de verificación:
```bash
# Health
curl -s http://<HOST>:8000/healthz | jq

# Predicción individual (ajustar schema)
curl -s -X POST "http://<HOST>:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"age":35,"job":"technician","marital":"married","education":"tertiary","balance":1500,"housing":"yes","loan":"no","contact":"cellular","campaign":1,"pdays":999,"previous":0,"poutcome":"nonexistent"}' | jq

# Batch (CSV)
curl -s -X POST "http://<HOST>:8000/batch" -F "file=@clientes_para_predecir.csv"
```

---

## 3) Configuración (env vars y flags)
Variables de entorno clave (usar en Docker / orquestador):
- APP_ENV=staging|production
- APP_USE_MOCK=true|false    # fallback que devuelve respuestas dummy
- MODEL_PATH=/app/models/model.joblib    # ruta por defecto dentro del contenedor
- MLFLOW_TRACKING_URI=http://<mlflow-server>:5000  # opcional para tracking remoto
- LOG_LEVEL=INFO|DEBUG
- PORT=8000

Versionado:
- La /healthz debe exponer commit SHA o model_version. Mantener en `models/` un archivo `version.txt` o registrar el run_id en MLflow para trazabilidad.

---

## 4) Start / Stop / Logs

Local (desarrollo):
```bash
# Ejecutar la API con uvicorn (ajustar import si la app está en otro módulo)
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

Docker:
```bash
# Construir imagen
docker build -t banco-x-api .

# Ejecutar (staging)
docker rm -f banco-x-api || true
docker run -d --name banco-x-api -p 8000:8000 \
  -e APP_ENV=staging \
  -e APP_USE_MOCK=false \
  -e MODEL_PATH=/app/models/model.joblib \
  banco-x-api:latest

# Ver logs
docker logs -f banco-x-api
```

Kubernetes (si se usa):
```bash
kubectl get pods -n staging -l app=banco-x-api
kubectl logs -f deploy/banco-x-api -n staging
```

Logs: la app escribe en stdout; los logs recomendados incluyen timestamp, request_id, endpoint, latency, model_version y error stacktrace en caso de fallo.

---

## 5) Playbooks de incidentes (paso a paso)

### 5.1 Healthz DOWN (3 fallos seguidos)
1. Comprobar si el proceso o contenedor está corriendo:
   - docker ps | grep banco-x-api
   - ps aux | grep uvicorn
2. Revisar logs (últimas 200 líneas):
   - docker logs --tail 200 banco-x-api
3. Verificar existencia del modelo:
   - docker exec -it banco-x-api ls -la /app/models
   - docker exec -it banco-x-api cat /app/models/version.txt || true
4. Reiniciar servicio:
   - docker restart banco-x-api
5. Si persiste, habilitar fallback:
   - docker rm -f banco-x-api
   - docker run -d --name banco-x-api -p 8000:8000 -e APP_USE_MOCK=true banco-x-api:latest
6. Registrar incidente (resumen, logs relevantes) y abrir ticket.

Criterio de éxito: `/healthz` == 200 y 2 requests `/predict` exitosos.

---

### 5.2 Latencia p95 alta (> umbral por 5 min)
1. Capturar requests lentos (ids, payloads) desde logs o APM.
2. Monitor CPU/RAM del nodo / contenedor:
   - docker stats banco-x-api
   - kubectl top pods -n staging
3. Revisar si transformaciones en inferencia (PCA, codificaciones) agregan latencia; revisar código en `mvp_para_frontend.py` y transformadores.
4. Mitigaciones rápidas:
   - APP_USE_MOCK=true temporal.
   - Aumentar réplicas.
   - Limitar tamaño de payload (si procede).
5. Remediación: optimizar pipeline de inferencia, precalcular transformaciones, o usar un endpoint de batch para cargas grandes.

Criterio de éxito: p95 vuelve por debajo del umbral definido durante 10–15 min.

---

### 5.3 Errores 5xx elevados (>1% por 10 min)
1. Filtrar logs por 5xx y agrupar por endpoint/stacktrace.
2. Revisar si son causados por input malformado (convertir a 4xx) o por fallo interno.
3. Reproducir el error localmente con el payload que falla.
4. Si es bug del servicio, implementar hotfix, construir nueva imagen y desplegar. Si proviene de dependencia externa, aplicar retry/backoff o fallback.
5. Mantener control de cambios y despliegue seguro (smoke tests antes de declarar recuperado).

Criterio de éxito: error rate < 1% por 10 min.

---

## 6) Rollback / Fallback
- Fallback rápido: poner APP_USE_MOCK=true y reiniciar contenedor.
- Rollback a imagen previa:
```bash
# listar imágenes
docker images | grep banco-x-api

# ejecutar imagen anterior
docker run -d --name banco-x-api -p 8000:8000 banco-x-api:<previous-tag>
```
- Si se usa MLflow model registry: recuperar versión anterior del modelo y apuntar MODEL_PATH a esa versión, o descargar y reemplazar model.joblib en `models/`.

Verificación: correr smoke tests y validación de contrato.

---

## 7) Verificación post-incidente
- Ejecutar pruebas smoke:
```bash
pytest -q -m smoke
```
- Comprobar endpoints:
```bash
curl -s http://localhost:8000/healthz | jq
curl -s -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"age":35,...}' | jq
```
- Revisar métricas y dashboards (MLflow, Prometheus/Grafana si existen).
- Documentar: tiempo de recuperación, causa raíz, acciones tomadas y acciones preventivas.

---

## 8) SLOs declarados (staging)
- Disponibilidad: >= 98% semanal (`/healthz` 200).  
- Latencia p95 /predict: <= 300 ms (ajustable según entorno).  
- Error rate 5xx: <= 1% semanal.  

Error budget: 2% semanal. Si se agota, priorizar correcciones.

---

## 9) Alertas (ejemplos)
Reglas sugeridas:
- Healthz FAIL x3 → notificar #staging-ml y asignar on-call.  
- Error rate 5xx > 1% por 10 min → abrir incidente.  
- Latencia p95 > 500 ms → alerta de performance.

Script ejemplo check_healthz.sh:
```bash
fails=0
for i in {1..3}; do
  code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/healthz || echo 000)
  [ "$code" != "200" ] && fails=$((fails+1))
  sleep 2
done
if [ $fails -ge 3 ]; then
  echo "[ALERTA] healthz falló 3 veces seguidas" >&2
  exit 1
else
  echo "OK: healthz estable"
fi
```

---

## 10) Tareas de mantenimiento / Runbook operativo
- Reentrenamiento / regeneración de artefactos:
  1. Re-ejecutar `MVP+Dashboard.ipynb` o el script `mvp_para_frontend.py` para generar `models/`, `metrics.csv`, `clientes_segmentados.csv`.
  2. Registrar artefactos y métricas en MLflow (`mlflow.log_param`, `mlflow.log_metric`, `mlflow.log_artifact`).
  3. Construir imagen Docker y etiquetar con `model_version` (por ejemplo: `banco-x-api:vYYYYMMDD-<run_id>`).
  4. Desplegar en staging y ejecutar smoke tests.

- Comandos útiles:
```bash
# Revisar metrics.csv
ls -la results || true
cat results/metrics.csv | head -n 200

# Levantar UI de MLflow
mlflow ui --backend-store-uri ./mlruns --port 5000

# Ver modelo dentro del contenedor
docker exec -it banco-x-api ls -la /app/models
```

---

## 11) Anexos y referencias
- README.md (raíz): instrucciones generales y dependencia de notebooks.  
- Notebooks: `MVP+Dashboard.ipynb` — generación de artefactos, métricas y dashboards.  
- Entrenamiento / motor: `mvp_para_frontend.py` — preprocesamiento, SMOTE, XGBoost, serialización.  
- Frontend / dashboard: `frontend.py`, `dashboard_seguimiento.py` (Streamlit).  
- MLflow: runs en `./mlruns` (local) o `MLFLOW_TRACKING_URI` para remoto.  
- Contactos: sección Equipo en README.

---

## 12) Recomendaciones finales y pendientes
- Confirmar y estandarizar la ruta exacta de serialización del modelo (`models/model.joblib` o `artifacts/model.pkl`) y exponer `model_version` en /healthz.  
- Añadir pruebas de contrato automáticas (CI) que validen `/predict` y `/healthz` después de cada build.  
- Configurar alertas en Prometheus/Grafana o en la plataforma de monitoreo usada por el equipo (listas de alertas propuestas en la sección 9).  
- Mantener versionado y registro en MLflow (model registry y tags) para facilitar rollback.

---
