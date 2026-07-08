# ════════════════════════════════════════════════════════════════════
# FaberLoom · VPS Dockerfile
# Builds a lightweight production image for the FastAPI + React UMD app.
# Excludes desktop-only dependencies (pywebview / pyinstaller).
# ════════════════════════════════════════════════════════════════════

# ── Builder stage ──────────────────────────────────────────────────
FROM python:3.13-slim AS builder

# sqlcipher3 needs the SQLCipher headers and a compiler at build time.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsqlcipher-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY app/requirements-server.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-server.txt

# ── Runtime stage ──────────────────────────────────────────────────
FROM python:3.13-slim

# Runtime library required by the sqlcipher3 extension.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlcipher1 \
    tesseract-ocr \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy only the backend and static frontend assets.
COPY app/src ./app/src
COPY app/static ./app/static
COPY app/VERSION ./app/VERSION
COPY app/pyproject.toml ./app/pyproject.toml
COPY faberloom ./app/faberloom

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FABERLOOM_HOST=0.0.0.0
ENV FABERLOOM_PORT=8000
ENV FABERLOOM_CONFIG_DIR=/data
ENV FABERLOOM_DB_ENGINE=${FABERLOOM_DB_ENGINE:-postgres}
ENV FABERLOOM_POSTGRES_URL=${FABERLOOM_POSTGRES_URL:-postgresql://faberloom:faberloom@postgres:5432/faberloom}
ENV FABERLOOM_DB_PATH=/data/faberloom.sqlite3
ENV FABERLOOM_FOUNDATION_DB_ENGINE=${FABERLOOM_FOUNDATION_DB_ENGINE:-sqlite}
ENV FABERLOOM_FOUNDATION_DB=/data/foundation.sqlite3
ENV FABERLOOM_PUBLIC_HOST=app.faberloom.ai

EXPOSE 8000

CMD ["uvicorn", "app.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
