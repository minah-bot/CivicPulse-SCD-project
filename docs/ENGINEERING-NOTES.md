# Engineering Notes

This document records the engineering reasoning behind important CivicPulse design decisions and answers the questions required for the project documentation.

## Q1. Why was a TriageProvider interface used?

CivicPulse separates complaint triage from the specific AI or classification implementation through a common `TriageProvider` protocol.

The protocol is defined in:

* `backend/app/providers/base.py:6`
* `backend/app/providers/base.py:17` for the triage timeout error type

The project supports multiple providers behind the same abstraction:

* LLM provider
* Ollama provider
* Rule-based provider
* Simulated provider

The provider is selected through the `TRIAGE_PROVIDER` environment variable rather than being hard-coded into the route layer.

The selection is implemented in:

* `backend/app/providers/factory.py:14`
* `backend/app/providers/factory.py:25-26`

This allows CI and development to use deterministic providers without requiring an external API while allowing an LLM provider to be selected for demonstration or production-style execution.

This design follows the dependency inversion principle: the triage service depends on the provider abstraction rather than directly depending on a particular AI implementation.

Related documentation:

* `docs/adr/0001-provider-interface.md`
* `docs/TRIAGE.md`

---

## Q2. How does the system remain available when the LLM fails?

CivicPulse uses a timeout, retry, and deterministic fallback strategy.

The LLM provider defines a configurable timeout, with the default set to 10 seconds:

* `backend/app/providers/llm_provider.py:35`
* `backend/app/providers/llm_provider.py:37`
* `backend/app/providers/llm_provider.py:53`

Timeout errors are converted into `TriageTimeoutError` so that the service layer can distinguish retryable failures:

* `backend/app/providers/llm_provider.py:57-60`

The main triage workflow is implemented in:

* `backend/app/services/triage_service.py:26`

Retryable failures are retried once with randomized jitter:

* `backend/app/services/triage_service.py:15`
* `backend/app/services/triage_service.py:41-48`

If the retry fails, or if the original error is non-retryable, the service falls through to the deterministic `RuleProvider`:

* `backend/app/services/triage_service.py:51-55`

The final result records which provider produced the classification:

* `backend/app/services/triage_service.py:20`
* `backend/app/services/triage_service.py:57`
* `backend/app/services/triage_service.py:60-67`

This means an external AI failure does not necessarily cause complaint submission to fail. The system can still produce a deterministic classification.

Related documentation:

* `docs/TRIAGE.md`
* `docs/adr/0001-provider-interface.md`

---

## Q3. How are deterministic tests kept independent of external AI services?

CivicPulse provides a simulated provider specifically for development and CI scenarios.

The provider abstraction allows the application to select a deterministic implementation using:

```text
TRIAGE_PROVIDER=simulated
```

The available provider implementations are located under:

```text
backend/app/providers/
```

including:

* `simulated_provider.py`
* `rule_provider.py`
* `llm_provider.py`
* `ollama_provider.py`

The backend tests are located under:

```text
backend/tests/
```

Important provider and fallback tests include:

* `backend/tests/test_providers.py`
* `backend/tests/test_triage_fallback.py`
* `backend/tests/test_prompt_injection.py`

Using deterministic providers means the automated test suite does not require a live Groq API, API key, or external network connection.

This improves repeatability and avoids test failures caused by external API availability, rate limits, or network conditions.

Related documentation:

* `docs/adr/0001-provider-interface.md`
* `docs/TRIAGE.md`

---

## Q4. What data is sent to the external LLM provider?

The triage workflow intentionally separates complaint classification from reporter contact information.

The triage service receives:

* complaint text
* location

The reporter contact information is not intentionally passed to the triage provider.

The relevant implementation is in:

* `backend/app/services/triage_service.py`
* `backend/app/providers/llm_provider.py`

The data-governance decision is documented in:

* `docs/adr/0004-pii-and-data-governance.md`

There is, however, an important limitation: complaint text is free-form. A citizen could voluntarily include a name, phone number, or other personal information inside the complaint text itself.

The current implementation does not automatically redact such information before sending complaint text to an external LLM provider.

This is documented as a known limitation rather than being represented as a solved privacy problem.

---

## Q5. What was observed about HPA scaling lag?

The HPA scaling-lag observation requires a real Kubernetes load test and monitoring of the Horizontal Pod Autoscaler.

The required observation command is:

```bash
kubectl get hpa -w
```

The final engineering note should record:

* the load applied to the backend,
* when the HPA changed desired replicas,
* how quickly additional replicas became ready,
* whether request latency changed during scaling,
* and the final replica count.

The required replicas-versus-load chart should also be included as evidence.

**Status: Kubernetes load-test evidence pending.**

References:

* `k8s/`
* HPA configuration in the Kubernetes manifests
* Required HPA load-test evidence

---

## Q6. How was VPA configured and how does it interact with HPA?

The VPA/HPA relationship needs to be evaluated using the final Kubernetes configuration.

The required evidence should show the VPA operating in recommendation-only (`Off`) mode rather than automatically modifying pod resources.

This avoids having VPA and HPA simultaneously attempting to control the same scaling dimension.

The final documentation should include:

* VPA configuration,
* recommendation output,
* resource requests used by the workloads,
* and an explanation of why HPA and VPA are not competing for control.

**Status: Kubernetes VPA evidence pending and assigned to the Kubernetes workstream.**

References:

* `k8s/`
* VPA configuration and recommendation evidence

---

## Q7. How is internal networking separated from external LLM egress?

CivicPulse separates the frontend, backend, database, and cache responsibilities at the application and deployment levels.

The backend communicates with infrastructure services such as PostgreSQL and Redis, while the frontend communicates with the backend API rather than directly accessing the database.

The final Kubernetes networking configuration determines the exact production-level network boundaries and external egress behavior.

The AI architecture supports both external and local provider options:

* Groq represents the external LLM provider.
* Ollama can operate as a local provider.
* RuleProvider and SimulatedProvider do not require external AI connectivity.

The relevant AI and data-governance documentation is:

* `docs/adr/0004-pii-and-data-governance.md`
* `docs/TRIAGE.md`

**Status: Final Kubernetes networking and egress behavior requires verification against the completed deployment configuration.**

---

## Q8. What is the main reliability trade-off in the triage architecture?

The main reliability trade-off is between richer AI-based classification and independence from external AI availability.

An external LLM can provide more sophisticated classification, but it introduces dependencies on:

* network connectivity,
* API availability,
* response time,
* rate limits,
* provider errors,
* and external service outages.

CivicPulse addresses this risk through the deterministic `RuleProvider`.

The fallback is implemented in:

* `backend/app/services/triage_service.py:53-57`

The rule provider itself is implemented in:

* `backend/app/providers/rule_provider.py:22`

The result is that a degraded external AI provider does not necessarily prevent a complaint from being submitted and classified.

The trade-off is that rule-based classification is less sophisticated than an LLM and may misclassify complaints when the keyword rules do not cover the wording used by a citizen.

Related documentation:

* `docs/adr/0001-provider-interface.md`
* `docs/TRIAGE.md`

---

## Summary of Engineering Decisions

The CivicPulse triage architecture deliberately favors:

1. Provider independence through a common abstraction.
2. Deterministic CI and development through the simulated provider.
3. Availability through timeout, retry, and rule-based fallback.
4. Traceability through the `triaged_by` field.
5. Separation of reporter contact information from intentional LLM input.
6. Explicit documentation of unresolved privacy and infrastructure limitations.

The remaining Kubernetes-specific observations should be updated after the corresponding live deployment and load-test evidence is collected.
