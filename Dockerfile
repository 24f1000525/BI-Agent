# syntax=docker/dockerfile:1

FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 5000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} flask_app:app"]
