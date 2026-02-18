# 🔍 Guía de Debugging: Modelo No Predice Casos Positivos

**Fecha creada:** Febrero 18, 2026  
**Problema:** El modelo predice principalmente clase 0 (negativo) incluso en API `/predict` y endpoints de batch  
**Objetivo:** Diagnóstico paso a paso + soluciones implementables

---

## 1. DIAGNÓSTICO RÁPIDO (5 minutos)

### 1.1 Verificar que la API está funcionando
```bash
# Test básico de conectividad
curl -s http://localhost:8000/healthz | jq
curl -s http://localhost:8000/info | jq
```

**Esperado:** 200 OK en ambos

### 1.2 Probar predicción con datos de prueba
```bash
curl -s -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35.0,
    "month": 5,
    "day_of_week": 2,
    "duration": 1000.0,
    "campaign": 5.0,
    "pdays": 999.0,
    "previous": 5.0,
    "emp_var_rate": -1.8,
    "cons_price_idx": 92.893,
    "cons_conf_idx": -46.2,
    "euribor3m": 1.266,
    "nr_employed": 5099.1,
    "previous_bin": 1,
    "job_target_mean": 0.50,
    "marital_divorced": 0,
    "marital_married": 1,
    "marital_single": 0,
    "marital_unknown": 0,
    "education_freq_encode": 0.75,
    "housing_no": 0,
    "housing_unknown": 0,
    "housing_yes": 1,
    "loan_no": 1,
    "loan_unknown": 0,
    "loan_yes": 0,
    "contact_cellular": 1,
    "contact_telephone": 0
  }' | jq
```

**Observar:**
- `"prediction": 0` o `1` ← es siempre 0?
- `"probability_class_0"` y `"probability_class_1"` ← cuál es mayor?

**Si ves siempre `"prediction": 0`** → PROBLEMA CONFIRMADO. Continúa a 2.

---

## 2. CAUSAS RAÍZ POTENCIALES

| Causa | Probabilidad | Síntoma | Sección |
|-------|------------|---------|---------|
| **Sesgo del modelo entrenado** | 🔴 ALTA | Predice todo 0 incluso con `probability_class_1 > 0.5` | 3.1 |
| **Threshold incorrecto (> 0.5)** | 🔴 ALTA | Proba cercana a 0.5 pero sigue prediciendo 0 | 3.2 |
| **Desajuste de features** | 🟠 MEDIA | Error en lista `FEATURE_COLUMNS` | 3.3 |
| **Datos de entrada fuera de rango** | 🟠 MEDIA | Valores inválidos en entrada | 3.4 |
| **Modelo descargado incorrectamente** | 🟡 BAJA | Features mismatch después de cargar pickle | 3.5 |

---

## 3. DIAGNÓSTICO DETALLADO

### 3.1 ¿El modelo tiene SESGO inherente?

