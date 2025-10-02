# Experimento 02: Random Oversampling

## Objetivo
Evaluar el impacto de la técnica de Random Oversampling en el balanceo de la variable objetivo y el desempeño de modelos de clasificación para la detección de clientes potenciales.

## Configuración
- **Notebook:** EDA_(Avanzado)_Grupo1 V.2 .ipynb
- **Dataset:** bank-additional-full.csv
- **Técnica:** Random Oversampling para balancear la clase minoritaria
- **Modelos:** Random Forest
- **Preprocesamiento:**
  - Limpieza y análisis exploratorio de datos
  - Codificación de variables categóricas
  - Escalado de variables numéricas
  - Aplicación de Random Oversampling
- **Evaluación:** Métricas de accuracy, recall, precision, f1-score, matriz de confusión

## Resultados
- Se logró balancear la variable objetivo, aumentando la proporción de la clase minoritaria.
- El modelo entrenado sobre el conjunto balanceado mostró mejoras en sensibilidad y precisión para la clase minoritaria.
- Se observó un posible aumento en el riesgo de overfitting, por lo que se recomienda validar con técnicas adicionales.

## Conclusión breve
Random Oversampling permite mejorar la detección de clientes potenciales en datasets desbalanceados, pero debe aplicarse con precaución para evitar sobreajuste. Es recomendable comparar con otras técnicas de balanceo y validar los resultados en datos no vistos.