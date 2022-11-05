"""Pawprint stuff."""

from __future__ import annotations

# STDLIB
from dataclasses import dataclass
from typing import TYPE_CHECKING

# THIRD-PARTY
import numpy as np
from matplotlib.path import Path

# LOCAL
from cats.pawprint.footprint.base import FootprintBase

if TYPE_CHECKING:
    # THIRD-PARTY
    from astropy.units import Quantity, Unit


@dataclass(frozen=True)
class CMDFootprint(FootprintBase):
    """Sky Footprint.

    Parameters
    ----------
    edges : SkyCoord
        In the correct frame. A list of the vertices. These points define the
        boundary of the polygon. It must be “closed”, i.e., the last point is
        the same as the first.
    """

    path: Path
    units: tuple[Unit, Unit]
    labels: tuple[str, str]

    name: str | None = None

    # ---------------------------------------------------------------

    @classmethod
    def from_box(
        cls,
        min1: Quantity,
        max1: Quantity,
        min2: Quantity,
        max2: Quantity,
        *,
        labels: tuple[str, str],
        name: str | None = None,
    ) -> CMDFootprint:
        mn1, mx1 = min1.value, max1.to_value(min1.unit)
        mn2, mx2 = min2.value, max2.to_value(min2.unit)
        vertices = np.c_[[mn1, mn1, mx1, mx1], [mn2, mx2, mn2, mx2]]
        units = (min1.unit, min2.unit)
        return CMDFootprint(Path(vertices), units=units, labels=labels)