**Paso 1:** Acceder al modelo entrenado localmente
```bash
cd /workspaces/deteccion_clientes_banco

# Crear un script de debug
cat > debug_model.py << 'EOF'
import pickle
import pandas as pd
import numpy as np
from pathlib import Path

# Cargar modelo
model_path = Path.cwd() / "model" / "trained_pipeline-0.1.0.pkl"
if not model_path.exists():
    print(f"❌ Modelo no encontrado en {model_path}")
    exit(1)

with open(model_path, "rb") as f:
    model = pickle.load(f)

print("=" * 60)
print("ANÁLISIS DEL MODELO ENTRENADO")
print("=" * 60)

# Info del modelo
print(f"\n✓ Tipo de modelo: {type(model).__name__}")
print(f"✓ Features esperadas: {model.n_features_in_ if hasattr(model, 'n_features_in_') else 'N/A'}")

# Crear datos de test con características positivas obvias
test_data = pd.DataFrame([{
    'age': 35.0,
    'month': 5,
    'day_of_week': 2,
    'duration': 1000.0,  # Duration alta = más probable aceptar
    'campaign': 5.0,
    'pdays': 999.0,
    'previous': 5.0,      # Previous contacts alto
    'emp_var_rate': -1.8,
    'cons_price_idx': 92.893,
    'cons_conf_idx': -46.2,
    'euribor3m': 1.266,
    'nr_employed': 5099.1,
    'previous_bin': 1,
    'job_target_mean': 0.50,  # Trabajo con alta tasa de aceptación
    'marital_divorced': 0,
    'marital_married': 1,
    'marital_single': 0,
    'marital_unknown': 0,
    'education_freq_encode': 0.75,
    'housing_no': 0,
    'housing_unknown': 0,
    'housing_yes': 1,
    'loan_no': 1,
    'loan_unknown': 0,
    'loan_yes': 0,
    'contact_cellular': 1,
    'contact_telephone': 0
}])

# Predicción
pred_class = model.predict(test_data)
pred_proba = model.predict_proba(test_data) if hasattr(model, 'predict_proba') else None

print(f"\n📊 PREDICCIÓN CON DATOS POSIBLES POSITIVOS:")
print(f"  Clase predicha: {pred_class[0]}")
if pred_proba is not None:
    print(f"  Prob(Clase 0): {pred_proba[0][0]:.4f}")
    print(f"  Prob(Clase 1): {pred_proba[0][1]:.4f}")
    print(f"  ⚠️  Máxima probabilidad: Clase {np.argmax(pred_proba[0])}")

# Distribución de clases en predicción de 1000 muestras aleatorias
print(f"\n📈 DISTRIBUCIÓN DE PREDICCIONES (1000 muestras aleatorias):")
predictions = []
for i in range(1000):
    random_data = test_data.copy()
    # Add slight randomness to duration (key feature)
    random_data.iloc[0, random_data.columns.get_loc('duration')] += np.random.uniform(-100, 100)
    pred = model.predict(random_data)[0]
    predictions.append(pred)

unique, counts = np.unique(predictions, return_counts=True)
for u, c in zip(unique, counts):
    print(f"  Clase {u}: {c} ({100*c/1000:.1f}%)")

print("\n" + "=" * 60)
EOF

python debug_model.py
```

**Interpretar resultado:**
- Si **Prob(Clase 1) es alta (>0.5) pero predice 0** → THRESHOLD PROBLEM (ver 3.2)
- Si **Prob(Clase 1) es baja (<0.1) siempre** → Modelo tiene sesgo o entrenamiento deficiente
- Si **Clase 1 aparece en <5% de 1000 predicciones** → Problema crítico

---

### 3.2 ¿Hay un THRESHOLD incorrecto?

**Síntoma:** `probability_class_1 = 0.65` pero `prediction = 0` (debería ser 1)

**Causa probable:** El modelo usa threshold ≠ 0.5

**Solución:**
```python
# En src/app/model/model.py, reemplazar:

def predict_pipeline_proba(input_data: Dict[str, Any]) -> tuple:
    """Versión mejorada: expone threshold"""
    # ... código existente ...
    
    pred_class = model.predict(X)
    pred_proba = model.predict_proba(X)
    
    # ⭐ NUEVA LÓGICA: usar threshold explícito 0.5
    threshold = 0.5  # ← Cambiar aquí si necesitas otro valor
    pred_class_corrected = (pred_proba[0][1] >= threshold).astype(int)
    
    return int(pred_class_corrected), float(pred_proba[0][0]), float(pred_proba[0][1])
```

**Verificar threshold actual:**
```bash
# Extraer threshold del modelo PKL
python << 'EOF'
import pickle
from pathlib import Path

model_path = Path.cwd() / "model" / "trained_pipeline-0.1.0.pkl"
with open(model_path, "rb") as f:
    model = pickle.load(f)

# XGBoost y RandomForest usan threshold 0.5 por defecto
# Logistic Regression también
print(f"Modelo: {type(model).__name__}")
if hasattr(model, 'predict_proba'):
    print("✓ Modelo soporta predict_proba")
    print("✓ Threshold por defecto: 0.5")
else:
    print("❌ Modelo NO soporta predict_proba")
EOF
```

---

### 3.3 ¿DESAJUSTE DE FEATURES?

**Síntoma:** RuntimeError: "El modelo espera X features pero la entrada tiene Y"

**Causa:** Lista `FEATURE_COLUMNS` en [src/app/model/model.py](src/app/model/model.py) no coincide con las features del modelo entrenado

