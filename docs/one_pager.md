# Título del proyecto: “Predicción de suscripción a depósitos a plazo en clientes bancarios”

*Problema/Usuario* : El banco necesita identificar qué clientes tienen mayor probabilidad de contratar un depósito, para optimizar campañas comerciales.

*Valor/Impacto esperado*: Mejorar la efectividad de las campañas → más conversión con menos costo.

*Alcance del cuatrimestre*: Entrenar y entregar un MVP reproducible que clasifique clientes (Sí / No depósito). **Fuera de alcance**: despliegue en producción real, integración con sistemas core bancarios.

*Stakeholders y canal de feedback*:

    * Marketing (usuarios principales del modelo)

    * Riesgos/Compliance (PII y sesgos)
    
    * Data Team (ingesta y features)

*Datos disponibles y brecha*: dataset bancario de campañas de marketing (atributos socio-demográficos + comportamiento). Posibles faltantes: frescura de datos, balance de clases.

*Riesgos principales (3) + mitigación inicial (se vincula a la matriz de riesgos)*:

    * Datos desbalanceados → mitigación: oversampling/undersampling.

    * PII/privacidad → mitigación: anonimización/tokenización.

    * Sesgos en el modelo → mitigación: métricas fairness + revisión de features.

*KPIs de éxito (SMART)*:

    * F1 ≥ 0.72 para campaña de validación al 30/09/2025.

    * Latencia ≤ 1s por predicción en entorno de prueba.

    * 2 analistas de marketing usando el modelo en demo al 31/10/2025.