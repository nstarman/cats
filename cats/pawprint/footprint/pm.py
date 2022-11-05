"""Pawprint stuff."""

from __future__ import annotations

# STDLIB
from collections.abc import MutableMapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Iterator

# THIRD-PARTY
import astropy.units as u
import numpy as np
from astropy.coordinates import (
    BaseDifferential,
    SkyCoord,
    UnitSphericalCosLatDifferential,
)

# LOCAL
from .base import FootprintBase

if TYPE_CHECKING:
    # THIRD-PARTY
    from astropy.coordinates import BaseCoordinateFrame


def _get_points(data: BaseDifferential) -> np.ndarray:
    r = data.represent_as(UnitSphericalCosLatDifferential)
    return np.c_[r.d_lon_coslat.to_value(u.mas / u.yr), r.d_lat.to_value(u.mas / u.yr)]


@dataclass(frozen=True)
class PMFootprintBase(FootprintBase):

    edges: UnitSphericalCosLatDifferential
    center: SkyCoord
    is_reflex_corrected: bool

    @property
    def frame(self) -> BaseCoordinateFrame:
        return self.center.frame.replicate_without_data()

    @property
    def vertices(self) -> np.ndarray:
        return _get_points(self.edges)[:-1, :]  # (N, 2)


@dataclass(frozen=True)
class PMFootprint(PMFootprintBase):

    edges: UnitSphericalCosLatDifferential
    center: SkyCoord
    is_reflex_corrected: bool = True
    name: str | None = None

    @property
    def frame(self) -> BaseCoordinateFrame:
        return self.center.frame.replicate_without_data()

    @property
    def vertices(self) -> np.ndarray:
        raise NotImplementedError("TODO! just get from edges")


class CompositePMFootprint(MutableMapping[str, PMFootprintBase], PMFootprintBase):
    def __init__(
        self,
        frame: BaseCoordinateFrame,
        *,
        name: str | None,
        **pm_footprints: PMFootprintBase,
    ):
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
    def is_reflex_corrected(self) -> bool:
        return all(v.is_reflex_corrected for v in self.values())

    @property
    def centers(self) -> MappingProxyType:
        return MappingProxyType({k: v.center for k, v in self.items()})

    @property
    def vertices(self) -> np.ndarray:
        raise NotImplementedError("TODO! just get from edges")

    @property
    def edges(self) -> np.ndarray:
        raise NotImplementedError("TODO! just get from edges")
