# Data Card - Bank Marketing Dataset (BancoX)

## Overview
Breve descripción: Conjunto de datos usado para modelar la suscripción de clientes a depósitos a término (variable objetivo `y`). El repositorio utiliza la versión del UCI Bank Marketing Dataset combinada con transformaciones internas en los notebooks y scripts.

## Provenance
- Fuente original: UCI Machine Learning Repository – Bank Marketing (https://archive.ics.uci.edu/dataset/222/bank+marketing).
- Fecha de adquisición: especificada por el autor del notebook; el dataset se descarga/usa localmente en los notebooks y scripts del repositorio.
- Contacto del repositario: equipo BancoXLab (ver sección Equipo en README).

## Composition
- Tipos de datos: mezclas de variables numéricas (ej. `age`, `balance`, `campaign`, `previous`, `pdays`) y categóricas (ej. `job`, `marital`, `education`, `housing`, `loan`, `contact`, `poutcome`).
- Columnas principales encontradas en el repo/notebooks:
  - age, job, marital, education, default (si aplica), balance, housing, loan, contact, day, month, duration, campaign, pdays, previous, poutcome, y
- Tamaño del dataset: la versión pública típica contiene ~45211 registros; en este repo se utiliza la versión base/transformada desde los notebooks (ver outputs generados como `clientes_segmentados.csv`). Re-ejecutar los notebooks para confirmar tamaño exacto.

## Sensitive Attributes
- Atributos que podrían ser sensibles o dar lugar a sesgos: `age`, `job`, `education`, `marital`.
- Recomendación: analizar métricas por subgrupos y, si se usan decisiones automatizadas, aplicar mitigaciones de sesgo.

## Collection Process
- Procedencia: datos de campañas de telemarketing reales (origen UCI). En este repo los datos se usan para entrenamiento y análisis exploratorio en notebooks (`MVP+Dashboard.ipynb`).
- Modo de recolección original: interacciones de campañas con clientes, colectadas por la entidad que publicó el dataset.

## Preprocessing Applied in Repo
- Limpieza de outliers en variables numéricas.
- Codificación de variables categóricas (one-hot o label encoding según variable y uso en el pipeline).
- Escalado / normalización en features numéricos cuando corresponde.
- Balanceo del dataset con SMOTE en el set de entrenamiento.
- Reducción de dimensionalidad mediante PCA (opcional según configuración del pipeline).
- División de datos: entrenamiento/test 80/20 según scripts/notebooks.

## Uses
- Usos actuales en el repo: entrenamiento de un clasificador (XGBoost) para predecir suscripción a depósitos, análisis de ROI estimado, generación de dashboards y segmentación de clientes.
- Usos recomendados: priorización de clientes para campañas con intervención humana; análisis exploratorio; prototipado de modelos.
- Usos no recomendados: decisiones automatizadas que afecten derechos o condiciones de clientes sin revisión humana ni control de sesgos.

## Distribution & Maintenance
- Licencia y acceso: dataset original sujeto a los términos de la UCI; el repo incluye scripts para reproducir el pipeline localmente. Ver README para más detalles.
- Actualizaciones: los notebooks y scripts deben re-ejecutarse para regenerar artefactos si se actualiza la fuente de datos. Mantener versión de los modelos y datasets en MLflow o control de versiones.

## Limitations & Quality
- Limitaciones conocidas: posible sesgo por distribución de edad, ocupación y educación; registros con valores especiales para `pdays` (ej. 999) que requieren tratamiento.
- Calidad: datos de logs de campañas reales, pero pueden contener ruido o registros incompletos. Se aplican pasos de limpieza en el pipeline.

## Recommended Evaluation
- Evaluar métricas por subgrupos (age buckets, job, education).
- Mantener trazabilidad con MLflow y guardar `metrics.csv` y artefactos del entrenamiento.

## Contact
- Equipo: Juan Acciardi, Javier Balda, Juan Caracoix, Facundo Casas, Agustín Giannice (ver README).