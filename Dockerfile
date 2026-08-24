# syntax=docker/dockerfile:1

##############################
# Stage 1 — builder
##############################
FROM python:3.12-slim AS builder

# Build tools live ONLY in the builder stage. They let pip compile a wheel
# from source if a prebuilt one is missing for the target arch (e.g. ciso8601
# or numpy on some ARM variants). The final image carries none of this.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

##############################
# Stage 2 — runtime
##############################
FROM python:3.12-slim AS runtime

# Copy the ready-built virtualenv; no compilers in the final image.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY venus.py docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh \
    && adduser --disabled-password --gecos '' appuser
USER appuser

# Configuration is passed via environment variables (see README).
# Defaults are applied in the entrypoint.
ENTRYPOINT ["./docker-entrypoint.sh"]
