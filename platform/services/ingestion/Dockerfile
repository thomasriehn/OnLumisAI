# OnLumis Ingestion-Worker – multi-arch (aarch64 für DGX Spark, x86_64 für Dev)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv
COPY pyproject.toml ./
COPY worker ./worker

# WITH_OCR=1 installiert Tesseract (deu) + Poppler für den Scan-Fallback
ARG WITH_OCR=0
RUN if [ "$WITH_OCR" = "1" ]; then \
      apt-get update && \
      apt-get install -y --no-install-recommends \
        tesseract-ocr tesseract-ocr-deu poppler-utils && \
      rm -rf /var/lib/apt/lists/* && \
      pip install ".[ocr]"; \
    else \
      pip install .; \
    fi

CMD ["python", "-m", "worker.main", "loop"]
