"""Pawprint stuff."""

from __future__ import annotations
from dataclasses import dataclass
from functools import singledispatchmethod
from typing import TYPE_CHECKING, Any

# THIRD-PARTY
import numpy as np
from astropy.coordinates import SkyCoord
from cats.pawprint.footprint.base import FootprintBase

if TYPE_CHECKING:
    from astropy.coordinates import BaseCoordinateFrame


@dataclass(frozen=True)
class SkyFootprint(FootprintBase):

    edges: SkyCoord  # in the stream frame (phi1, phi2)

    @property
    def frame(self) -> BaseCoordinateFrame:
        return self.edges.frame.replicate_without_data()

    @property
    def vertices(self) -> np.ndarray:
        return np.array(
            [
                self.edges.transform_to(self.frame).phi1,
                self.edges.transform_to(self.frame).phi2
            ]
        ).T

    # ===============================================================
    # I/O

    @singledispatchmethod
    @classmethod
    def from_format(cls, vertex_coordinates: Any) -> SkyFootprint:
        raise NotImplementedError

    @from_format.register(SkyCoord)
    @classmethod
    def _from_format_skycoord(cls, vertex_coordinates: SkyCoord) -> SkyFootprint:
        return cls(vertex_coordinates)

    # @from_format.register(SkyCoord)
    # @classmethod
    # def _from_format_iterable(cls, vertex_coordinates: SkyCoord) -> SkyFootprint:
    #     return cls(vertex_coordinates)
