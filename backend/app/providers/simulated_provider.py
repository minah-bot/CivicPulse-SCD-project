# backend/app/providers/simulated_provider.py
#
# Deterministic fake TriageProvider. No network call, no API key.
# Lets A wire routes and C wire the frontend before real LLM keys exist.
# Also used in CI so tests never depend on a live API.

import hashlib

from app.schemas import Category, Priority, TriageResult

# very small keyword table -> category, just for believable-looking demo data
_KEYWORDS = {
    Category.WATER: ["water", "leak", "pipe", "sewage", "drain"],
    Category.ELECTRICITY: ["power", "electric", "outage", "wire", "transformer", "light", "lamp", "streetlight"],
    Category.SANITATION: ["garbage", "trash", "waste", "dump", "smell"],
    Category.ROADS: ["road", "pothole", "traffic", "street", "bridge"],
}


def _pick_category(text: str) -> Category:
    lowered = text.lower()
    for category, words in _KEYWORDS.items():
        if any(word in lowered for word in words):
            return category
    return Category.OTHER


def _pick_priority(text: str) -> Priority:
    lowered = text.lower()
    if any(w in lowered for w in ["urgent", "danger", "emergency", "injur", "fire"]):
        return Priority.HIGH
    if any(w in lowered for w in ["minor", "small", "whenever"]):
        return Priority.LOW
    return Priority.MEDIUM


class SimulatedProvider:
    name = "simulated"

    def triage(self, text: str, location: str) -> TriageResult:
        category = _pick_category(text)
        priority = _pick_priority(text)

        # deterministic "confidence" so repeated calls with the same text
        # always return the same result -- important for reproducible tests
        digest = hashlib.sha256(text.encode()).hexdigest()
        confidence = 0.55 + (int(digest[:2], 16) / 255) * 0.4  # range ~0.55-0.95

        summary = text.strip().split(".")[0][:140]
        if not summary:
            summary = f"{category.value} issue reported at {location}"

        return TriageResult(
            category=category,
            priority=priority,
            summary=summary,
            confidence=round(confidence, 2),
        )