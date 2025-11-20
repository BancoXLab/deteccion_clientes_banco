# Guía de Contribución - Banco X Detector

## Estructura del Repositorio

```
banco-x-detector/
├── scr/                    # Código principal del proyecto
│   ├── app/               # API FastAPI y rutas
│   ├── ingesta/           # Módulo de ingesta de datos
│   ├── training/          # Pipeline de entrenamiento
│   ├── client/            # Cliente API para predicciones
│   ├── utils/             # Utilidades (logs, errores, PII)
│   ├── processing/        # Procesamiento de datos
│   ├── ops/               # Operaciones y monitoreo
│   └── scripts/           # Scripts auxiliares
├── tests/                  # Pruebas automatizadas
│   └── test_*.py          # Casos de prueba
├── notebooks/             # Notebooks de análisis y experimentación
├── data/                  # Datos (pequeños/ejemplos)
├── models/                # Modelos serializados (no versionado)
├── docs/                  # Documentación
├── config/                # Archivos de configuración
├── setup.py               # Configuración de setuptools
├── pyproject.toml         # Configuración de proyecto moderno
├── requirements.txt       # Dependencias reproducibles
├── Makefile               # Comandos comunes
├── Dockerfile             # Build de contenedor
└── docker-compose.yml     # Orquestación de servicios
```

## Configuración de Desarrollo

### 1. Clonar y preparar el entorno

```bash
git clone https://github.com/BancoXLab/deteccion_clientes_banco.git
cd deteccion_clientes_banco
```

### 2. Crear entorno virtual (recomendado)

```bash
python3.9 -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias

```bash
# Instalación básica
pip install -e .

# Instalación con dependencias de desarrollo
pip install -e ".[dev]"

# Instalación con soporte para notebooks
pip install -e ".[notebooks]"

# Instalación completa
pip install -e ".[dev,notebooks]"
```

Alternativamente, usar `requirements.txt` reproducible:
```bash
pip install -r requirements.txt
```

## Ejecutar Pruebas

### Ejecutar todos los tests
```bash
pytest -v
pytest -q  # Salida concisa
```

### Ejecutar tests específicos
```bash
pytest tests/test_encoding.py -v
pytest tests/test_training.py::test_smote -v
```

### Ejecutar con cobertura
```bash
pytest --cov=scr --cov-report=html
```

### Ejecutar solo tests unitarios
```bash
pytest -m unit -v
```

### Ejecutar solo tests de integración
```bash
pytest -m integration -v
```

## Estándares de Código

### Formateo automático
```bash
black scr/ tests/
isort scr/ tests/
flake8 scr/ tests/
```

### Type checking (opcional)
```bash
mypy scr/
```

## Flujo de Trabajo Git

### 1. Crear rama para nueva funcionalidad
```bash
git checkout -b feature/nueva-funcionalidad
# o
git checkout -b fix/correccion-bug
```

### 2. Realizar cambios y commits
```bash
git add .
git commit -m "docs: descripción clara del cambio (feat|fix|docs|test|chore)"
```

### 3. Mantener rama actualizada
```bash
git fetch origin
git rebase origin/main
```

### 4. Push y crear Pull Request
```bash
git push origin feature/nueva-funcionalidad
```

**Commit messages recomendados:**
- `feat:` nueva funcionalidad
- `fix:` corrección de bug
- `docs:` cambios en documentación
- `test:` añadir/modificar tests
- `chore:` cambios en build, deps, etc.
- `refactor:` refactorización sin cambio de funcionalidad

## Escribir Tests

### Estructura básica
```python
import pytest
from src.ingesta.encoding import enc_preprocessor

class TestEncoding:
    def setup_method(self):
        """Configuración antes de cada test"""
        self.sample_data = {...}
    
    def test_encoding_basic(self):
        """Test simple de encoding"""
        result = enc_preprocessor(self.sample_data)
        assert result is not None
    
    @pytest.mark.integration
    def test_encoding_with_db(self):
        """Test de integración con BD"""
        result = enc_preprocessor(self.sample_data)
        assert result["status"] == "success"
```

### Fixtures comunes
```python
@pytest.fixture
def sample_dataframe():
    """Fixture de dataframe de ejemplo"""
    import pandas as pd
    return pd.DataFrame({
        'age': [25, 30, 35],
        'balance': [100, 200, 300]
    })
```

## Reproducibilidad

### Generar requirements.txt actualizado
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: actualizar dependencies"
```

### Instalar desde requirements.txt
```bash
pip install -r requirements.txt
```

### Generar ambiente reproducible con conda (opcional)
```bash
conda create -n banco-x python=3.11
conda activate banco-x
pip install -r requirements.txt
```

## Gestión de Modelos

Los modelos entrenados (`.pkl`, `.joblib`) NO se versionan. Usar MLflow para tracking:

```bash
# Ver experimentos
mlflow ui

# Los artefactos se guardan en mlruns/ o en servidor remoto
```

## Docker

### Build de imagen
```bash
docker build -t banco-x-detector:latest .
```

### Ejecutar con docker-compose
```bash
docker-compose up
```

## Ignorar archivos sensibles

- `.env` - Variables de entorno (nunca commitar)
- `*.key`, `*.pem` - Claves privadas
- Modelos grandes (`.pkl`)
- Bases de datos SQLite/MLflow (`*.db`)

Ver `.gitignore` para lista completa.

## Documentación

Mantener `docs/` actualizado:
- `DATA_DICTIONARY.md` - Descripción de variables
- `model_card.md` - Especificación del modelo
- `RUNBOOK.md` - Guía operacional

## Ayuda

- Issues de GitHub: Reportar bugs / solicitar features
- Documentación: Ver `README.md` y carpeta `docs/`
- Contacto: dev@bancox.com

---

¡Gracias por contribuir!
