# Image de MaintAI : code et bibliothèques, sans données ni modèle.
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances séparément pour profiter du cache Docker.
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copier le code après les bibliothèques.
COPY maintai ./maintai
COPY ui ./ui

ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

EXPOSE 8000
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
