# Error analysis — informe

Resumen ejecutivo
- Fecha: 06/11/2025
- Pipeline / componente: API de predicción / validación de entrada
- Métrica afectada: Tasa de errores 422, calidad de datos, robustez del endpoint

Análisis
- Síntoma: Se reciben errores 422 al enviar datos fuera de rango o con tipos incorrectos al endpoint /predict.
- Logs relevantes:
  - Ejemplo de error controlado por validación automática:
    ```
    422 Unprocessable Entity: age debe estar entre 0 y 120, month entre 1 y 12, day_of_week entre 1 y 7, duration >= 0, etc.
    ```
- Slices afectadas (por feature / cohort): Usuarios con edad fuera de rango, meses inválidos, días de la semana incorrectos.

Acciones recomendadas (priorizadas)
1. Implementar validaciones automáticas en los endpoints usando Pydantic (`Field(ge=0, le=120)`, etc.) para asegurar que los datos de entrada cumplen los rangos y tipos esperados. Impacto alto / coste bajo — Evita errores en el pipeline y mejora la calidad de los datos procesados.
2. Documentar los errores 422 generados por datos inválidos en los logs y reportes.
3. Revisar y actualizar los tests para cubrir casos de datos fuera de rango y tipos incorrectos.

Evidencia / next steps
- Issues a crear:
  - Añadir validaciones de rango y tipo en los modelos de entrada de la API (Pydantic).
  - Documentar los errores 422 generados por datos inválidos en los logs y reportes.
  - Revisar cobertura de tests para validaciones automáticas.
- Owner: Equipo de backend/API