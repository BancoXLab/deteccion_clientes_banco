# Documentación de supuestos, decisiones y riesgos del proyecto

## Contexto del proyecto
En este proyecto trabajamos con un conjunto de datos de campañas telefónicas de un banco, donde el objetivo es predecir qué clientes tienen mayor probabilidad de suscribirse a un depósito a plazo.

## Supuestos del proyecto
- **Calidad de los datos**: asumimos que los datos provistos son completos y representativos del comportamiento histórico del cliente.
- **Estabilidad temporal**: asumimos que los patrones del pasado (años anteriores) se mantendrán en el futuro cercano.
- **Definición de variable objetivo**: asumimos que la variable `y` es un reflejo fiel de si el cliente realmente se suscribió o no.

## Riesgos y problemas identificados
- **Desbalance de clases**: la clase "no" es mayoritaria (~89%). Esto puede sesgar los modelos a predecir siempre "no".
- **Sesgos temporales**: los datos incluyen un fuerte componente estacional por `month`.
- **Outliers y datos atípicos** en variables numéricas como `duration` y `balance`.
- **Multicolinealidad** entre variables económicas (`euribor3m`, `nr.employed`, `emp.var.rate`), que puede afectar a modelos lineales.

## Decisiones tomadas
- **Selección de modelos**:
  - Iniciamos con un baseline (Logistic Regression) por su interpretabilidad.
  - Evaluamos también modelos avanzados como `CatBoost` y `LightGBM` por su buen desempeño en datos tabulares.
- **Tratamiento del desbalance**:
  - Evaluamos técnicas como `SMOTE`, `RandomOverSampler` y ajuste de pesos en los modelos.
- **Transformación de variables categóricas**:
  - Usamos `pd.get_dummies()` para variables categóricas simples.
  - Mantenemos variables ordinales (ej. `education`) sin transformación excesiva para probar su efecto.
- **Manejo del tiempo**:
  - Conservamos variables temporales (`month`, `day_of_week`) ya que muestran correlación con el target.
- **Métricas de evaluación**:
  - Escogimos `ROC AUC` y `PR AUC` por su robustez en problemas desbalanceados.
  - También evaluamos `Precision`, `Recall` y `F1-score` para comprender mejor el trade-off entre falsos positivos y falsos negativos.

## Riesgos mitigados
- **Desbalance**: balanceamos mediante técnicas de remuestreo y también ajustamos `class_weight='balanced'` en algunos modelos.
- **Sobreajuste**: validamos mediante un split train/test 70/30 y `cross_val_score` en modelos más complejos.
- **Explicabilidad**: mantenemos modelos interpretables en paralelo a los complejos para que el negocio entienda qué factores influyen.

## Siguientes pasos
- Analizar impacto de nuevas fuentes de datos (e.g. datos socioeconómicos externos).
- Implementar un pipeline robusto en producción que incluya preprocesamiento + predicción en tiempo real.
- Construir un dashboard para monitoreo continuo del desempeño del modelo en nuevos datos y ajuste proactivo cuando cambie la distribución.

---

*Última actualización:* 2025-06-24
