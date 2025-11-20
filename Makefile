.PHONY: train streamlit streamlit-install api help

train:
	jupyter nbconvert --to notebook --execute models/baseline.ipynb --output baseline_output.ipynb --output-dir=models

# Instalar dependencias de Streamlit
streamlit-install:
	pip install -r requirements.txt

# Ejecutar la interfaz de Streamlit
streamlit:
	streamlit run streamlit_app.py

# Ejecutar la API
api:
	python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload

# Ejecutar API con Docker
api-docker:
	docker-compose up -d
	@echo "✅ API ejecutándose en http://localhost:8000"

# Ver logs de la API en Docker
api-logs:
	docker-compose logs -f

# Detener API en Docker
api-stop:
	docker-compose down

# Ayuda
help:
	@echo "Comandos disponibles:"
	@echo "  make train             - Ejecutar entrenamiento del modelo"
	@echo "  make streamlit-install - Instalar dependencias de Streamlit"
	@echo "  make streamlit         - Ejecutar interfaz de Streamlit"
	@echo "  make api               - Ejecutar API localmente"
	@echo "  make api-docker        - Ejecutar API en Docker"
	@echo "  make api-logs          - Ver logs de la API en Docker"
	@echo "  make api-stop          - Detener API en Docker"
	@echo "  make help              - Mostrar esta ayuda"
