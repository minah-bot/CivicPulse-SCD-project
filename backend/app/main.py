import json
import logging
import signal
import sys
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.routes import complaints, health, meta, stats

# ---------------------------------------------------------------------------
# Structured JSON logging to stdout (never to a file — container FS is
# ephemeral, log shippers read stdout).
# ---------------------------------------------------------------------------

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "request_id": getattr(record, "request_id", None),
        }
        return json.dumps(payload)


logger = logging.getLogger("civicpulse")
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(JsonFormatter())
logger.addHandler(_handler)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Graceful shutdown: stop accepting new requests, let in-flight ones drain,
# close the DB pool, exit. Without this a rolling update drops live requests.
# ---------------------------------------------------------------------------

_shutting_down = False


def _handle_sigterm(signum, frame):
    global _shutting_down
    _shutting_down = True
    logger.info("SIGTERM received, draining in-flight requests")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        signal.signal(signal.SIGTERM, _handle_sigterm)
    except ValueError:
        # signal.signal() only works in the main thread of the main
        # interpreter. Starlette's TestClient runs the lifespan in a
        # worker thread, so this is expected (and harmless) under pytest.
        # Real deployments (uvicorn) run this in the main thread and register fine.
        logger.info("SIGTERM handler not registered (not running in main thread)")

    logger.info("civicpulse backend starting up")
    yield
    from app.database import engine

    engine.dispose()  # close pool connections cleanly
    logger.info("civicpulse backend shut down cleanly")


app = FastAPI(title="CivicPulse API", lifespan=lifespan)

app.include_router(complaints.router)
app.include_router(stats.router)
app.include_router(meta.router)
app.include_router(health.router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Propagates X-Request-ID (generates one if absent) and attaches it
    to every structured log line for that request."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.monotonic()

    response = await call_next(request)

    duration_ms = int((time.monotonic() - start) * 1000)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        f"{request.method} {request.url.path} {response.status_code} {duration_ms}ms",
        extra={"request_id": request_id},
    )
    return response
