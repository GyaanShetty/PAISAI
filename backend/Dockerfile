# PAISAI backend image. Build context is the backend/ directory.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml README.md ./
COPY paisai ./paisai
RUN pip install --no-cache-dir -e ".[api,postgres]"

EXPOSE 8000

# DATABASE_URL and PAISAI_CORS_ORIGINS are provided at runtime.
CMD ["uvicorn", "paisai.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
