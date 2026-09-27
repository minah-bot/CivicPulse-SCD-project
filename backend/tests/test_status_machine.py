import pytest

from app.schemas import Status
from app.services.status_service import InvalidTransitionError, validate_transition


@pytest.mark.parametrize(
    "current,new",
    [
        (Status.OPEN, Status.IN_PROGRESS),
        (Status.OPEN, Status.REJECTED),
        (Status.IN_PROGRESS, Status.RESOLVED),
        (Status.IN_PROGRESS, Status.REJECTED),
    ],
)
def test_allowed_transitions_do_not_raise(current, new):
    validate_transition(current, new)  # should not raise


@pytest.mark.parametrize(
    "current,new",
    [
        (Status.OPEN, Status.RESOLVED),          # can't skip in_progress
        (Status.RESOLVED, Status.OPEN),           # terminal
        (Status.REJECTED, Status.IN_PROGRESS),    # terminal
        (Status.IN_PROGRESS, Status.OPEN),        # no going backwards
    ],
)
def test_disallowed_transitions_raise_409_worthy_error(current, new):
    with pytest.raises(InvalidTransitionError) as exc_info:
        validate_transition(current, new)
    # message must name the attempted transition (API contract requirement)
    assert current.value in str(exc_info.value)
    assert new.value in str(exc_info.value)


def test_terminal_states_have_no_outgoing_transitions():
    from app.schemas import ALLOWED_TRANSITIONS

    assert ALLOWED_TRANSITIONS[Status.RESOLVED] == set()
    assert ALLOWED_TRANSITIONS[Status.REJECTED] == set()
