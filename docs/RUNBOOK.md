# RUNBOOK — <Nombre del servicio / MVP>

## 1) Contactos y alcance
- **Dueño técnico:** <Nombre> (@usuario)
- **Soporte/Incidentes:** <Canal> (ej. #staging-ml)
- **Horario operativo:** <días/horas>
- **Alcance:** API `/predict` en **staging** (este runbook no cubre producción)

---

## 2) Endpoints y checks rápidos
- **Health:** `GET /healthz` → **200** `{ok, env, version}`
- **Inferencia:** `POST /predict` → **200** `{customer_id, score, version}`
- **Métricas:** `GET /metrics` → counters básicos (si aplica)

**Comandos (ejemplo):**
```bash
curl -s http://<HOST>:8000/healthz
curl -s -X POST http://<HOST>:8000/predict -H "Content-Type: application/json"   -d '{"customer_id":"123","features":{"monto":100}}'
```

---

## 3) Configuración (env vars y flags)
- `APP_ENV=staging`
- `APP_USE_MOCK=true|false`  ← **toggle** del modelo
- `MODEL_PATH=/artifacts/model.joblib`
- Otros: <...>

**Versión actual:** commit `<sha>` · modelo `<run_id/versión>`

---

## 4) Start / Stop / Logs
**Local (uvicorn):**
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

**Docker:**
```bash
docker run -d --name <svc> -p 8000:8000   -e APP_ENV=staging -e APP_USE_MOCK=true   <image>:<tag>
```

**Logs:**
```bash
docker logs -f <svc>    # o tail -f app.log
```

---

## 5) Playbooks de incidentes (paso a paso)

### 5.1 Healthz DOWN (3 fallos seguidos)
1. Verificar proceso/contendor → **reiniciar**.
2. Revisar últimos **5 min** de logs (buscar stacktrace).
3. Si persiste: activar **APP_USE_MOCK=true** y reiniciar.
4. Validar `/healthz` y **flujo feliz** en `/predict`.
5. Registrar incidente (resumen y causa preliminar) y abrir **ticket**.

**Criterio de éxito:** `/healthz` = 200 y 2 requests a `/predict` **OK**.

---

### 5.2 Latencia p95 > <umbral> por 5 min
1. Capturar **5 requests** lentos (sin PII): tamaño payload, timestamps.
2. Verificar dependencia de modelo/feature store/red.
3. Mitigar: limitar payload / subir timeout cliente / **APP_USE_MOCK=true** temporal.
4. Abrir ticket de performance con evidencia.

**Criterio de éxito:** p95 vuelve por debajo de <umbral> por 10 min.

---

### 5.3 Errores 5xx > 1% por 10 min
1. Distinguir **5xx** vs **input inválido** (convertible a 4xx).
2. Endurecer validación (pydantic/jsonschema) para evitar 5xx por input.
3. Si dependencia externa falla: retry/backoff o fallback documentado.

**Criterio de éxito:** error rate < 1% por 10 min.

---

## 6) Rollback / Fallback
- **Toggle de modelo (rápido):** `APP_USE_MOCK=true` + redeploy.
- **Imagen previa:** `docker run <image>:<tag_anterior>` (tag S11 recomendado).
- **Verificación post-rollback:** correr **smoke tests** y flujo feliz.

---

## 7) Verificación post-incidente
- `pytest -m smoke` → **verde**
- `/healthz` 200 y `/predict` contrato ok
- Registrar: tiempo de recuperación, causa raíz breve, acciones A1–A3.

---

## 8) SLOs declarados (staging)
- **Disponibilidad:** ≥ **98%** semanal (healthz=200)
- **Latencia p95 /predict:** ≤ **300 ms**
- **Errores 5xx:** ≤ **1%**

**Error budget:** 2% semanal. Si se agota → priorizar fixes sobre features.

---

## 9) Alerta (simulada) — ejemplo
- **Regla:** si `/healthz` falla **3** veces seguidas → **alertar** a `#staging-ml`.
- **Acción:** reiniciar servicio; si persiste, `APP_USE_MOCK=true`; validar y registrar.

**Script de ejemplo:**
```bash
# check_healthz.sh
fails=0
for i in {1..3}; do
  code=$(curl -s -o /dev/null -w "%{http_code}" http://<HOST>:8000/healthz || echo 000)
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

## 10) Anexos
- **Endpoints externos / secretos**: (no volcar secretos en texto claro)
- **Diagrama corto**: <link/imagen opcional>
- **Checklist de release**: <link>
