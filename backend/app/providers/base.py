class TriageError(Exception):
    pass


class TriageTimeoutError(TriageError):
    pass


class TriageValidationError(TriageError):
    pass

