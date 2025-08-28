# Matriz de Riesgos Inicial

| ID  | Riesgo                          | Prob. | Impacto | RAG  | Dueño  | Mitigación                                         | Fecha |
|-----|---------------------------------|-------|---------|------|--------|----------------------------------------------------|-------|
| R1  | Dataset desbalanceado           | M     | A       | 🔴   | DS     | Rebalanceo con SMOTE/undersampling + PR-AUC        | S4    |
| R2  | Datos sensibles (PII)           | M     | A       | 🟠   | DE     | Anonimización/Hash, DLP                            | S4    |
| R3  | Calidad de datos (nulos/dups)   | M     | M       | 🟠   | DE     | Profiling + limpieza inicial                       | S4    |
| R4  | Sesgo en variables socio-demo   | B     | A       | 🟠   | DS/PO  | Métricas fairness + exclusión si aplica            | S6    |
| R5  | Infraestructura limitada        | M     | M       | 🟡   | TL     | Optimizar librerías, usar muestreo inicial         | S5    |
