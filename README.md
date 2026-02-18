# Predicción de Suscripción de Clientes a Depósitos Bancarios

Este proyecto tiene como objetivo desarrollar un modelo de machine learning que prediga si un cliente aceptará una oferta de suscripción a un depósito a término, utilizando datos históricos de[...] 

---

## Objetivo del Proyecto

BancoX enfrenta dificultades para optimizar recursos en sus campañas de marketing directo (llamadas telefónicas) dirigidas a promover depósitos a término. Este proyecto busca:

- Identificar clientes con mayor probabilidad de aceptar la oferta.
- Reducir costos operativos al optimizar el targeting de las campañas.
- Implementar un sistema de monitoreo y evaluación del modelo predictivo.

---

## Conjunto de Datos

Se utilizaron distintos conjuntos de datos que contienen información demográfica, financiera y de comportamiento de los clientes, como:

- Edad, ocupación, estado civil, nivel educativo.
- Saldo medio anual, créditos previos, tipo de contacto.
- Número de llamadas realizadas, resultado de campañas anteriores.
- Variable objetivo: si el cliente se suscribió (`y`: "yes"/"no").

El dataset principal proviene de [UCI Machine Learning Repository – Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing).

---

## Enfoque

1. **Modelado predictivo**:
   - División 80/20 para entrenamiento/test.
   - Entrenamiento de un modelo de clasificación (`XGBClassifier`).
   - Evaluación mediante métricas como `precision`, `recall`, `f1-score`, `ROC AUC`.

2. **Motor de Clasificación: `mvp_para_frontend.py`**
Incluye:
- Preprocesamiento (outliers, codificación, reducción de dimensionalidad con PCA).
- Balanceo de clases con `SMOTE`.
- Entrenamiento y predicción con `XGBoost`.

3. **Interfaz Gráfica: `frontend.py`**
Streamlit app que permite:
- Ejecutar todo el pipeline con un solo botón.
- Visualizar los mejores candidatos (clientes ordenados por probabilidad).
- Fácil despliegue local.

4. **Exportación de resultados**:
   - CSVs con métricas, predicciones, probabilidades, curvas ROC/PR.
   - Cálculo de ROI estimado antes y después del modelo.
   - Generación de tabla segmentada de clientes predichos como aceptantes.

5. **Desarrollo de Dashboard**:
   - Dashboard interactivo con `Streamlit` para monitoreo del modelo.
   - Visualización de métricas, análisis por segmento y seguimiento del entrenamiento.
   - Curvas ROC y PR.
   - Análisis de clientes predichos como positivos.
   - Comparación de ROI antes/después del modelo.

---

## Herramientas y Tecnologías

- **Python 3.11**
- `pandas`, `scikit-learn`, `numpy`, `seaborn`, `scipy`, `imbalanced-learn`, `matplotlib`, `xgboost`, `plotly`, `streamlit`
- **Google Colab** para prototipado
- **Streamlit** para interfaz de dashboard
- **Google Drive** para almacenamiento de resultados
- **CSV** como formato estándar de salida
- **Metodología**: Agile (entrega continua, enfoque iterativo)
- **Preprocesamiento**:
  - Codificación de variables categóricas
  - Detección y remoción de outliers
  - SMOTE + PCA

---

## Resultados

- **Precisión del modelo:** ~92%
- **ROC AUC:** ~0.95
- **Mejora estimada en ROI**: se identifican segmentos de clientes con tasas de aceptación significativamente mayores.
- **Dashboard de seguimiento** permite monitoreo continuo y análisis por segmento.
- **Reducción de llamadas innecesarias**
- **Identificación clara de segmentos de clientes más receptivos**

---

## Instrucciones de uso

### Requisitos
Instalar las dependencias con:
```bash
pip install -r requirements.txt
# o, si no existe requirements.txt:
pip install streamlit pandas numpy scikit-learn imbalanced-learn xgboost plotly mlflow uvicorn fastapi
```

### Opción 1: Interfaz de Streamlit (Recomendado para usuarios)
La aplicación incluye una interfaz web moderna construida con **Streamlit** que permite:
- Hacer predicciones individuales en tiempo real
- Procesar lotes de clientes desde un CSV
- Visualizar resultados con gráficos interactivos
- Descargar resultados

**Instalación de dependencias:**
```bash
pip install -r requirements.txt
```

**Ejecutar la interfaz:**
```bash
# En Linux/Mac
./run_streamlit.sh

# O directamente
streamlit run streamlit_app.py

# En Windows
run_streamlit.bat
```

La aplicación se abrirá en `http://localhost:8501`

Para más información, consulta [STREAMLIT_README.md](STREAMLIT_README.md)

