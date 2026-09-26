# backend/app/providers/base.py
#
# >>> SHARED CONTRACT <<<
# The TriageProvider Protocol every provider implementation must satisfy,
# plus the custom exceptions triage_service.py catches for its
# timeout/retry/fallback logic.

from typing import Protocol

from app.schemas import TriageResult


class TriageProvider(Protocol):
    name: str

    def triage(self, text: str, location: str) -> TriageResult:
        """Return a triage result for the given complaint text/location.
        Implementations may raise TriageError or TriageTimeoutError;
        RuleProvider must never raise anything (it's the fallback)."""
        ...


class TriageError(Exception):
    """Base exception for any provider-level triage failure
    (malformed output, API error response, etc.)."""


class TriageTimeoutError(TriageError):
    """Raised when a provider call exceeds its timeout budget."""