"""Pawprint stuff."""

from __future__ import annotations
from dataclasses import dataclass
from functools import singledispatchmethod
from typing import Any

# THIRD-PARTY
import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io.registry import UnifiedReadWriteMethod
from astropy.table import QTable
from matplotlib.path import Path as mpl_path

# LOCAL
from .connect import PawprintFromFormat, PawprintRead, PawprintToFormat, PawprintWrite

if TYPE_CHECKING:
    from astropy.coordinates import BaseCoordinateFrame

# class densityClass: #TODO: how to represent densities?

@dataclass(frozen=True)
class FootprintBase:

    pass


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


class PMFootprint(FootprintBase):

    def __init__(self):
        if isinstance(vertex_coordinates, SkyCoord):
            vc = vertex_coordinates
        else:
            # check if the vertices come with units
            has_units = True
            for v in vertex_coordinates:
                has_units *= isinstance(v[0], u.Quantity)
                has_units *= isinstance(v[1], u.Quantity)
            if has_units:
                # assume coordinates are in stream frame
                vc = SkyCoord(vertex_coordinates, frame=stream_frame)
            else:
                # assume units are mas/yr and frame is phi1/phi2
                vc = SkyCoord(
                    stream_frame,
                    lat=vertex_coordinates[0],
                    lon=vertex_coordinates[1],
                    unit="mas/yr",
                )
        self.edges = vc
        self.vertices = np.array(
            [vc.transform_to(stream_frame).phi1, vc.transform_to(stream_frame).phi2]
        ).T



class Footprint2D:
    def __init__(self, vertex_coordinates, footprint_type, stream_frame=None):
        # if footprint_type == "sky":
        #     if isinstance(vertex_coordinates, SkyCoord):
        #         vc = vertex_coordinates
        #     else:
        #         # check if the vertices come with units
        #         has_units = True
        #         for v in vertex_coordinates:
        #             has_units *= isinstance(v[0], u.Quantity)
        #             has_units *= isinstance(v[1], u.Quantity)
        #         if has_units:
        #             # assume coordinates are in stream frame
        #             vc = SkyCoord(vertex_coordinates, frame=stream_frame)
        #         else:
        #             # assume units are degrees and frame is phi1/phi2
        #             vc = SkyCoord(vertex_coordinates, unit="deg", frame=stream_frame)
        #     self.edges = vc
        #     self.vertices = np.array(
        #         [vc.transform_to(stream_frame).phi1, vc.transform_to(stream_frame).phi2]
        #     ).T

        # # HELP - how do we do PMs properly?
        # elif footprint_type == "pm":
        #     if isinstance(vertex_coordinates, SkyCoord):
        #         vc = vertex_coordinates
        #     else:
        #         # check if the vertices come with units
        #         has_units = True
        #         for v in vertex_coordinates:
        #             has_units *= isinstance(v[0], u.Quantity)
        #             has_units *= isinstance(v[1], u.Quantity)
        #         if has_units:
        #             # assume coordinates are in stream frame
        #             vc = SkyCoord(vertex_coordinates, frame=stream_frame)
        #         else:
        #             # assume units are mas/yr and frame is phi1/phi2
        #             vc = SkyCoord(
        #                 stream_frame,
        #                 lat=vertex_coordinates[0],
        #                 lon=vertex_coordinates[1],
        #                 unit="mas/yr",
        #             )
        #     self.edges = vc
        #     self.vertices = np.array(
        #         [vc.transform_to(stream_frame).phi1, vc.transform_to(stream_frame).phi2]
        #     ).T

        elif footprint_type == "cartesian":
            self.edges = vertex_coordinates
            self.vertices = vertex_coordinates

        self.stream_frame = stream_frame
        self.footprint_type = footprint_type
        self.footprint = mpl_path(self.vertices)

    
