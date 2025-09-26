FROM python:3.12 as builder

WORKDIR /app

# x-release-please-start-version
ARG PREFIX="interflow_backend-0.0.0"
# x-release-please-end

# Copie des fichiers nécessaires pour construire le wheel
COPY pyproject.toml README.md ./

COPY src/ ./src/

# Installation des dépendances de build et construction du wheel
RUN pip install --no-cache-dir build wheel setuptools
RUN python -m build --wheel

# Deuxième étape: installation et exécution
FROM python:3.12-slim

WORKDIR /app

# x-release-please-start-version
ARG PREFIX="interflow_backend-0.0.0"
# x-release-please-end

# Copie du wheel depuis l'étape de build
COPY --from=builder /app/dist/${PREFIX}-py3-none-any.whl ./

# Installation du wheel
RUN pip install --no-cache-dir --upgrade ${PREFIX}-py3-none-any.whl

# Création d'un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exposition du port pour uvicorn
EXPOSE 5000

# Variables d'environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=5000

# Commande de démarrage
CMD ["run_api"]
