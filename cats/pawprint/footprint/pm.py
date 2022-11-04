
"""Pawprint stuff."""

from __future__ import annotations
from typing import Iterator

# THIRD-PARTY
import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import QTable
from matplotlib.path import Path as mpl_path
from dataclasses import dataclass
from collections.abc import MutableMapping
from types import MappingProxyType

from .base import FootprintBase
from astropy.coordinates import UnitSphericalDifferential

if TYPE_CHECKING:
    from astropy.coordinates import BaseCoordinateFrame


@dataclass(frozen=True)
class PMFootprintBase(FootprintBase):

    center: SkyCoord


@dataclass(frozen=True)
class PMFootprint(PMFootprintBase):

    edges: UnitSphericalDifferential
    center: SkyCoord
    name: str | None = None

    @property
    def frame(self) -> BaseCoordinateFrame:
        return self.center.frame.replicate_without_data()

    @property
    def vertices(self) -> np.ndarray:
        raise NotImplementedError("TODO! just get from edges")


class CompositePMFootprint(MutableMapping[str, PMFootprintBase], PMFootprintBase):

    def __init__(self, frame: BaseCoordinateFrame, *, name: str | None, **pm_footprints: PMFootprintBase):
        # frame
        self.frame: BaseCoordinateFrame
        object.__setattr__(self, "frame", frame)

        # name
        self.name: str | None
        object.__setattr__(self, "name", name)

        # Make data
        self._data: dict[str, PMFootprintBase]
        object.__setattr__(self, "_data", {})
        for k, v in pm_footprints.items():  # set, with validation
            self[k] = v

    # ===============================================================
    # Mapping

    def __getitem__(self, key: str) -> PMFootprintBase:
        return self._data[key]

    def __setitem__(self, key: str, value: PMFootprintBase) -> None:
        # validate frame equality
        if value.frame != self.frame:
            raise ValueError

        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    # ===============================================================

    @property
    def center(self)

    @property
    def centers(self) -> MappingProxyType:
        return MappingProxyType(
            {
                k: v.center for k, v in self.items()
            }
        )

    @property
    def vertices(self) -> np.ndarray:
        raise NotImplementedError("TODO! just get from edges")