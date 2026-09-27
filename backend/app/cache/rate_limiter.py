# backend/app/cache/rate_limiter.py
#
# Redis-backed fixed-window rate limiter, keyed by client IP.
# Used as a FastAPI dependency on POST /api/complaints.

import os
import time

import redis

_client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))

_LIMIT = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "10"))
_WINDOW_SECONDS = 60


class RateLimitExceeded(Exception):
    def __init__(self, retry_after_seconds: int):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Rate limit exceeded, retry after {retry_after_seconds}s")


def check_rate_limit(client_ip: str) -> None:
    """
    Fixed-window limiter: LIMIT requests per WINDOW_SECONDS per IP.
    Raises RateLimitExceeded if the caller is over the limit; the route
    catches this and returns 429 with a Retry-After header.
    """
    key = f"ratelimit:{client_ip}:{int(time.time()) // _WINDOW_SECONDS}"

    count = _client.incr(key)
    if count == 1:
        _client.expire(key, _WINDOW_SECONDS)

    if count > _LIMIT:
        ttl = _client.ttl(key)
        raise RateLimitExceeded(retry_after_seconds=max(ttl, 1))