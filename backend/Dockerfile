# Backend image: FastAPI + async SQLAlchemy serving the official BIK takvim from Postgres.
# docker-compose supplies the runtime command (alembic upgrade -> seed -> uvicorn); the CMD
# here is the sensible default for running the image on its own.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime dependencies via the project metadata. Dev extras (pytest, requests,
# beautifulsoup4) are intentionally excluded — they're not needed to migrate/seed/serve.
COPY pyproject.toml ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
RUN pip install .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
