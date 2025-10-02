# Prueba de Concepto (PoC) - Detección de Clientes Suscritos

## Objetivo
Evaluar la viabilidad de predecir la suscripción de clientes a un depósito bancario utilizando modelos de clasificación supervisada. Se busca identificar patrones y características relevantes que permitan segmentar clientes potenciales para campañas de marketing.

## Configuración
- **Dataset:** bank-additional-full.csv
- **Modelos:** Regresión Logística (baseline) y Random Forest (PoC)
- **Preprocesamiento:**
	- Codificación y escalado de variables
	- Ingeniería de características (contactosTotales, campañasExitosasPrevias)
	- Codificación de variables categóricas (target mean, one-hot, frecuencia, ordinal)
	- Discretización de variables numéricas
	- Balanceo de la variable objetivo con SMOTE
- **Evaluación:** Métricas de accuracy, recall, precision, f1-score, ROC-AUC, matriz de confusión
- **Herramientas:** scikit-learn, imbalanced-learn, mlflow

## Resultados
- El modelo baseline (regresión logística) mostró buen accuracy, pero baja precisión y sensibilidad debido al desbalance de clases.
- El modelo Random Forest, tras aplicar SMOTE, logró mejorar la precisión y sensibilidad, alcanzando métricas superiores al 90% en accuracy y precision para la clase "yes".
- La matriz de confusión mostró menos de 1000 predicciones incorrectas, con 246 falsos negativos y 679 falsos positivos.
- El modelo fue registrado y evaluado con MLflow.

## Conclusión breve
El experimento demuestra que es viable implementar un modelo predictivo para identificar clientes potenciales de suscripción bancaria. El balanceo de clases y la ingeniería de características mejoran significativamente el desempeño. Se recomienda enfocar futuras campañas en segmentos identificados por el modelo y continuar optimizando el pipeline de datos y modelos.
