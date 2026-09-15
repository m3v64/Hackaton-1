FROM python:3.14-slim

WORKDIR /app

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-root --only main

COPY src/api /app/api
COPY alembic.ini ./
COPY migrations ./migrations

EXPOSE 8000

CMD alembic upgrade head && exec uvicorn api:app --host 0.0.0.0 --port 8000