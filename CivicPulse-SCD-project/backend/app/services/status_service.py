from app.schemas import Status, ALLOWED_TRANSITIONS


class InvalidTransitionError(Exception):
    """Raised when a status transition is not allowed. Routes translate
    this into HTTP 409, naming the attempted transition (per API contract)."""

    def __init__(self, current: Status, attempted: Status):
        self.current = current
        self.attempted = attempted
        super().__init__(
            f"Cannot transition complaint from '{current.value}' to '{attempted.value}'"
        )


def validate_transition(current: Status, new: Status) -> None:
    """Raise InvalidTransitionError if `current -> new` is not in the table.
    This is the ONLY place transition rules live — no ifs scattered in routes."""
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if new not in allowed:
        raise InvalidTransitionError(current, new)