**Verificar:**
```bash
python << 'EOF'
import pickle
from pathlib import Path
from src.app.model.model import FEATURE_COLUMNS

model_path = Path.cwd() / "model" / "trained_pipeline-0.1.0.pkl"
with open(model_path, "rb") as f:
    model = pickle.load(f)

print(f"Features en FEATURE_COLUMNS: {len(FEATURE_COLUMNS)}")
print(f"Features esperadas por modelo: {model.n_features_in_}")
print(f"\nCoinciden: {'✓ SÍ' if len(FEATURE_COLUMNS) == model.n_features_in_ else '❌ NO'}")

# Si no coinciden, mostrar diferencia
if hasattr(model, 'feature_names_in_'):
    print(f"\nFeatures del modelo:\n{list(model.feature_names_in_)}")
    print(f"\nFeatures de entrada:\n{FEATURE_COLUMNS}")
    missing = set(model.feature_names_in_) - set(FEATURE_COLUMNS)
    extra = set(FEATURE_COLUMNS) - set(model.feature_names_in_)
    if missing:
        print(f"\n❌ Faltando en entrada: {missing}")
    if extra:
        print(f"\n⚠️  Extra en entrada: {extra}")
EOF
```

---

### 3.4 ¿DATOS DE ENTRADA FUERA DE RANGO?

**Síntoma:** API devuelve 200 pero siempre predice 0

**Causa:** Features escaladas/normalizadas durante entrenamiento, pero datos de entrada crudos

**Verificar en logs:**
```bash
# Si logs existe
tail -100 /tmp/bancox_api.log | grep -i "error\|warning\|scale"

# O hace un test con valores extremos
curl -s -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"age": 0, "month": 1, ..., "contact_telephone": 0}' | jq '.probability_class_1'
```

**Solución:** Asegurar que datos se normalizan antes de predecir:
```python
# En predict_pipeline_proba, ANTES de model.predict():
from sklearn.preprocessing import StandardScaler

# Si el modelo fue entrenado con escalado:
# X = scaler.transform(X)  # ← Necesita estar disponible
```

---

### 3.5 ¿Modelo DESCARGADO INCORRECTAMENTE del pickle?

**Síntoma:** Error como "type object 'XGBClassifier' has no attribute 'predict'"

**Verificar:**
```bash
python << 'EOF'
import pickle
from pathlib import Path

model_path = Path.cwd() / "model" / "trained_pipeline-0.1.0.pkl"
try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print(f"✓ Modelo cargado: {type(model)}")
    print(f"✓ Métodos disponibles: {[m for m in dir(model) if not m.startswith('_')][:10]}...")
except Exception as e:
    print(f"❌ Error al cargar: {e}")
EOF
```

---

## 4. SOLUCIONES IMPLEMENTABLES

### Solución 1: Reentrenar el Modelo (Recomendado)

**Paso 1:** Revisar balance de clases
```bash
python << 'EOF'
import pandas as pd

# Cargar datos originales
df = pd.read_parquet("/tmp/bancox_train/dataset_raw.parquet")
print("Distribución de clases en datos CRUDOS:")
print(df['y'].value_counts())
print(f"Ratio negativo/positivo: {(df['y']==0).sum() / (df['y']==1).sum():.1f}x")
EOF
```

**Paso 2:** Ejecutar pipeline con SMOTE explícito
```bash
cd /workspaces/deteccion_clientes_banco

# Ejecutar entrenamiento con balance
python -m src.training.train_pipeline --model-type XGBoost --enable-smote

# O usar el Makefile si existe
make train  # si hay target en Makefile
```

**Paso 3:** Validar nuevo modelo
```bash
python debug_model.py  # ver sección 3.1
```

---

### Solución 2: Ajustar Threshold de Predicción

**En** [src/app/model/model.py](src/app/model/model.py):

```python
def predict_pipeline_proba(input_data: Dict[str, Any]) -> tuple:
    # ... código existente hasta predict_proba ...
    
    pred_proba = model.predict_proba(X)
    
    # ⭐ USAR THRESHOLD OPTIMIZADO (no siempre 0.5)
    # Ejemplo: threshold 0.3 para capturar más positivos
    DECISION_THRESHOLD = 0.35  # ← Ajustar según tus necesidades
    pred_class_custom = (pred_proba[0][1] >= DECISION_THRESHOLD).astype(int)
    
    return int(pred_class_custom), float(pred_proba[0][0]), float(pred_proba[0][1])
```

