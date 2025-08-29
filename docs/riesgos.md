# Matriz de Riesgos Inicial

| ID  | Riesgo                          | Prob. | Impacto | RAG  | Dueño  | Mitigación                                         | Fecha |
|-----|---------------------------------|-------|---------|------|--------|----------------------------------------------------|-------|
| R1  | Dataset desbalanceado           | M     | A       | 🔴   | DS     | Rebalanceo con SMOTE/undersampling + PR-AUC        | S4    |
| R2  | Datos sensibles (PII)           | M     | A       | 🟠   | DE     | Anonimización/Hash, DLP                            | S4    |
| R3  | Calidad de datos (nulos/dups)   | M     | M       | 🟠   | DE     | Profiling + limpieza inicial                       | S4    |
| R4  | Sesgo en variables socio-demo   | B     | A       | 🟠   | DS/PO  | Métricas fairness + exclusión si aplica            | S6    |
| R5  | Infraestructura limitada        | M     | M       | 🟡   | TL     | Optimizar librerías, usar muestreo inicial         | S5    |
| R6  | Generación de datos sinteticos  | B     | M       | 🟡   | DS/DE  | Validar representatividad; SMOTE      | S5    |
| R7  | Conexión pipeline y dependencias| M     | A       | 🔴   | DE/TL  | Tests de integración, CI/CD con validación de flujo    | S6    |
| R8  | Método visualización al usuario | M     | M       | 🟠   | PO/DS  | Prototipo temprano con feedback de marketing         | S8    |