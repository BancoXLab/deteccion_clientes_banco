# Imagen base ligera
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para aprovechar cache de Docker)
COPY ./scr/app/requirements.txt /app/requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# Copiar todo el código de la app
COPY ./scr/app /app

# Exponer el puerto donde correrá FastAPI (8000 recomendado)
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main_orq:app", "--host", "0.0.0.0", "--port", "8000"]