**¿Cuándo usar qué threshold?**
- **0.5:** Balance perfecto (predicts 50% positivos si proba uniforme)
- **0.3-0.4:** Maximizar recall (capturar más clientes dispuestos a comprar, aceptar más falsos positivos)
- **0.6-0.7:** Maximizar precisión (ser seguro, evitar falsos positivos)

---

### Solución 3: Agregar Logging Detallado

**En** [src/app/model/model.py](src/app/model/model.py), añadir logging:

```python
import logging

logger = logging.getLogger(__name__)

def predict_pipeline_proba(input_data: Dict[str, Any]) -> tuple:
    X = pd.DataFrame([{col: input_data[col] for col in FEATURE_COLUMNS}])
    pred_class = model.predict(X)[0]
    pred_proba = model.predict_proba(X)[0]
    
    # ⭐ LOGGING
    logger.info(f"INPUT: {input_data}")
    logger.info(f"PREDICTION: class={pred_class}, proba_0={pred_proba[0]:.4f}, proba_1={pred_proba[1]:.4f}")
    
    return int(pred_class), float(pred_proba[0]), float(pred_proba[1])
```

**Ver logs:**
```bash
# Con Uvicorn
docker logs -f bancox_api 2>&1 | grep -i prediction

# O si corres localmente
python -m uvicorn src.app.main:app --log-level debug
```

---

### Solución 4: Crear Suite de Tests

**Archivo:** [tests/test_predict_positives.py](tests/test_predict_positives.py)

```python
import pytest
from src.app.model.model import predict_pipeline_proba

class TestPositivePredictions:
    """Verificar que el modelo PUEDE predecir clase 1"""
    
    def test_high_duration_predicts_positive(self):
        """Cliente con duración larga debe tener prob(1) > 0.5"""
        data = {
            'age': 35.0, 'month': 5, 'day_of_week': 2,
            'duration': 2000.0,  # ← Muy alto
            'campaign': 5.0, 'pdays': 999, 'previous': 5.0,
            # ... resto de features ...
        }
        pred_class, prob_0, prob_1 = predict_pipeline_proba(data)
        assert prob_1 > 0.5, f"Esperaba prob(1) > 0.5, pero fue {prob_1}"
    
    def test_previous_contacts_help(self):
        """Cliente con contactos previos debe tener prob(1) más alta"""
        data1 = {..., 'previous': 0, ...}
        data2 = {..., 'previous': 10, ...}
        
        _, _, prob1_with_0_prev = predict_pipeline_proba(data1)
        _, _, prob1_with_10_prev = predict_pipeline_proba(data2)
        
        assert prob1_with_10_prev > prob1_with_0_prev, \
            f"Más contactos previos debería aumentar prob(1)"
```

**Ejecutar:**
```bash
pytest tests/test_predict_positives.py -v
```

---

## 5. CHECKLIST DE IMPLEMENTACIÓN

- [ ] **Ejecutar debug_model.py** (3.1) → Verificar probabilidades
- [ ] **Revisar threshold del modelo** (3.2) → ¿Es 0.5 o diferente?
- [ ] **Verificar FEATURE_COLUMNS** (3.3) → ¿Coincide con entrenamiento?
- [ ] **Revisar logs de la API** (3.4) → ¿Hay errores de escalado?
- [ ] **Reentrenar modelo** (4.1) → Ejecutar pipeline con SMOTE
- [ ] **Ajustar threshold** (4.2) → Si necesita más positivos
- [ ] **Agregar logging** (4.3) → Para visibility
- [ ] **Ejecutar tests** (4.4) → Validar comportamiento esperado

---

## 6. COMANDOS RÁPIDOS PARA TESTING

```bash
# Terminal 1: Iniciar API
docker-compose up -d bancox-api
docker logs -f bancox-api

# Terminal 2: Test suite completo
python debug_model.py
pytest tests/test_predict_positives.py -v

# Terminal 3: Manual testing
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d @test_data.json | jq
```

---

## 7. PRÓXIMOS PASOS SI EL PROBLEMA PERSISTE

1. **Revisar datos de entrenamiento SMOTE** (sección 3.1)
2. **Ejecutar análisis de importancia de features** para ver si model.py desbalanceado
3. **Comparar predicciones del modelo entrenado vs API** (puede haber preprocesamiento faltante)
4. **Consultar MLflow** (`mlflow ui --backend-store-uri ./mlruns`) para historial de runs

---

**Última actualización:** 2026-02-18
