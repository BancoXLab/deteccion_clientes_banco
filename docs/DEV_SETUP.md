# Desarrollo y despliegue local

Este documento recoge pasos mínimos para levantar el proyecto localmente con Docker Compose y cómo usar el contenedor `prefect` añadido.

Requisitos
- Docker y Docker Compose
- Variables de entorno: copia `.env.example` a `.env` y ajusta los valores.

Levantar la pila:

```bash
# Construir imágenes
docker compose build

# Levantar servicios en background
docker compose up -d

# Ver logs del API
docker compose logs -f bancox_api
```

Prefect (ejecutar desde el contenedor `bancox_prefect`):

```bash
# Abrir shell en el contenedor
docker compose exec bancox_prefect /bin/sh

# Ver la versión instalada de prefect
/app/venv/bin/prefect --version

# Ejemplos de comandos (ajustar según la versión de Prefect 3):
# - Construir y aplicar un deployment
/app/venv/bin/prefect deployment build --name train-pipeline src/training/train_pipeline:train_pipeline
/app/venv/bin/prefect deployment apply ./train-pipeline-deployment.yaml

# - Iniciar un agente para ejecutar deployments
/app/venv/bin/prefect agent start

# Si prefieres Prefect Cloud, configura las variables de entorno necesarias y ejecuta el agente con autenticación.
```

Prometheus / Grafana
- `docker-compose.yml` incluye servicios opcionales `prometheus` y `grafana`.
- El archivo de configuración Prometheus está en `config/prometheus.yml` y ya apunta a `alert-server:9000` y `monitor` (puerto 8002).

Notas
- Para integrar Redis, MailHog o Grafana con dashboards, configura sus puertos y variables desde `.env`.
- Si prefieres que Prefect arranque automáticamente, puedo actualizar `docker-compose.yml` para ejecutar el comando de servidor/agent al iniciar (indica la versión exacta de Prefect si quieres esto automatizado).
