# backend/tests/test_triage_fallback.py
#
# The one rubric explicitly asks for: if the configured provider always
# raises, the request must still succeed via the rules fallback, and
# triaged_by must record that it happened.

from unittest.mock import patch

from app.providers.base import TriageError
from app.schemas import TriagedBy
from app.services.triage_service import run_triage


class AlwaysFailsProvider:
    name = "llm:groq"

    def triage(self, text, location):
        raise TriageError("simulated total provider failure")


def test_fallback_when_provider_always_fails():
    with patch("app.services.triage_service.get_provider", return_value=AlwaysFailsProvider()):
        outcome = run_triage("Water leaking on Main Street", "Main Street")

    assert outcome.result is not None
    assert outcome.triaged_by == TriagedBy.rules_fallback
    # the rule provider must have produced a real category, not a crash
    assert outcome.result.category is not None


def test_fallback_result_is_still_valid_triage_result():
    with patch("app.services.triage_service.get_provider", return_value=AlwaysFailsProvider()):
        outcome = run_triage("Streetlight has been dark for a week", "5th Ave")

    assert 0.0 <= outcome.result.confidence <= 1.0
    assert len(outcome.result.summary) <= 140