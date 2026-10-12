# Build the React/Vite frontend on Linux so platform-specific npm dependencies are correct.
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Single public web service: FastAPI API + static frontend; knowledge data bootstraps at runtime.
FROM python:3.11-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    APP_ENV=production \
    DEBUG=false \
    TRANSCRIPTS_DATA_DIR=/app/data/transcripts \
    VECTOR_INDEX_DIR=/app/data/index
WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./alembic.ini
COPY scripts ./scripts
COPY --from=frontend-build /frontend/dist ./static
RUN mkdir -p /app/data/transcripts /app/data/index

EXPOSE 8000
# Download the licensed starter corpus at runtime (not into the public repo/image),
# build the local index, then serve UI and API from a single origin.
CMD ["sh", "-c", "python /app/scripts/bootstrap_knowledge.py && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
