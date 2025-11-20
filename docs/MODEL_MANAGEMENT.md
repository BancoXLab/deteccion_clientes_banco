# Gestión de Modelos - Banco X Detector

## 📍 Ubicación del Modelo en Producción

### Único Modelo Activo
```
src/app/model/
├── __init__.py
├── model.py                      # ← Carga el modelo aquí (línea 13)
└── trained_pipeline-0.1.0.pkl   # ← MODELO EN PRODUCCIÓN
```

### Cómo la API Carga el Modelo

```python
# Archivo: src/app/model/model.py

from pathlib import Path
import pickle

__version__ = "0.1.0"
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / f"trained_pipeline-{__version__}.pkl"

# Carga en tiempo de importación
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
```

**Ubicación resuelta**: `/workspaces/deteccion_clientes_banco/src/app/model/trained_pipeline-0.1.0.pkl`

### Cómo lo Consume la API

```python
# En src/app/routes/general_routes.py o src/app/main.py

from src.app.model.model import predict_pipeline_proba

# Predicción
prediction = predict_pipeline_proba(input_data)
```

---

## 🔄 Ciclo de Vida del Modelo

### 1. Desarrollo y Entrenamiento
```bash
# Se realiza en notebooks/
# Salida: modelo serializado en .pkl
# Ubicación temporal: notebooks/ o artifacts/
```

### 2. Versionamiento
```bash
# Formato de nombre: trained_pipeline-{version}.pkl
# Ejemplo: trained_pipeline-0.1.0.pkl
# Versiones futuras: 0.2.0, 1.0.0, etc.
```

### 3. Deployment
```bash
# Copiar archivo .pkl a:
cp models/trained_pipeline-X.Y.Z.pkl src/app/model/trained_pipeline-X.Y.Z.pkl

# Actualizar __version__ en src/app/model/model.py:
__version__ = "X.Y.Z"
```

### 4. Testing
```bash
# La API automáticamente usa la nueva versión
pytest tests/test_API.py -v
```

---

## 📊 Rastreo de Cambios de Modelo

### Información del Modelo Actual

| Propiedad | Valor |
|-----------|-------|
| Versión | 0.1.0 |
| Ruta | `src/app/model/trained_pipeline-0.1.0.pkl` |
| Tamaño | 363 KB |
| Ubicación en repo | `src/app/model/` |
| Cargado por | `src/app/model/model.py:13` |
| Consumido por | API (FastAPI routes) |

### Historial de Modelos

```
| Versión | Fecha | Cambios | Estado |
|---------|-------|---------|--------|
| 0.1.0   | Nov 2025 | Modelo inicial | ✅ ACTIVO |
| (próximo) | -- | -- | -- |
```

---

## 🚀 Actualizar a Nuevo Modelo

### Paso 1: Preparar Nuevo Modelo
```bash
# Entrenar en notebook
python notebooks/train_model.py
# Salida: trained_pipeline-0.2.0.pkl
```

### Paso 2: Copiar a Producción
```bash
cp artifacts/trained_pipeline-0.2.0.pkl src/app/model/
```

### Paso 3: Actualizar Versión
```python
# Archivo: src/app/model/model.py
__version__ = "0.2.0"  # Cambiar esto
```

### Paso 4: Validar
```bash
pytest tests/ -v
```

### Paso 5: Commit y Deploy
```bash
git add src/app/model/trained_pipeline-0.2.0.pkl
git commit -m "refactor: actualizar modelo a versión 0.2.0"
git push origin DEV
# Crear PR y mergear a main
```

---

## ⚙️ Mejores Prácticas

### ✅ Hacer
- ✓ Mantener modelo en `src/app/model/`
- ✓ Versionar cambios de modelo en git
- ✓ Incluir notas en commit sobre cambios del modelo
- ✓ Ejecutar tests completos después de actualizar modelo
- ✓ Documentar métricas del nuevo modelo

### ❌ Evitar
- ✗ Múltiples copias del modelo en diferentes ubicaciones
- ✗ Cambiar `__version__` sin actualizar archivo
- ✗ Nombres de archivos inconsistentes
- ✗ Modelos sin versión o fecha
- ✗ Actualizar modelo sin tests

---

## 🔍 Debugging: Verificar Qué Modelo se Usa

```bash
# Ver la ruta exacta del modelo cargado
python3 << 'EOF'
from pathlib import Path
from src.app.model.model import MODEL_PATH, __version__
print(f"Versión: {__version__}")
print(f"Ruta: {MODEL_PATH}")
print(f"Existe: {MODEL_PATH.exists()}")
EOF
```

---

## 📦 Almacenamiento Externo (Futuro)

Si el modelo crece o necesitas versionar múltiples versiones:

### Opción 1: MLflow Model Registry
```python
# src/app/model/model_registry.py
import mlflow

# Registrar modelo
mlflow.sklearn.log_model(model, "banco-x-detector")
```

### Opción 2: S3 / Azure Blob Storage
```python
# Descargar modelo en startup
from azure.storage.blob import BlobClient

blob = BlobClient.from_blob_url(model_url)
blob.download_blob().readinto(open("model.pkl", "wb"))
```

### Opción 3: GitHub Releases
```bash
# Liberar modelo como artifact
gh release upload v0.2.0 trained_pipeline-0.2.0.pkl
```

---

## 📝 Changelog

### v0.1.0 (Nov 2025)
- Modelo inicial
- Features: 27 variables
- Algoritmo: XGBoost Pipeline
- Precisión: ~XX%

---

## 📚 Referencias

- [Documentación de pickle](https://docs.python.org/3/library/pickle.html)
- [MLflow Model Serving](https://mlflow.org/docs/latest/model-serving.html)
- [Model Versioning Best Practices](https://aws.amazon.com/es/blogs/machine-learning/)
