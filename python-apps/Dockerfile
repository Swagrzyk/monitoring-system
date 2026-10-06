# syntax=docker/dockerfile:1

# --- Build stage: install dependencies into an isolated prefix ---
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime stage: minimal image, no build tools, non-root user ---
FROM python:3.11-slim

# Dedicated non-root user/group for running the exporter
RUN groupadd --gid 10001 exporter \
    && useradd --uid 10001 --gid exporter --no-create-home --shell /usr/sbin/nologin exporter

WORKDIR /app

COPY --from=builder /install /usr/local
COPY simple_monitor.py .

# Numeric UID:GID so Kubernetes can verify runAsNonRoot without having to
# resolve a user name from /etc/passwd inside the image.
USER 10001:10001

EXPOSE 8000

# The exporter has no external dependencies (no DB, no upstream API), so
# /metrics doubles as both liveness and readiness signal for this container.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/metrics', timeout=2)"]

ENTRYPOINT ["python", "simple_monitor.py"]
