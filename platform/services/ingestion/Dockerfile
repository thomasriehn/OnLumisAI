# OnLumis Ingestion-Worker – multi-arch (aarch64 für DGX Spark, x86_64 für Dev)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv
COPY pyproject.toml ./
COPY worker ./worker
RUN pip install .

CMD ["python", "-m", "worker.main", "loop"]
