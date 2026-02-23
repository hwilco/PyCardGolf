"""Module containing the RNGMixin class."""

from __future__ import annotations

import functools
import random
import sys


class RNGMixin:
    """Provides a consistent RNG state associated with a seed."""

    def __init__(self, seed: int | None = None) -> None:
        self.seed = seed if seed is not None else random.randrange(sys.maxsize)

    @functools.cached_property
    def rng(self) -> random.Random:
        """Returns the random number generator, lazily initialized."""
        return random.Random(self.seed)

    def copy_rng_state(self, target: RNGMixin) -> None:
        """Copy the exact RNG state from this instance to the target instance."""
        target.seed = self.seed
        if "rng" in self.__dict__:
            target.rng.setstate(self.rng.getstate())

    def reseed(self, seed: int) -> None:
        """Safely reseed the random number generator."""
        self.seed = seed
        self.rng = random.Random(self.seed)
