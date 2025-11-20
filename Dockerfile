# Imagen base ligera
FROM python:3.12-slim

# Establecer directorio de trabajo
ENV PYTHONPATH="/app"
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app

# Copiar código primero
COPY . .

# Copiar requirements.lock (tiene todas las dependencias pinned)
COPY requirements.lock .

# Crear venv e instalar dependencias en una sola capa
RUN python -m venv venv && \
    venv/bin/pip install --no-cache-dir --upgrade pip && \
    venv/bin/pip install --no-cache-dir -r requirements.lock

# Exponer el puerto donde correrá FastAPI
EXPOSE 8000

# Comando de inicio - usar ruta absoluta a uvicorn
CMD ["/app/venv/bin/uvicorn", "scr.app.main_orq:app", "--host", "0.0.0.0", "--port", "8000"]
