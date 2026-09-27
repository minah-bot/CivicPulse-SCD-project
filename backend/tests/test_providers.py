# backend/tests/test_providers.py

import os
from unittest.mock import patch

from app.providers.factory import get_provider
from app.providers.rule_provider import RuleProvider
from app.providers.simulated_provider import SimulatedProvider
from app.schemas import Category, Priority


def test_factory_returns_simulated_by_default():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("TRIAGE_PROVIDER", None)
        provider = get_provider()
    assert provider.name == "simulated"


def test_factory_returns_rules_when_selected():
    with patch.dict(os.environ, {"TRIAGE_PROVIDER": "rules"}):
        provider = get_provider()
    assert provider.name == "rules"


def test_factory_rejects_unknown_provider():
    with patch.dict(os.environ, {"TRIAGE_PROVIDER": "not_a_real_provider"}):
        try:
            get_provider()
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_simulated_provider_is_deterministic():
    provider = SimulatedProvider()
    r1 = provider.triage("Pothole on 3rd street", "3rd Street")
    r2 = provider.triage("Pothole on 3rd street", "3rd Street")
    assert r1.category == r2.category
    assert r1.confidence == r2.confidence


def test_rule_provider_categorizes_water_complaint():
    result = RuleProvider().triage("There is a burst water pipe flooding the road", "Elm St")
    assert result.category == Category.WATER


def test_rule_provider_flags_urgent_as_high_priority():
    result = RuleProvider().triage("URGENT: gas leak, this is an emergency", "Oak Ave")
    assert result.priority == Priority.HIGH