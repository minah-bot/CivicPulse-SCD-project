# backend/app/providers/factory.py
#
# Single place that decides which TriageProvider implementation is active.
# triage_service.py calls get_provider() and never imports a concrete
# provider class directly -- that's what makes swapping providers a
# one-line env var change instead of a code change.

import os

from app.providers.base import TriageProvider


def get_provider() -> TriageProvider:
    choice = os.environ.get("TRIAGE_PROVIDER", "simulated").lower()

    if choice == "llm":
        from app.providers.llm_provider import LlmProvider
        return LlmProvider()

    if choice == "ollama":
        from app.providers.ollama_provider import OllamaProvider
        return OllamaProvider()

    if choice == "rules":
        from app.providers.rule_provider import RuleProvider
        return RuleProvider()

    if choice == "simulated":
        from app.providers.simulated_provider import SimulatedProvider
        return SimulatedProvider()

    raise ValueError(
        f"Unknown TRIAGE_PROVIDER={choice!r}. "
        "Expected one of: llm, ollama, rules, simulated."
    )