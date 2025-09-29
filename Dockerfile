# Étape 1: Build du frontend Next.js
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copier les fichiers de dépendances du frontend
COPY interflow-frontend/package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le code source du frontend
COPY interflow-frontend/ .

# Corriger les permissions des exécutables npm
RUN chmod +x node_modules/.bin/*

# Construire l'application Next.js
RUN npm run build -- --no-lint

# Créer le dossier public s'il n'existe pas (requis pour la copie plus tard)
RUN mkdir -p public

# Étape 2: Build du backend Python
FROM python:3.12-alpine AS backend-builder

WORKDIR /app/backend

# Copier les fichiers nécessaires pour construire le wheel
COPY interflow-backend/pyproject.toml interflow-backend/README.md ./
COPY interflow-backend/src/ ./src/

# Installation des dépendances de build et construction du wheel
RUN pip install --no-cache-dir .[ci]
RUN python -m build --wheel

# Étape 3: Image finale avec Alpine 3.20
FROM alpine:3.20

# Installer les dépendances nécessaires
RUN apk add --no-cache \
    python3=3.12.11-r0 \
    py3-pip=24.0-r2 \
    nodejs=20.15.1-r0 \
    npm=10.9.1-r0 \
    nginx=1.26.3-r0 \
    supervisor=4.2.5-r5 \
    && rm -rf /var/cache/apk/*

# Créer les répertoires nécessaires
WORKDIR /app

# Copier le backend depuis l'étape de build
COPY --from=backend-builder /app/backend/dist/interflow_backend-0.0.0-py3-none-any.whl ./

# Créer un environnement virtuel et installer le backend
RUN python3 -m venv /app/venv
RUN /app/venv/bin/pip install --no-cache-dir interflow_backend-0.0.0-py3-none-any.whl

# Copier les fichiers du frontend depuis l'étape de build
COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static
COPY --from=frontend-builder /app/frontend/public ./public

# Créer tous les répertoires nginx nécessaires
RUN mkdir -p /var/log/nginx /var/lib/nginx/tmp /run/nginx
# Créer la structure complète de logs qui sera partagée avec l'hôte
RUN mkdir -p /var/log/nginx /var/log/supervisor
COPY conf/nginx.conf /etc/nginx/nginx.conf

# Créer le répertoire de configuration supervisor
RUN mkdir -p /etc/supervisor/conf.d
COPY conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Créer le répertoire data et copier les données du backend
RUN mkdir -p /app/data

# Configuration spécifique Podman : utiliser des UIDs/GIDs compatibles rootless
# Utiliser l'UID 1000 qui correspond souvent à l'utilisateur hôte
RUN addgroup -g 1000 -S appgroup && \
    adduser -u 1000 -S appuser -G appgroup

# Changer les permissions pour /app et /var/log (pour les logs partagés)
# Podman : s'assurer que les volumes sont accessibles
RUN chown -R appuser:appgroup /app /var/log
# S'assurer que les répertoires de logs sont accessibles en écriture
RUN chmod -R 755 /var/log

# Exposer le port
EXPOSE 80

# Variables d'environnement
ENV API_HOST=0.0.0.0
ENV API_PORT=5000
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
# NEXT_PUBLIC_API_URL non défini pour forcer l'utilisation des API Routes Next.js

# Commande de démarrage
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
