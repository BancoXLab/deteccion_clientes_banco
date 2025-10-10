FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Copiar requerimientos
COPY ./app/requirements.txt /app/requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copiar la aplicación
COPY ./app /app

# Establecer directorio de trabajo
WORKDIR /app

# Exponer puerto
EXPOSE 80
