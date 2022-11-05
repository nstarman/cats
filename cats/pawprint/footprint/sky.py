"""Pawprint stuff."""

from __future__ import annotations

# STDLIB
import os
from dataclasses import dataclass
from functools import singledispatchmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

# THIRD-PARTY
import astropy.units as u
import numpy as np
from astropy.coordinates import BaseCoordinateFrame, SkyCoord
from astropy.table import QTable
from matplotlib.path import Path

# LOCAL
from cats.pawprint.footprint.base import FootprintBase

if TYPE_CHECKING:
    # THIRD-PARTY
    from astropy.units import Quantity


F = TypeVar("F", bound=BaseCoordinateFrame)
FArg = TypeVar("FArg", bound=BaseCoordinateFrame)


def _get_points(
    data: SkyCoord | BaseCoordinateFrame, frame: BaseCoordinateFrame
) -> np.ndarray:
    d = data.transform_to(frame)
    return np.c_[d.phi1.to_value(u.deg), d.phi2.to_value(u.deg)]


@dataclass(frozen=True)
class SkyFootprint(FootprintBase, Generic[F]):
    """Sky Footprint.

    Parameters
    ----------
    edges : SkyCoord
        In the correct frame. A list of the vertices. These points define the
        boundary of the polygon. It must be “closed”, i.e., the last point is
        the same as the first.
    """

    path: Path  # in the stream frame (phi1, phi2)  # TODO! must be closed?
    frame: F
    name: str | None = None

    # ===============================================================
    # I/O

    @singledispatchmethod
    @classmethod
    def from_format(cls, vertex_coordinates: Any) -> SkyFootprint:
        raise NotImplementedError

    @from_format.register(SkyCoord)
    @classmethod
    def _from_format_skycoord(
        cls, vertex_coordinates: SkyCoord, frame: F | None, name: str | None = None
    ) -> SkyFootprint[F]:
        if frame is not None:
            d = vertex_coordinates.transform_to(frame)
            frm = frame
        else:
            d = vertex_coordinates
            frm = vertex_coordinates.frame.replicate_without_data()

        return cls(
            Path(np.c_[d.phi1.to_value(u.deg), d.phi12.to_value(u.deg)]),
            frame=frm,
            name=name,
        )

    @from_format.register(np.ndarray)
    @classmethod
    def _from_format_vertices(
        cls, vertex_coordinates: np.ndarray, frame: F, name: str | None = None
    ) -> SkyFootprint[F]:
        return cls(Path(vertex_coordinates), frame=frame, name=name)

    # ---------------------------------------------------------------

    @classmethod
    def from_box(
        cls,
        min1: Quantity,
        max1: Quantity,
        min2: Quantity,
        max2: Quantity,
        *,
        frame: BaseCoordinateFrame,
        name: str | None = None,
    ) -> SkyFootprint:
        mn1 = min1.to_value(u.deg)
        mn2 = min2.to_value(u.deg)
        mx1 = max1.to_value(u.deg)
        mx2 = max2.to_value(u.deg)
        vertices = np.c_[[mn1, mn1, mx1, mx1], [mn2, mx2, mn2, mx2]]

        return SkyFootprint(Path(vertices), frame=frame, name=name)

    @classmethod
    def read(cls, fname: str | bytes | os.PathLike) -> SkyFootprint:
        tbl = QTable.read(fname)
        vertices = tbl["vertices"]
        frame = tbl.meta["frame"]
        name = tbl.meta.get("name", None)
        # TODO! names
        return cls(vertices, frame=frame, name=name)

    # ===============================================================
    # Methods

    def inside_footprint(self, point: SkyCoord | BaseCoordinateFrame) -> list[bool]:
        return self.path.contains_points(_get_points(point, self.frame))
