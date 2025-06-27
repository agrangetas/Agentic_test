FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VERSION=1.7.1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN pip install poetry==$POETRY_VERSION

# Répertoire de travail
WORKDIR /app

# Copie des fichiers de configuration Poetry
COPY pyproject.toml poetry.lock* ./

# Configuration Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copie du code source
COPY . .

# Création des dossiers nécessaires
RUN mkdir -p logs config

# Exposition du port
EXPOSE 8000

# Commande par défaut
CMD ["python", "-m", "orchestrator.main"] 