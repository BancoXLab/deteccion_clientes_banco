# Integración del Pipeline de Entrenamiento - Resumen de Cambios

## ¿Qué se hizo?

Se integró la función de entrenamiento del notebook `baseline.ipynb` en el pipeline de Prefect (`src/training/train_pipeline.py`) con las siguientes características:

### 1. **Función de Entrenamiento Integrada**
   - Importadas todas las librerías necesarias (sklearn, xgboost, mlflow)
   - Integrada la lógica de entrenamiento de modelos: XGBoost, Random Forest, Logistic Regression
   - División automática train/test (80/20) en cada ejecución

### 2. **Trackeo con MLflow**
   - Cada entrenamiento se registra en MLflow con:
     - **Parámetros**: Configuración del modelo
     - **Métricas**: accuracy, precision, recall, f1, roc_auc, accuracy_train
     - **Modelo**: Guardado en formato nativo (xgboost.log_model o sklearn.log_model)
   - Experimento automático: `BancoX-{model_type}`
   - Run name con timestamp: `{model_type}_YYYYMMDD_HHMMSS`

### 3. **Comparación con Modelo en Producción**
   - Carga automática del F1 score del modelo en producción
   - Calcula mejora: `F1_nuevo - F1_producción`
   - Decisión de despliegue: **Actualiza si F1_nuevo > F1_producción**

### 4. **Gestión Automática de Modelos**
   - Nuevo task: `save_model_if_improved()`
   - Guarda modelo como pickle en `model/trained_pipeline-0.1.0.pkl`
   - Backup automático con timestamp si ya existe modelo
   - Metadatos guardados en JSON

### 5. **Salidas Generadas**
   - **CSV de métricas**: `artifacts/resultados/training_metrics.csv`
     - Registra cada entrenamiento con timestamp
     - Incluye F1 score actual, de producción, y decisión de despliegue
   - **Modelo en producción**: `model/trained_pipeline-0.1.0.pkl`
   - **Metadatos**: `model/model_metadata.txt` (JSON)
   - **MLflow Tracking**: Todos los runs en http://0.0.0.0:5000

## Estructura del Pipeline

```
┌─ load_data() ─────────────────────────┐
│  Carga desde MySQL                     │
└──────────────────┬──────────────────────┘
                   ↓
┌─ apply_smote() ────────────────────────┐
│  Oversampling para balanceo             │
└──────────────────┬──────────────────────┘
                   ↓
┌─ save_transformed_data() ──────────────┐
│  Guarda en MySQL_prepared_data          │
└──────────────────┬──────────────────────┘
                   ↓
┌─ train_classification_model() ─────────┐
│ ┌─ _train_model()                      │
│ │  - Entrena XGBoost/RF/LR             │
│ ├─ _calculate_metrics()                │
│ │  - Calcula accuracy, F1, ROC-AUC     │
│ ├─ _load_production_model_f1()         │
│ │  - Obtiene F1 de modelo actual       │
│ └─ Registra en MLflow                  │
│    - Parámetros, métricas, modelo      │
└──────────────────┬──────────────────────┘
                   ↓
┌─ save_model_if_improved() ─────────────┐
│  Si F1_nuevo > F1_producción:          │
│  - Hace backup del modelo actual       │
│  - Guarda nuevo modelo                 │
│  - Actualiza metadatos                 │
└──────────────────┬──────────────────────┘
                   ↓
┌─ clean_temp_files() ───────────────────┐
│  Limpia archivos temporales             │
└────────────────────────────────────────┘
```

## Configuración Requerida

### Variables de Entorno (.env)
```bash
# Base de datos
user=your_user
password=your_password
host=localhost
port=3306
db=banco_db

# Directorios
BANCX_TMP_DIR=/tmp/bancox_train
BANCX_MODEL_DIR=/workspaces/deteccion_clientes_banco/model
BANCX_RESULTS_DIR=/workspaces/deteccion_clientes_banco/artifacts/resultados

# MLflow
MLFLOW_TRACKING_URI=http://0.0.0.0:5000
```

### Iniciar MLflow (para trackeo local)
```bash
cd /workspaces/deteccion_clientes_banco
mlflow ui --host 0.0.0.0 --port 5000
```

## Cómo Usar

### Ejecución Manual
```python
from src.training.train_pipeline import train_pipeline

# Con modelo XGBoost (por defecto)
train_pipeline()

# Con Random Forest
train_pipeline(model_type="Random Forest")

# Con Logistic Regression
train_pipeline(model_type="Logistic Regression")
```

### Ejecución Programada
```bash
python src/training/train_pipeline.py
```
Se ejecutará diariamente a las 3:00 AM mediante Prefect.

### Validar Instalación
```bash
python tests/test_train_pipeline.py
```

## Archivos Modificados

