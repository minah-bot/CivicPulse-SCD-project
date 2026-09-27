from fastapi import APIRouter

from app.config import get_settings
from app.schemas import ProviderMeta, ProvidersMetaOut

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/meta/providers", response_model=ProvidersMetaOut)
def get_providers_meta():
    """Surfaces triage_latency_ms / fallback counts per provider.

    NOTE for Person B: this route expects a `get_metrics()` function from
    your services/triage_service.py returning a list of dicts shaped like
    ProviderMeta (name, calls, fallback_count, avg_latency_ms). Until that
    lands, this returns a static placeholder so the endpoint is contract-
    correct and C can build the frontend against it today.
    """
    settings = get_settings()
    try:
        from app.services.triage_service import get_metrics  # Person B's module

        providers = [ProviderMeta(**m) for m in get_metrics()]
    except ImportError:
        providers = [
            ProviderMeta(name=settings.triage_provider, calls=0, fallback_count=0)
        ]

    return ProvidersMetaOut(active_provider=settings.triage_provider, providers=providers)
