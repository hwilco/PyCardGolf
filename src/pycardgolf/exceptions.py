"""Custom exceptions for PyCardGolf."""


class PyCardGolfError(Exception):
    """Base exception for all PyCardGolf errors.

    Catch this to handle any PyCardGolf-specific exception.
    """


class GameConfigError(PyCardGolfError):
    """Exception raised for errors in the game configuration."""


class GameExitError(PyCardGolfError):
    """Exception raised when the user wants to exit the game."""


class IllegalActionError(PyCardGolfError):
    """Raised when a player attempts an illegal action."""
