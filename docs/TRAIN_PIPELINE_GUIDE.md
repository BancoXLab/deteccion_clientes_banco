# Guía del Pipeline de Entrenamiento con MLflow

## Descripción General

El pipeline actualizado en `src/training/train_pipeline.py` integra:

1. **Carga de datos** desde MySQL
2. **Transformación con SMOTE** para balanceo de clases
3. **Entrenamiento de modelos** (XGBoost, Random Forest, Logistic Regression)
4. **Trackeo con MLflow** de parámetros, métricas y modelos
5. **Comparación con modelo en producción** basada en F1 score
6. **Actualización automática en producción** si hay mejora

## Arquitectura

### Componentes Principales

#### 1. Tasks de Prefect
- `load_data()`: Carga datos de MySQL
- `apply_smote()`: Aplica oversampling SMOTE
- `save_transformed_data()`: Guarda datos en MySQL
- `train_classification_model()`: Entrena y evalúa el modelo
- `save_model_if_improved()`: Actualiza modelo en producción si mejora
- `clean_temp_files()`: Limpia archivos temporales

#### 2. Funciones de Soporte
- `_train_model()`: Entrena modelo según tipo
- `_calculate_metrics()`: Calcula todas las métricas
- `_load_production_model_f1()`: Obtiene F1 score del modelo en producción

### Flow Principal

```
load_data() 
    ↓
apply_smote() 
    ↓
save_transformed_data()
    ↓
train_classification_model() ← Integra entrenamiento + MLflow
    ↓
save_model_if_improved() ← Decisión de despliegue
    ↓
clean_temp_files()
```

## Configuración

### Variables de Entorno

Configura estas variables en tu `.env`:

```bash
# Base de datos
user=your_mysql_user
password=your_mysql_password
host=your_mysql_host
port=3306
db=your_database

# Directorios
BANCX_TMP_DIR=/tmp/bancox_train
BANCX_MODEL_DIR=/workspaces/deteccion_clientes_banco/model
BANCX_RESULTS_DIR=/workspaces/deteccion_clientes_banco/artifacts/resultados

# MLflow
MLFLOW_TRACKING_URI=http://0.0.0.0:5000
```

## Uso

### Ejecución Manual

```python
from src.training.train_pipeline import train_pipeline

# Ejecutar con modelo XGBoost (por defecto)
train_pipeline()

# Ejecutar con Random Forest
train_pipeline(model_type="Random Forest")

# Ejecutar con Logistic Regression
train_pipeline(model_type="Logistic Regression")
```

### Ejecución Programada

El pipeline está configurado para ejecutarse automáticamente:

```bash
python src/training/train_pipeline.py
```

Se ejecutará diariamente a las 3:00 AM mediante cron.

## Salidas Generadas

### 1. MLflow
- Experimento: `BancoX-{model_type}`
- Run con parámetros, métricas y modelo registrado
- Tracking URI: `http://0.0.0.0:5000`

### 2. Archivos CSV
**Archivo**: `artifacts/resultados/training_metrics.csv`

Columnas:
- `timestamp`: Fecha y hora de entrenamiento
- `modelo`: Tipo de modelo entrenado
- `accuracy`: Exactitud en conjunto de prueba
- `recall`: Recall en conjunto de prueba
- `precision`: Precisión en conjunto de prueba
- `f1`: F1 Score en conjunto de prueba
- `accuracy_train`: Exactitud en conjunto de entrenamiento
- `roc_auc`: AUC-ROC en conjunto de prueba
- `f1_production`: F1 Score del modelo en producción
- `f1_improvement`: Mejora en F1 Score (actual - producción)
- `should_deploy`: Boolean indicando si se debe actualizar producción

### 3. Modelo en Producción
**Archivo**: `model/trained_pipeline-0.1.0.pkl`

- Actualizado únicamente si F1 score mejora
- Backup automático con timestamp: `model/model_backup_YYYYMMDD_HHMMSS.pkl`
- Metadatos guardados en: `model/model_metadata.txt`

## Lógica de Decisión de Despliegue

El modelo se actualiza en producción si:

