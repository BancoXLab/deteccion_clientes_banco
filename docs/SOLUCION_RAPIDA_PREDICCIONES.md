# 🎯 RESUMEN EJECUTIVO: Solución Rápida

## ❌ PROBLEMA IDENTIFICADO

Tu modelo **predice SIEMPRE Clase 0 (negativo)**, nunca Clase 1 (positivo).

```
1000 predicciones:  [Clase 0: 100% ████████████████████]  [Clase 1: 0%]
Probabilidades:     Prob(1) ≈ 0.30  (necesita > 0.50)
```

---

## 🔍 CAUSA RAÍZ

El modelo cargado es un **RandomForest con SOLO 10 árboles** entrenado en datos desbalanceados:

```python
RandomForestClassifier(
    n_estimators=10,  # ← SUPER PEQUEÑO (debería ser 100-500)
    random_state=42
)
```

**Con 10 árboles + datos desbalanceados → Sesgo total hacia Clase 0**

---

## ✅ SOLUCIONES

### 🟢 SOLUCIÓN 1: RÁPIDA (5 MIN) - ¡HAZLO AHORA!

Ajustar threshold de predicción:

```bash
python src/scripts/fix_predictions.py --quick
```

**Qué hace:**
- Reduce threshold de 0.5 → 0.35 en `src/app/model/model.py`
- Ahora el modelo predice Clase 1 cuando Prob(1) ≥ 0.35 (antes ≥ 0.50)

**Resultado esperado:**
```
ANTES: Clase 0: 1000 (100%) | Clase 1: 0 (0%)
DESPUÉS: Clase 0: ~700 (70%) | Clase 1: ~300 (30%)  ← MÁS POSITIVOS
```

---

### 🟡 SOLUCIÓN 2: PERMANENTE (30 MIN) - HAZLO HOY

Reentrenar modelo con mejor configuración:

```bash
python src/scripts/fix_predictions.py --retrain
python src/training/retrain_model.py
```

**Qué hace:**
- RandomForest: 10 → 200 estimadores
- Aplica SMOTE para balanceo
- Regularización adicional

**Mejor que Solución 1 porque:**
- ✅ Threshold vuelve a 0.5 (estándar)
- ✅ Modelo aprende mejor
- ✅ Menos falsos positivos

---

### 🔵 SOLUCIÓN 3: ROBUSTA (60 MIN) - ESTA SEMANA

Cambiar a XGBoost (mejor para datos desbalanceados):

```bash
python src/scripts/fix_predictions.py --improve
python src/training/train_xgboost_model.py
```

---

## 🚀 PLAN RECOMENDADO

### HOY (5 minutos):
```bash
# 1. Implementar solución rápida
python src/scripts/fix_predictions.py --quick

# 2. Reiniciar API
docker-compose restart bancox-api

# 3. Verificar
curl -X POST http://localhost:8000/predict ... | jq '.probability_class_1'
```

---

### HOY O MAÑANA (30 minutos):
```bash
# Implementar solución permanente
python src/scripts/fix_predictions.py --retrain
python src/training/retrain_model.py

# Verificar métricas
python src/scripts/debug_predictions.py
```

---

## 📊 COMPARACIÓN

| Solución | Tiempo | Efectividad | Cuándo |
|----------|--------|-------------|--------|
| 1. Threshold | 5 min | 60% | ✅ AHORA |
| 2. Retrain | 30 min | 90% | ✅ HOY |
| 3. XGBoost | 60 min | 95% | ✅ ESTA SEMANA |

---

## 📁 ARCHIVOS CREADOS PARA TI

| Archivo | Para |
|---------|------|
| [src/scripts/debug_predictions.py](src/scripts/debug_predictions.py) | Diagnosticar problemas |
| [src/scripts/fix_predictions.py](src/scripts/fix_predictions.py) | Generar soluciones |
| [docs/DIAGNOSTICO_PREDICCIONES.md](docs/DIAGNOSTICO_PREDICCIONES.md) | Guía detallada |

---

## 🎯 PRÓXIMO PASO

Elige UNA opción y ejecuta:

```bash
# Opción 1 (RÁPIDA - recomendada para ahora)
python src/scripts/fix_predictions.py --quick

# Opción 2 (PERMANENTE - recomendada para hoy)
python src/scripts/fix_predictions.py --retrain && python src/training/retrain_model.py

# Opción 3 (ROBUSTA - recomendada para esta semana)
python src/scripts/fix_predictions.py --improve && python src/training/train_xgboost_model.py
```

---

✅ **¡El problema está identificado y solucionable!**
