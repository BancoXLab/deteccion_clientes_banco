# Imagen base con Jupyter y Python 3.11
FROM jupyter/scipy-notebook:python-3.11

# Evitar que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear carpeta de trabajo
WORKDIR /home/jovyan/work

# Copiar archivo de dependencias
COPY requirements_dock.txt .

# Instalar dependencias con pip
RUN pip cache purge
RUN pip install --upgrade pip
RUN pip install --no-cache-dir numpy pandas matplotlib
RUN pip install --no-cache-dir -r requirements_dock.txt

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto de Jupyter
EXPOSE 8888

# Comando por defecto
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--NotebookApp.token=''", "--NotebookApp.password=''"]
