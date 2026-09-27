"""Aggregate stats with a Redis read-through cache (Rubric E: 30s TTL,
X-Cache header, invalidated on write — not left to expire).

Note: Person B owns cache/rate_limiter.py and cache/triage_cache.py for the
AI layer's own Redis usage. This module keeps its own tiny Redis client
because the stats cache is a Backend/services concern, not an AI concern —
both simply point at the same REDIS_URL.
"""
import json

import redis
from sqlalchemy.orm import Session

from app.config import get_settings
from app.repositories import complaint_repo

STATS_CACHE_KEY = "stats:aggregate:v1"

_settings = get_settings()
_redis_client = redis.Redis.from_url(_settings.redis_url, decode_responses=True)


def get_stats(db: Session) -> tuple[dict, str]:
    """Returns (stats_dict, cache_status) where cache_status is 'HIT' or 'MISS'."""
    try:
        cached = _redis_client.get(STATS_CACHE_KEY)
    except redis.exceptions.RedisError:
        # No Redis available (e.g. unit tests without a cache container) —
        # degrade to always-MISS rather than hard-failing the request.
        cached = None

    if cached is not None:
        return json.loads(cached), "HIT"

    stats = complaint_repo.get_aggregate_counts(db)
    try:
        _redis_client.set(STATS_CACHE_KEY, json.dumps(stats), ex=_settings.cache_ttl_seconds)
    except redis.exceptions.RedisError:
        pass
    return stats, "MISS"


def invalidate_stats_cache() -> None:
    """Call this after any write (new complaint, status change) so stats
    are correct immediately rather than up to 30s stale."""
    try:
        _redis_client.delete(STATS_CACHE_KEY)
    except redis.exceptions.RedisError:
        pass
