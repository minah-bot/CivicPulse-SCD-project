# backend/Dockerfile
#
# Multi-stage: build deps in one layer, run in a slim final image.
# Pinned base version (never :latest), non-root user, exec-form CMD.

FROM python:3.12.7-slim AS builder

WORKDIR /app

# Install deps into a venv-like prefix so the final stage can copy just
# this, not the compiler toolchain that psycopg2/etc need to build.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12.7-slim

WORKDIR /app

# Copy only the installed packages from the builder stage -- keeps the
# final image free of build tools (gcc, headers) that requirements.txt
# needed only to compile, not to run.
COPY --from=builder /install /usr/local

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Non-root user -- never run the app as root in the container.
RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000

# Matches the startupProbe/livenessProbe path in k8s/base/backend-deployment.yaml
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Exec form -- so SIGTERM reaches uvicorn directly for graceful shutdown,
# rather than being swallowed by a shell wrapping the command.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