```
F1_nuevo > F1_producción
```

### Ejemplo

```
F1 Producción:   0.80
F1 Nuevo:        0.82
Mejora:          +0.02
Acción:          ✅ ACTUALIZAR MODELO
```

```
F1 Producción:   0.82
F1 Nuevo:        0.81
Mejora:          -0.01
Acción:          ❌ MANTENER MODELO ACTUAL
```

## Métricas Registradas

Todas las siguientes métricas se registran por cada entrenamiento:

| Métrica | Descripción |
|---------|------------|
| `accuracy` | (TP + TN) / (TP + TN + FP + FN) |
| `precision` | TP / (TP + FP) |
| `recall` | TP / (TP + FN) |
| `f1` | 2 * (precision * recall) / (precision + recall) |
| `roc_auc` | Area bajo la curva ROC |
| `accuracy_train` | Accuracy en conjunto de entrenamiento |
| `f1_production` | F1 del modelo actual en producción |
| `f1_improvement` | Diferencia de F1: nuevo - producción |

## Modelos Soportados

### XGBoost (Recomendado)
```python
params = {
    "n_estimators": 100,
    "learning_rate": 0.1,
    "max_depth": 6,
    "eval_metric": "logloss",
    "random_state": 42
}
```

### Random Forest
```python
params = {
    "n_estimators": 500,
    "max_depth": 10,
    "random_state": 42
}
```

### Logistic Regression
```python
params = {
    "max_iter": 1000,
    "solver": "liblinear",
    "random_state": 42
}
```

## Monitoreo

### En MLflow UI
1. Abre: `http://0.0.0.0:5000`
2. Busca experimento `BancoX-{model_type}`
3. Compara métricas entre runs

### En CSV
```python
import pandas as pd

metrics_df = pd.read_csv("artifacts/resultados/training_metrics.csv")
print(metrics_df[["timestamp", "modelo", "f1", "f1_improvement", "should_deploy"]])
```

### Metadatos del Modelo
```bash
cat model/model_metadata.txt
```

## Manejo de Errores

### Error al conectar a MySQL
- Verificar credenciales en `.env`
- Verificar que la base de datos está disponible
- El task `load_data()` tiene reintentos automáticos (2 intentos)

### Error al cargar modelo de producción
- Si no existe, se asume F1 = 0.0
- Primera ejecución siempre actualizará producción
- Se registra warning en logs

### Error durante entrenamiento
- Task `train_classification_model()` tiene reintentos (1 intento)
- Se registra error detallado
- Pipeline se detiene y no actualiza producción

## Integración con Servicios Externos

### Prefect Cloud
Para usar Prefect Cloud en lugar de local:

```python
from prefect.settings import PREFECT_API_URL
import os

os.environ["PREFECT_API_URL"] = "https://api.prefect.cloud/api/accounts/{ACCOUNT_ID}/workspaces/{WORKSPACE_ID}"
```

### Slack Alerts (Opcional)
Para notificaciones, añade handlers a los tasks:

```python
from prefect.runtime import task_context

@task(name="Train...")
def train_classification_model(...):
    # Si hay mejora, enviar notificación a Slack
    if should_deploy:
        # Implementar notificación
        pass
```

## Troubleshooting

### Modelo no se actualiza aunque hay mejora
- Verificar que `PRODUCTION_MODEL_PATH` existe
- Verificar permisos de escritura en `model/`
- Revisar logs de Prefect para errores

### Métricas inconsistentes entre MLflow y CSV
- Ambas usan los mismos datos, deben ser iguales
- Redondeo a 4 decimales en CSV
- Revisar timestamp para correlacionar runs

### Pipeline muy lento
- SMOTE es computacionalmente intensivo
- Reducir `target_per_class` en `apply_smote()`
- Aumentar `timeout_seconds` en tasks si es necesario

## Próximas Mejoras

- [ ] Soporte para validación cruzada
- [ ] Hyperparameter tuning automático
- [ ] Alertas por degradación de modelo
- [ ] A/B testing entre modelos
- [ ] Predicciones en tiempo real con modelo de producción