1. **src/training/train_pipeline.py** ← Principal
   - Añadidas importaciones (sklearn, xgboost, mlflow, pickle)
   - Añadidas constantes de directorios
   - 3 funciones de soporte (_train_model, _calculate_metrics, _load_production_model_f1)
   - 2 tasks nuevos (train_classification_model, save_model_if_improved)
   - Flow principal actualizado

## Archivos Creados

1. **docs/TRAIN_PIPELINE_GUIDE.md**
   - Documentación detallada del pipeline
   - Ejemplos de uso
   - Troubleshooting

2. **tests/test_train_pipeline.py**
   - Script de validación completo
   - 5 tests: directorios, MLflow, modelos, producción, métricas

## Métricas Registradas

| Métrica | Descripción | Uso |
|---------|------------|-----|
| `accuracy` | (TP+TN)/(Total) | Exactitud general |
| `precision` | TP/(TP+FP) | Confianza en predicciones positivas |
| `recall` | TP/(TP+FN) | Cobertura de positivos reales |
| **`f1`** | 2×(P×R)/(P+R) | **Métrica de decisión** 🎯 |
| `roc_auc` | Área bajo ROC | Capacidad discriminativa |
| `accuracy_train` | Exactitud en entrenamiento | Detecta overfitting |
| `f1_production` | F1 del modelo vigente | Referencia para comparación |
| `f1_improvement` | F1_nuevo - F1_producción | Delta de desempeño |

## Ejemplo de Salida

### En MLflow UI (http://0.0.0.0:5000)
```
Experimento: BancoX-XGBoost
├── Run: XGBoost_20250120_143022
│   ├── Parámetros:
│   │   ├── n_estimators: 100
│   │   ├── learning_rate: 0.1
│   │   └── max_depth: 6
│   ├── Métricas:
│   │   ├── accuracy: 0.9123
│   │   ├── f1: 0.8232 ✓ Mejoró
│   │   └── roc_auc: 0.9500
│   └── Modelo: XGBoost (registrado)
```

### En CSV (artifacts/resultados/training_metrics.csv)
```
timestamp,modelo,accuracy,recall,precision,f1,accuracy_train,roc_auc,f1_production,f1_improvement,should_deploy
2025-01-20 14:30:22,XGBoost,0.9123,0.8500,0.8200,0.8232,0.9456,0.9500,0.8000,0.0232,True
```

### Metadatos (model/model_metadata.txt)
```json
{
  "timestamp": "2025-01-20 14:30:22",
  "model_type": "XGBoost",
  "f1_score": 0.8232,
  "f1_improvement": 0.0232,
  "accuracy": 0.9123,
  "recall": 0.85,
  "precision": 0.82,
  "roc_auc": 0.95
}
```

## Decisión de Despliegue

```
Si: F1_nuevo > F1_producción
    Entonces: Actualizar modelo en producción ✅
    Y guardar backup
    Y registrar metadatos

Si no:
    Entonces: Mantener modelo actual ⚠
    Y registrar en CSV (should_deploy=False)
```

### Ejemplo Real

| Escenario | F1 Nuevo | F1 Producción | Mejora | Acción |
|-----------|----------|--------------|--------|--------|
| Primera ejecución | 0.8232 | 0.0000 | +0.8232 | ✅ Desplegar |
| Mejora detectada | 0.8350 | 0.8232 | +0.0118 | ✅ Desplegar |
| Sin mejora | 0.8200 | 0.8232 | -0.0032 | ⚠ Mantener |
| Degradación | 0.7900 | 0.8232 | -0.0332 | ⚠ Mantener |

## Próximos Pasos Sugeridos

1. **Validación en Desarrollo**
   ```bash
   python tests/test_train_pipeline.py
   ```

2. **Iniciar MLflow** (si no está corriendo)
   ```bash
   mlflow ui --host 0.0.0.0 --port 5000
   ```

3. **Ejecutar Pipeline Manualmente**
   ```python
   from src.training.train_pipeline import train_pipeline
   train_pipeline()
   ```

4. **Verificar Resultados**
   - MLflow UI: http://0.0.0.0:5000
   - CSV: `artifacts/resultados/training_metrics.csv`
   - Modelo: `model/trained_pipeline-0.1.0.pkl`

5. **Monitorear en Producción**
   - Revisar CSV periódicamente
   - Verificar metadatos del modelo
   - Comparar runs en MLflow

## Troubleshooting

### "Connection refused" en MLflow
→ Iniciar servidor: `mlflow ui --host 0.0.0.0 --port 5000`

### Modelo no se actualiza
→ Verificar permisos en `model/` y revisar logs

### Métricas inconsistentes
→ Verificar timestamp en CSV y MLflow para correlacionar runs

## Documentación Completa

Para más detalles, consulta:
- `docs/TRAIN_PIPELINE_GUIDE.md` - Guía completa del pipeline
- `src/training/train_pipeline.py` - Código fuente con comentarios
- `tests/test_train_pipeline.py` - Tests de validación
