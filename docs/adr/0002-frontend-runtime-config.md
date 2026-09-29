# ADR 0002: Frontend Runtime Configuration

## Status
Accepted

## Context
The same frontend image needs to run against different backend URLs in
dev, CI, and prod, without rebuilding the image for each environment.

## Decision
<TODO: describe your actual approach once confirmed with C -- e.g.
"nginx serves a generated /config.js at container start, populated from
an environment variable at runtime via docker-entrypoint" OR "the
frontend calls relative /api/* paths and nginx proxies them to the
backend service, so no absolute URL is ever baked in">

## Consequences
One image works everywhere; no rebuild needed to change environments.
