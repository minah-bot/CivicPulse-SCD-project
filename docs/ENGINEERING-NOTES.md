\# Engineering Notes



\## Q1. Why was a TriageProvider interface used?



CivicPulse separates complaint triage from the specific AI implementation by using a common TriageProvider interface. The system currently supports LLM, Ollama, rule-based, and simulated providers.



The provider is selected through the TRIAGE\_PROVIDER environment variable rather than being hard-coded into the route layer. This allows CI and development to use deterministic providers without requiring an external API while production can use an LLM provider.



References:

\- docs/adr/0001-provider-interface.md

\- docs/TRIAGE.md

\- backend/providers/base.py

\- backend/providers/factory.py



\## Q2. How does the system remain available when the LLM fails?



The triage service uses a fallback strategy. The LLM provider has a timeout and timeout failures can be retried. If the retry fails, or a non-retryable provider error occurs, the deterministic RuleProvider is used.



The resulting triaged\_by value records which provider ultimately produced the result, including rules:fallback.



This prevents an external AI outage from causing complaint submission itself to fail.



References:

\- docs/TRIAGE.md

\- backend/services/triage\_service.py

\- backend/providers/llm\_provider.py

\- backend/providers/rule\_provider.py



\## Q3. How are deterministic tests kept independent of external AI services?



The simulated provider is used for development and CI so that tests do not require a live Groq API, API key, or external network connection. The rule provider also provides a deterministic fallback.



This makes the automated test suite repeatable and avoids test failures caused by external API availability, rate limits, or network conditions.



References:

\- docs/adr/0001-provider-interface.md

\- docs/TRIAGE.md

\- backend/providers/simulated\_provider.py

\- backend/tests/



\## Q4. What data is sent to the external LLM provider?



Only complaint text and location are passed to the triage provider. reporter\_contact is not passed to the triage function and therefore is not intentionally sent to Groq for classification.



However, complaint text is free-form. A citizen could voluntarily place a name or phone number inside the complaint text. The current implementation does not perform PII redaction before sending such text to the external LLM provider.



This is documented as a known limitation rather than being represented as a solved problem.



References:

\- docs/adr/0004-pii-and-data-governance.md

\- backend/providers/llm\_provider.py

\- backend/services/triage\_service.py



\## Q5. What was observed about HPA scaling lag?



This requires a real Kubernetes load-test run and observation of the HPA using:



&#x20;   kubectl get hpa -w



The final observation and replicas-versus-load chart should be added after the Kubernetes load test is completed.



Status: Kubernetes evidence pending.



References:

\- Kubernetes manifests under k8s/

\- Required HPA load-test evidence



\## Q6. How was VPA configured and how does it interact with HPA?



The required VPA Off-mode evidence depends on the VPA manifest and recommendation output being present in the Kubernetes configuration.



Status: Kubernetes evidence pending and to be completed by the Kubernetes workstream.



References:

\- Kubernetes manifests under k8s/

\- Required VPA recommendation evidence



\## Q7. How is internal networking separated from external LLM egress?



The application architecture separates backend services from frontend access to infrastructure services. The exact production networking and LLM egress behavior depends on the final Kubernetes and deployment configuration.



The PII/data-governance ADR documents that reporter\_contact is not sent to the LLM provider and that Ollama can operate locally, while the Groq provider represents the external API case.



Status: Final Kubernetes/networking configuration requires verification.



References:

\- docs/adr/0004-pii-and-data-governance.md

\- docs/TRIAGE.md

\- Kubernetes manifests under k8s/



\## Q8. What is the main reliability trade-off in the triage architecture?



The architecture prioritizes availability of complaint submission over dependence on a single AI provider. External AI provides richer classification, but it introduces network, availability, timeout, and rate-limit risks.



The deterministic RuleProvider provides a final safety net. This means a degraded AI service does not necessarily prevent a complaint from being submitted and classified.



The trade-off is that rule-based fallback classification is less sophisticated than an LLM and may misclassify complaints when the keyword table does not cover the wording used by a citizen.



References:

\- docs/adr/0001-provider-interface.md

\- docs/TRIAGE.md

\- backend/providers/rule\_provider.py

