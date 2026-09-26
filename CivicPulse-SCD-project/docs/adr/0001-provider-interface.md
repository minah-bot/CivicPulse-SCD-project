ADR 0001: TriageProvider Interface
Status
Accepted
Context
CivicPulse needs to classify complaint text into a category and priority using an LLM. But three separate constraints pushed against calling an LLM API directly from wherever triage happens:
Tests and CI can't depend on a live API key or network access. A test suite that calls a real LLM is slow, costs money per run, and fails nondeterministically when the API is briefly unavailable — none of which is acceptable for a required, deterministic test suite.
The API being used might change. Groq was picked for its free tier and speed, but if it goes down mid-project, or a teammate's key gets rate-limited during grading, there needed to be a way to keep the app working without a code change under pressure.
A "nothing worked" case still has to return something. Even with retries, the app can't leave a citizen's complaint submission hanging or return a 500 error just because an external API is unreachable.
Decision
Every way of turning complaint text into a TriageResult implements the same interface — a TriageProvider Protocol with a single method: triage(text: str, location: str) -> TriageResult. Four implementations exist behind this interface: LlmProvider (real Groq call), OllamaProvider (local model, same shape), RuleProvider (deterministic keywords), and SimulatedProvider (a fake for dev/CI that mimics LLM-like variability without a network call).
providers/factory.py is the only place that decides which implementation is active, based on the TRIAGE_PROVIDER environment variable. triage_service.py — and everything upstream of it, including the routes — only ever calls provider.triage(...) through this shared interface. It has no idea, and doesn't need to know, whether it's talking to Groq, a local model, or a keyword table.
Alternatives considered
An abstract base class instead of a Protocol. Python's Protocol gives structural typing — a class "is" a TriageProvider if it has a matching triage() method, with no explicit inheritance required. An ABC would have required every provider to explicitly subclass a shared base, which adds a dependency between files that don't otherwise need one (e.g. simulated_provider.py has no reason to import anything from llm_provider.py). Protocol keeps the four providers fully independent of each other.
Passing the provider choice as a function argument instead of an env var. This was rejected because it would mean the caller — a route handler — has to know about provider selection at all, which mixes an infrastructure concern (which AI backend is active right now) into request-handling code. Keeping it in factory.py, driven by an env var, means switching providers for a demo or a grading run is a .env edit, not a code change or redeploy.
Consequences
Easier: Adding a fifth provider later (say, a different LLM vendor) means writing one new file that implements triage() — nothing else in the codebase needs to change. Testing is also easier: test_triage_fallback.py swaps in a fake "always fails" provider via a simple patch, without needing to mock HTTP calls at all.
Harder: If TriageResult itself needs a new field, every provider needs to be updated to populate it, and the shared schemas.py contract has to change first with the whole team aware of it — a change to the interface is a change everyone feels, not something one person can quietly do in their own file.

