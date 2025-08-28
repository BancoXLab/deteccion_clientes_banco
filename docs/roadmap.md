# Roadmap del Proyecto

Este roadmap describe la planificación de alto nivel del proyecto, con hitos principales (H1–H4) y entregables semanales.  
El objetivo es llegar a un **MVP reproducible y defendible** en 14 semanas, siguiendo la metodología ágil.

---

## Hitos principales

- **H1 (S4): Baseline + Data Readiness**  
- **H2 (S7): Demo v0**  
- **H3 (S11): Feature Complete**  
- **H4 (S14): Entrega Final**

---

## Plan semana a semana

| Semana | Entregable principal | Dependencias | Hito |
|--------|----------------------|--------------|------|
| **S1** | OnePager + Matriz de riesgos inicial + repo/tablero | – | – |
| **S2** | Alcance MVP v1 + Top-10 historias priorizadas (t-shirt sizing) | S1 | – |
| **S3** | Roadmap + 2 ADRs + Diagrama de arquitectura | S1–S2 | – |
| **S4** | Data Readiness Report (profiling + diccionario + sesgos) + Baseline inicial | S3 | **H1** |
| **S5** | Baseline reproducible + Plan de experimentación + tracking de métricas | S4 | – |
| **S6** | Pipeline reproducible (1 comando: entrenamiento completo) | S5 | – |
| **S7** | Demo v0 (flujo end-to-end mínimo con métricas) | S4–S6 | **H2** |
| **S8** | Producto & API/batch stub con ejemplo de predicción | S7 | – |
| **S9** | Dockerfile + CI/CD mínima (GitHub Actions) | S8 | – |
| **S10** | Error analysis + Informe con 3 acciones priorizadas | S7–S9 | – |
| **S11** | Feature complete en staging (flujo validado, stress test) | S7–S10 | **H3** |
| **S12** | Runbook + Monitoreo (SLOs y alerta simulada) | S11 | – |
| **S13** | Documentación final (README ejecutable + Model/Data Cards) | S12 | – |
| **S14** | Demo final + Retro final (lecciones aprendidas, próximos pasos) | S11–S13 | **H4** |

---

## Notas
- Cada entregable tiene un **Definition of Done (DoD)** definido en su documento correspondiente.  
- Los riesgos se revisan semanalmente y se actualiza la matriz (`docs/riesgos.md`).  
- Los commits se etiquetan por semana: `S1`, `S2`, …, `S14`.  
- Este roadmap es **iterativo**: puede ajustarse según feedback y hallazgos en cada fase.  
