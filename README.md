# Predicción de Suscripción de Clientes a Depósitos Bancarios

Este proyecto tiene como objetivo desarrollar un modelo de machine learning que prediga si un cliente aceptará una oferta de suscripción a un depósito a término, utilizando datos históricos de campañas de marketing telefónico de una institución financiera.

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
``bash
pip install streamlit pandas numpy scikit-learn imbalanced-learn xgboost plotly

1. Ejecutar el notebook `MVP+Dashboard.ipynb` para generar los archivos base (`metrics.csv`, `clientes_segmentados.csv`, etc.).
2. Ejecutar el dashboard con:
   ```bash
   streamlit run dashboard_seguimiento.py
   streamlit run frontend.py

---

## Referencias
   - Dataset base: [UCI Bank Marketing Dataset](https://archive.ics.uci.edu/dataset/222/bank+marketing)
   - Presentación ejecutiva: propuesta_trabajo_(Revision).pptx

---

## Equipo
   - Juan Acciardi – juanacciardi@uca.edu.ar
   - Javier Balda – javierbalda@uca.edu.ar
   - Juan Caracoix – juancaracoix@uca.edu.ar
   - Facundo Casas – facundocasas@uca.edu.ar
   - Agustín Giannice – agustingiannice@uca.edu.ar
   
---

## Licencia

Este proyecto fue desarrollado con fines educativos y de prueba de concepto. Su uso en producción debe contemplar los aspectos regulatorios y éticos correspondientes al manejo de datos personales.
