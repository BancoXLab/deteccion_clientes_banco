# Imagen base ligera
FROM python:3.12-slim

# Establecer directorio de trabajo
ENV PYTHONPATH="/app"

WORKDIR /app

# Copiar requirements primero (para aprovechar cache de Docker)
COPY scr/app/requirements.txt .
RUN python -m venv venv

# Instalar dependencias
RUN /bin/bash -c "source venv/bin/activate"
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la app
COPY . .

# Exponer el puerto donde correrá FastAPI (8000 recomendado)
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main_orq:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
