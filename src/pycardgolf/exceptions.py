"""Custom exceptions for PyCardGolf."""


class PyCardGolfError(Exception):
    """Base exception for all PyCardGolf errors.

    Catch this to handle any PyCardGolf-specific exception.
    """


class GameConfigError(PyCardGolfError):
    """Raised when game configuration is invalid."""
