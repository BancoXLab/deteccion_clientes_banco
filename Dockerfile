FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Copiar requerimientos
COPY ./requirements.txt /app/app/requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade -r /app/app/requirements.txt


COPY ./app/app /app/app

# Establecer directorio de trabajo
WORKDIR /app/app

# Exponer puerto
EXPOSE 80
