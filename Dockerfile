FROM python:3.12-slim

WORKDIR /app

# Copiar código (ajusta si tus requirements están en otra ruta)
COPY ./scr/app /app
# Si tienes requirements en scr/app/requirements.txt
COPY ./scr/app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
 && if [ -f /app/requirements.txt ]; then pip install --no-cache-dir -r /app/requirements.txt; fi

EXPOSE 80

# Ejecuta el módulo según la ubicación real: scr.app.main:app (porque copiamos scr/app a /app)
CMD ["uvicorn", "scr.app.main:app", "--host", "0.0.0.0", "--port", "80"]