from fastapi import APIRouter, Response
from sqlalchemy import text as sql_text

from app.database import engine
from app.services.stats_service import _redis_client

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Liveness. Must NEVER touch the database — a slow DB must not restart
    a perfectly healthy process (Kubernetes uses this for the liveness probe)."""
    return {"status": "ok"}


@router.get("/ready")
def ready(response: Response):
    """Readiness. SHOULD depend on the database (and cache) — Kubernetes
    pulls the pod out of the Service if this fails, without restarting it."""
    failures = []

    try:
        with engine.connect() as conn:
            conn.execute(sql_text("SELECT 1"))
    except Exception:
        failures.append("database")

    try:
        _redis_client.ping()
    except Exception:
        failures.append("redis")

    if failures:
        response.status_code = 503
        return {"status": "not_ready", "failed_dependencies": failures}

    return {"status": "ready"}


@router.get("/metrics")
def metrics():
    """Minimal Prometheus text-format exposition. Extend with prometheus_client
    if/when richer metrics (request counts, latency histograms) are added."""
    body = (
        "# HELP civicpulse_up Whether the backend process is up\n"
        "# TYPE civicpulse_up gauge\n"
        "civicpulse_up 1\n"
    )
    return Response(content=body, media_type="text/plain; version=0.0.4")
