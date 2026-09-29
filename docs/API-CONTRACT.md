\# API Contract



Frontend `client.ts` and backend `routes/` must match this exactly. Update this file whenever a route changes.



| Method | Path | Body / Query | Success | Failure |

|---|---|---|---|---|

| POST | `/api/complaints` | `ComplaintCreate` | 201 `ComplaintOut` | 400 field errors, 429 rate limited |

| GET | `/api/complaints/{id}` | - | 200 `ComplaintOut` | 404 |

| GET | `/api/complaints` | `?category=\&priority=\&status=\&page=\&page\_size=` (page\_size <= 100) | 200 `ComplaintList` | 400 bad page params |

| PATCH | `/api/complaints/{id}/status` | `StatusUpdate` | 200 `ComplaintOut` | 404, 409 invalid transition (message names the attempted transition) |

| GET | `/api/stats` | - | 200 aggregates, header `X-Cache: HIT|MISS` | - |

| GET | `/api/meta/providers` | - | 200 `ProvidersMeta` | - |

| GET | `/health` | - | 200 (never touches DB) | - |

| GET | `/ready` | - | 200 / 503 naming failed dependency | - |

| GET | `/metrics` | - | Prometheus text format | - |



\## Env vars (must match `.env.example` everywhere)



```

DATABASE\_URL=

REDIS\_URL=

TRIAGE\_PROVIDER=simulated # llm | ollama | rules | simulated

GROQ\_API\_KEY=

GEMINI\_API\_KEY=

OLLAMA\_BASE\_URL=

RATE\_LIMIT\_PER\_MINUTE=

CACHE\_TTL\_SECONDS=30

TRIAGE\_CACHE\_TTL\_HOURS=24

```

