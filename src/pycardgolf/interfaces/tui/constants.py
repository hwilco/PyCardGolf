"""Shared constants for the TUI."""

from __future__ import annotations

import enum


class _Sentinel(enum.Enum):
    QUIT = enum.auto()


QUIT_SENTINEL = _Sentinel.QUIT
