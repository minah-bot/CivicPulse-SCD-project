import json
import logging
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
# Graceful shutdown: uvicorn installs its own SIGTERM handler. On SIGTERM it
# stops accepting new connections, lets in-flight requests finish, then runs
# the shutdown half of this lifespan. We must NOT override that handler.
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
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
