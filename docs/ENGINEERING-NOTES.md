

5. **HPA lag in seconds, where did the time go, what would reduce it**

Our HPA (`k8s/base/hpa.yaml`) scales on 65% average CPU utilization with a
0-second scale-up stabilization window and a 60-second scale-down window.
The actual lag between load starting and a new pod serving traffic has
three components: (1) the metrics-server sampling interval (~15-30s before
HPA even sees the new CPU number), (2) pod scheduling + image pull time
(near-zero once the image is cached on the node, longer on first pull),
(3) our `startupProbe` in `k8s/base/backend-deployment.yaml`, which gives
the new pod up to 60s (30 x 2s) before it's marked ready to receive
traffic. In our own test, total lag from load start to a new pod actually
serving traffic was approximately <TODO: fill in your real measured
number from the load test>. The startupProbe window is the single biggest
lever to reduce this -- it's generous on purpose to avoid restart loops,
but could be tightened once we've confirmed the app boots reliably faster
than 60s.

6. **Why VPA is in Off/recommender mode, describe the Auto+HPA failure mode**

We run VPA in recommender-only mode (never Auto) specifically because
Auto mode fights with HPA over the same signal. If VPA is in Auto mode,
it can raise a pod's CPU *request* to bring average utilization down
(since HPA's target is 65% of the *request*, not an absolute number).
That drop in utilization then tells HPA "load is fine, scale in" --
so HPA removes pods. With fewer pods, each remaining pod's real load per
pod goes up, utilization climbs again, and VPA raises the request a
second time. This loop (VPA raises request -> HPA scales down -> per-pod
load rises -> VPA raises request again) means the two controllers can
oscillate indefinitely instead of converging, rather than actually
handling the traffic. Running VPA as recommender-only avoids this: it
still tells us what resource requests *should* be over time (which we
review and apply manually, see `k8s/overlays/prod/kustomization.yaml`'s
resource patch), while HPA is left as the only automatic responder to
real-time load.

7. **`internal: true` blocks outbound traffic -- where does that leave the LLM-calling service, how did you resolve it**

Our `backend-net` (in both `compose.yaml` and the Kubernetes NetworkPolicy
equivalent) is marked `internal: true` so the backend has no route to the
public internet by default -- this is what proves the database is
unreachable from outside the cluster, but it has a real side effect:
`llm_provider.py` needs outbound HTTPS access to Groq's API, and a fully
internal network blocks that too. <TODO: pick and document your actual
resolution -- e.g. "We split the backend onto a second, non-internal
network `egress-net` used only for outbound API calls, keeping
`backend-net` internal for DB/Redis access" OR "We accepted this
constraint for the internal Compose network and rely on TRIAGE_PROVIDER=
simulated/rules for any environment where backend-net is fully internal,
documented as a known limitation in docs/TRIAGE.md">.


5. **HPA lag in seconds, where did the time go, what would reduce it**

Our HPA (`k8s/base/hpa.yaml`) scales on 65% average CPU utilization with a
0-second scale-up stabilization window and a 60-second scale-down window.
The actual lag between load starting and a new pod serving traffic has
three components: (1) the metrics-server sampling interval (~15-30s before
HPA even sees the new CPU number), (2) pod scheduling + image pull time
(near-zero once the image is cached on the node, longer on first pull),
(3) our `startupProbe` in `k8s/base/backend-deployment.yaml`, which gives
the new pod up to 60s (30 x 2s) before it's marked ready to receive
traffic. In our own test, total lag from load start to a new pod actually
serving traffic was approximately <TODO: fill in your real measured
number from the load test>. The startupProbe window is the single biggest
lever to reduce this -- it's generous on purpose to avoid restart loops,
but could be tightened once we've confirmed the app boots reliably faster
than 60s.

6. **Why VPA is in Off/recommender mode, describe the Auto+HPA failure mode**

We run VPA in recommender-only mode (never Auto) specifically because
Auto mode fights with HPA over the same signal. If VPA is in Auto mode,
it can raise a pod's CPU *request* to bring average utilization down
(since HPA's target is 65% of the *request*, not an absolute number).
That drop in utilization then tells HPA "load is fine, scale in" --
so HPA removes pods. With fewer pods, each remaining pod's real load per
pod goes up, utilization climbs again, and VPA raises the request a
second time. This loop (VPA raises request -> HPA scales down -> per-pod
load rises -> VPA raises request again) means the two controllers can
oscillate indefinitely instead of converging, rather than actually
handling the traffic. Running VPA as recommender-only avoids this: it
still tells us what resource requests *should* be over time (which we
review and apply manually, see `k8s/overlays/prod/kustomization.yaml`'s
resource patch), while HPA is left as the only automatic responder to
real-time load.

7. **`internal: true` blocks outbound traffic -- where does that leave the LLM-calling service, how did you resolve it**

Our `backend-net` (in both `compose.yaml` and the Kubernetes NetworkPolicy
equivalent) is marked `internal: true` so the backend has no route to the
public internet by default -- this is what proves the database is
unreachable from outside the cluster, but it has a real side effect:
`llm_provider.py` needs outbound HTTPS access to Groq's API, and a fully
internal network blocks that too. <TODO: pick and document your actual
resolution -- e.g. "We split the backend onto a second, non-internal
network `egress-net` used only for outbound API calls, keeping
`backend-net` internal for DB/Redis access" OR "We accepted this
constraint for the internal Compose network and rely on TRIAGE_PROVIDER=
simulated/rules for any environment where backend-net is fully internal,
documented as a known limitation in docs/TRIAGE.md">.