### Opción 2: Dashboard de MLflow (Para analistas)
1. Ejecutar el notebook `MVP+Dashboard.ipynb` para generar los archivos base (`metrics.csv`, `clientes_segmentados.csv`, etc.).
2. Ejecutar el dashboard con:
```bash
streamlit run dashboard_seguimiento.py
# o
streamlit run frontend.py
```

### API con Docker (ejecución recomendada)
Si la API está empacada en la imagen Docker del repositorio, estos son los comandos para construirla y ejecutarla localmente (se incluyen tal cual):

```bash
docker rm banco-x-api
docker build -t banco-x-api .
docker run -d --name banco-x-api -p 8000:8000 banco-x-api
docker ps
```

- La API quedará expuesta en http://localhost:8000 (puerto por defecto en estos ejemplos).
- Ajusta el puerto o nombre del contenedor según necesites.

### Ejemplo de request (curl / batch)
A continuación se muestran ejemplos típicos de requests que la API suele exponer en implementaciones de este tipo. Si los endpoints difieren en tu código (por ejemplo otro path o puerto), reemplaza las rutas a continuación por las correctas.

- Request simple (predicción individual)
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "job": "technician",
    "marital": "married",
    "education": "tertiary",
    "balance": 1500,
    "housing": "yes",
    "loan": "no",
    "contact": "cellular",
    "campaign": 1,
    "pdays": 999,
    "previous": 0,
    "poutcome": "nonexistent"
  }'
```

Respuesta esperada (ejemplo):
```json
{
  "y_pred": "no",
  "probability": 0.12,
  "score": 0.12
}
```

- Request batch (subida de CSV)
Si la API soporta procesamiento por lotes, habitualmente se ofrece un endpoint tipo `/batch` que acepta multipart/form-data con un CSV:

```bash
curl -X POST "http://localhost:8000/batch" \
  -H "Accept: application/json" \
  -F "file=@clientes_para_predecir.csv"
```

Respuesta esperada (ejemplo): un archivo CSV con las columnas originales + `y_pred` y `probability`, o un JSON con un enlace al resultado almacenado.

Si tu implementación utiliza otro formato (por ejemplo envío de lista JSON), reemplaza el ejemplo por el formato correcto.

---

## Referencia a MLflow y métricas

El proyecto usa (o puede integrarse con) MLflow para tracking de experimentos y métricas. Recomendaciones y comandos para trabajar con MLflow:

- Si se guarda localmente, los runs quedan en `./mlruns` por defecto.
- Para visualizar el UI de MLflow localmente:
```bash
mlflow ui --backend-store-uri ./mlruns --port 5000
# luego abrir http://localhost:5000
```

- Métricas típicas registradas:
  - accuracy
  - precision
  - recall
  - f1_score
  - roc_auc
  - loss / log_loss
  - tiempo de entrenamiento, tamaño del set de entrenamiento, hiperparámetros usados

- Artefactos típicos:
  - modelo serializado (pickle / joblib / MLflow model)
  - curvas ROC/PR (png / html)
  - CSVs con predicciones y métricas (por ejemplo `metrics.csv`)

- Si se usa un servidor de tracking remoto, configurar:
```bash
export MLFLOW_TRACKING_URI=http://mlflow-server:5000
```

Incluye en la ejecución del pipeline las llamadas a `mlflow.log_param`, `mlflow.log_metric` y `mlflow.log_artifact` para asegurar que todo queda trazable.

---

## Referencias
 - Dataset base: [UCI Bank Marketing Dataset](https://archive.ics.uci.edu/dataset/222/bank+marketing)
 - Presentación ejecutiva: propuesta_trabajo_(Revision).pptx

## Solución rápida de predicciones

Si la API está retornando siempre Clase 0, sigue la guía rápida en:

- [docs/SOLUCION_RAPIDA_PREDICCIONES.md](docs/SOLUCION_RAPIDA_PREDICCIONES.md)

Scripts relevantes (migrados a `src/`):

- Diagnóstico: `python src/scripts/debug_predictions.py`
- Correcciones rápidas / retrain wrappers: `python src/scripts/fix_predictions.py`
- Reentrenamiento: `python src/training/retrain_model.py` y `python src/training/train_xgboost_model.py`

Ejecuta los scripts desde el root del proyecto. Ejemplo:

```bash
python src/scripts/fix_predictions.py --quick
docker-compose restart bancox-api
```

---

## Equipo
 - Juan Acciardi – juanacciardi@uca.edu.ar
 - Javier Balda – javierbalda@uca.edu.ar
 - Juan Caracoix – juancaracoix@uca.edu.ar
 - Facundo Casas – facundocasas@uca.edu.ar
 - Agustín Giannice – agustingiannice@uca.edu.ar

---

## Licencia

Este proyecto fue desarrollado con fines educativos y de prueba de concepto. Su uso en producción debe contemplar los aspectos regulatorios y éticos correspondientes al manejo de datos personal[...]