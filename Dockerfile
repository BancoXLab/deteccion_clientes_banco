# Imagen base con Python
FROM python:3.10-slim

# Evitar que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias básicas
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar requirements.txt e instalar dependencias
COPY requirements_dock.txt .
RUN pip install --no-cache-dir -r requirements_dock.txt

# Copiar el proyecto (incluido tu notebook)
COPY . .

# Exponer puerto para Jupyter
EXPOSE 5000

# Comando por defecto: lanzar Jupyter
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=5000", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
