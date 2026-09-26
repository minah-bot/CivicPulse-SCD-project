# backend/app/providers/rule_provider.py
#
# Pure keyword rules. Always succeeds, never raises, no network call.
# This is the SAFETY NET triage_service.py falls back to when the real
# LLM provider times out or returns something invalid -- so it must
# never itself be able to fail.

from app.schemas import Category, Priority, TriageResult

_RULES: list[tuple[Category, list[str]]] = [
    (Category.water, ["water", "leak", "pipe", "sewage", "drain", "flood"]),
    (Category.electricity, ["power", "electric", "outage", "wire", "transformer", "spark"]),
    (Category.sanitation, ["garbage", "trash", "waste", "dump", "smell", "rotting"]),
    (Category.roads, ["road", "pothole", "traffic", "street", "bridge", "crack"]),
    (Category.streetlights, ["light", "lamp", "dark", "streetlight", "bulb"]),
]

_URGENT_WORDS = ["urgent", "danger", "emergency", "injur", "fire", "collapse", "unsafe"]
_LOW_WORDS = ["minor", "small", "whenever", "cosmetic"]


class RuleProvider:
    name = "rules"

    def triage(self, text: str, location: str) -> TriageResult:
        lowered = text.lower()

        category = Category.other
        for cat, words in _RULES:
            if any(w in lowered for w in words):
                category = cat
                break

        if any(w in lowered for w in _URGENT_WORDS):
            priority = Priority.high
        elif any(w in lowered for w in _LOW_WORDS):
            priority = Priority.low
        else:
            priority = Priority.normal

        first_sentence = text.strip().split(".")[0][:140]
        summary = first_sentence or f"{category.value} issue at {location}"

        # rule-based confidence is intentionally modest and fixed --
        # it is a fallback, not a real inference, and should read as one
        return TriageResult(
            category=category,
            priority=priority,
            summary=summary,
            confidence=0.5,
        )