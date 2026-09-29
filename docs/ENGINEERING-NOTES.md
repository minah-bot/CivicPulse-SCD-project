\# Engineering Notes



\## 1. Three things that differ between your laptop and a CI runner

\- Database and cache: locally, `backend/.env.example` (or your local `.env`) points at `postgres`/`redis` service names that only resolve inside Docker Compose's network; a bare CI runner has no such hosts unless the workflow's `test` job also starts them. See `.github/workflows/cd.yml`, `test` job — it currently only runs `pytest`, not against a live Postgres/Redis (frozen by not defining `services:` for the test job).

\- Python/Node versions: locally these float to whatever's installed; frozen in CI by `actions/setup-python@v5` (`python-version: "3.12"`) and `actions/setup-node@v4` (`node-version: 22`) in `cd.yml`.

\- Base image versions: previously floating (`node:22-alpine`, `nginx:alpine`), now frozen by pinning in `frontend/Dockerfile` (`node:22.11.0-alpine3.20`, `nginx:1.27.2-alpine`).

## 2. Where your pipeline sits on the CI/CD maturity ladder

A common ladder: (1) manual builds/deploys -> (2) CI runs tests on push -> (3) CI + automated build/package -> (4) CI + automated deploy to an environment (CD) -> (5) automated deploy to production with progressive delivery (canary/blue-green) and automated rollback.



This pipeline sits at rung 4: `.github/workflows/cd.yml` runs tests (`test` job), then builds and publishes images tagged by commit SHA (`publish` job, `needs: test`), then deploys automatically to an ephemeral cluster and smoke-tests it (`deploy` job, `needs: publish`) — all gated and automatic, with no manual step between commit and a running deployment.



It isn't yet rung 5, because there's no staged/canary rollout and no automated rollback on a failed smoke test — a failed `Smoke test backend health` step currently just fails the job; it doesn't roll the Deployment back to the previous image. The next rung would add `kubectl rollout undo` (or similar) triggered by that failure, plus a real production target instead of only the ephemeral `kind` cluster used for CI.



\## 3. The exact line guaranteeing build-once-deploy-many

`kustomize edit set image ghcr.io/minah-bot/civicpulse-backend=ghcr.io/minah-bot/civicpulse-backend:${{ github.sha }}` in `.github/workflows/cd.yml` (`deploy` job) — the same image built and pushed by `SHA` in `publish` is the one referenced in the manifest applied to the cluster; nothing is rebuilt between environments. Without it, each environment would build its own image from source, so "the thing you tested" and "the thing you deployed" could differ.



\## 4. What "correct" means for a probabilistic LLM component, and how CI stays deterministic

`triage\_service.py` treats "correct" as: returns a value from the fixed `Category`/`Priority` enum in `schemas.py`, includes a summary, and records `triaged\_by`/`triage\_latency\_ms` — not that the LLM's wording matches an exact string. CI stays deterministic by using `providers/simulated\_provider.py` (seeded, no real network call) via `TRIAGE\_PROVIDER=simulated`, so tests never depend on a live LLM's output. `tests/test\_triage\_fallback.py` and `tests/test\_prompt\_injection.py` assert against the enum and against `triaged\_by == "rules:fallback"`, not against natural-language text.

## 5. Your HPA lag in seconds — where did the time go, what would reduce it

\[Needs an actual load test run — not yet performed as of this note. To measure: apply load with a tool like `hey` or `k6` against the backend Service, then run `kubectl get hpa -w -n civicpulse` and note the timestamp load started vs. the timestamp `REPLICAS` first increases.]



Expected sources of lag, to check against the real run: (1) the HPA's metrics-server polling interval (default \~15s) before it even sees the CPU spike, (2) the `--horizontal-pod-autoscaler-sync-period` scheduler interval, (3) new pod scheduling + image pull + readiness probe pass time before the new replica counts as available. To reduce it: lower the HPA's `stabilizationWindowSeconds` for scale-up (in the `behavior` block, if set), keep the image already cached on nodes (fewer/no image pulls), and keep the readiness probe's `periodSeconds`/`failureThreshold` tight so a ready pod is detected sooner.

## 6. Why VPA is in Off mode — describe the failure mode of Auto+HPA together

\[A VPA manifest doesn't exist in `k8s/base` yet — this needs to be created before this answer can cite a real file/line. Recommended: `updateMode: "Off"` so VPA only produces recommendations, viewable via `kubectl describe vpa`, without resizing pods itself.]



The reasoning to write up once it exists: HPA scales by adding/removing replicas based on average CPU/memory per pod. VPA in `Auto` mode resizes a pod's own CPU/memory requests, which requires evicting and recreating that pod. Run both in `Auto` at once on the same metric and they fight each other — VPA changes a pod's resource requests (changing what "average utilization" means per pod), which can trigger the HPA to scale replica count, while HPA changing replica count changes the load VPA sees per pod, prompting VPA to resize again. This can cause a "flapping" loop where pods are repeatedly resized and rescheduled instead of the system settling on a stable replica count and pod size. Running VPA in `Off` (recommendation-only) avoids this: humans read the recommendation and adjust `resources.requests`/`limits` in the Deployment manually, while HPA is left as the only thing actually reacting to load automatically.





\## 7. Your `internal: true` network blocks outbound traffic — where does that leave the LLM-calling service, how did you resolve it

`backend-net` is marked `internal: true` in `compose.yaml`, which blocks any container on it from reaching the internet, including a real Groq/Gemini API call from `llm\_provider.py`.

\[Needs confirming: does this setup only exercise `TRIAGE\_PROVIDER=llm` against `ollama\_provider.py` (same internal network, no internet needed), or is a real external LLM call expected? If external calls are needed, the fix is either (a) a separate non-internal network just for outbound LLM calls, or (b) a NAT/egress proxy container bridging the two networks. Check `providers/factory.py` and whichever `TRIAGE\_PROVIDER` value is actually used in Compose/K8s to answer this for real.]



\## 8. The failure that cost more than an hour

CD kept timing out on `kubectl rollout status deployment/backend` (`error: timed out waiting for the condition`, `cd.yml`, `deploy` job). First belief: the deployment YAML itself was broken. The actual cause, found after adding a debug step (`kubectl describe pods`, `kubectl get events`) \[confirm the exact status shown, e.g. `ImagePullBackOff`, once you or a teammate has the real output]: the `kind` cluster had no credentials to pull the private GHCR images. Fixed by creating a `ghcr-secret` (`kubectl create secret docker-registry ...`) and adding `imagePullSecrets: \[ghcr-secret]` to both Deployments.

