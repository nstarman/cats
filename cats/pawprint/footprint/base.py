"""Pawprint stuff."""

from __future__ import annotations

# STDLIB
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    # STDLIB
    import os

T = TypeVar("T", bound="FootprintBase")


@dataclass(frozen=True)
class FootprintBase:

    # ===============================================================
    # I/O

    @classmethod
    def read(cls: type[T], fname: str | bytes | os.PathLike) -> T:
        raise NotImplementedError("you should be using a subclass!")
