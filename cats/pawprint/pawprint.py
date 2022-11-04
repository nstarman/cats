"""Pawprint stuff."""

from __future__ import annotations

# THIRD-PARTY
import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io.registry import UnifiedReadWriteMethod
from astropy.table import QTable
from matplotlib.path import Path as mpl_path

# LOCAL
from .connect import PawprintFromFormat, PawprintRead, PawprintToFormat, PawprintWrite

# class densityClass: #TODO: how to represent densities?


class Footprint2D:
    def __init__(self, vertex_coordinates, footprint_type, stream_frame=None):
        if footprint_type == "sky":
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
                    # assume units are degrees and frame is phi1/phi2
                    vc = SkyCoord(vertex_coordinates, unit="deg", frame=stream_frame)
            self.edges = vc
            self.vertices = np.array(
                [vc.transform_to(stream_frame).phi1, vc.transform_to(stream_frame).phi2]
            ).T

        # HELP - how do we do PMs properly?
        elif footprint_type == "pm":
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

        elif footprint_type == "cartesian":
            self.edges = vertex_coordinates
            self.vertices = vertex_coordinates

        self.stream_frame = stream_frame
        self.footprint_type = footprint_type
        self.footprint = mpl_path(self.vertices)

    # ===============================================================
    # Construction

    @classmethod
    def from_vertices(cls, vertex_coordinates, footprint_type, stream_frame=None):
        return cls(vertex_coordinates, footprint_type, stream_frame)

    @classmethod
    def from_box(cls, min1, max1, min2, max2, footprint_type, stream_frame=None):
        def get_vertices_from_box(min1, max1, min2, max2):
            return [[min1, min2], [min1, max2], [max1, min2], [max1, max2]]

        vertices = get_vertices_from_box(min1, max1, min2, max2)
        return cls(vertices, footprint_type, stream_frame)

    @classmethod
    def from_file(cls, fname):
        with QTable.read(fname) as t:
            vertices = t["vertices"]
            footprint_type = t["footprint_type"]
        return cls(vertices, footprint_type)

    def get_vertices_from_box(self, min1, max1, min2, max2):
        return [[min1, min2], [min1, max2], [max1, min2], [max1, max2]]

    def inside_footprint(self, data):
        if isinstance(data, SkyCoord):
            if self.stream_frame is None:
                raise NotImplementedError("TODO!")
                return
            else:
                pts = np.array(
                    [
                        data.transform_to(self.stream_frame).phi1.value,
                        data.transform_to(self.stream_frame).phi2.value,
                    ]
                ).T
                return self.footprint.contains_points(pts)
        else:
            return self.footprint.contains_points(data)

    def export(self):
        data = {}
        data["stream_frame"] = self.stream_frame
        data["vertices"] = self.vertices
        data["footprint_type"] = self.footprint_type
        return data


class Pawprint:
    """Class to store a "pawprint".

    polygons in multiple observational spaces that define the initial selection
    used for stream track modeling, membership calculation / density modeling,
    and background modeling.

    New convention: everything is in phi1 phi2 (don't cross the streams)
    """

    read = UnifiedReadWriteMethod(PawprintRead)
    write = UnifiedReadWriteMethod(PawprintWrite)
    from_format = UnifiedReadWriteMethod(PawprintFromFormat)
    to_format = UnifiedReadWriteMethod(PawprintToFormat)

    def __init__(self, data):

        self.stream_name = data["stream_name"]
        self.pawprint_ID = data["pawprint_ID"]
        self.stream_frame = data["stream_frame"]
        self.width = data["width"]
        self.skyprint = {
            "stream": Footprint2D(
                data["stream_vertices"],
                footprint_type="sky",
                stream_frame=self.stream_frame,
            ),
            "background": Footprint2D(
                data["background_vertices"],
                footprint_type="sky",
                stream_frame=self.stream_frame,
            ),
        }

        # WG3: how to implement distance dependence in isochrone selections?
        self.cmd_filters = data["cmd_filters"]

        if self.cmd_filters is not None:
            self.cmdprint = {}
            for k in data.cmd_filters.keys():
                self.cmdprint[k] = Footprint2D(
                    data["cmd_vertices"][k], footprint_type="cartesian"
                )
        else:
            self.cmdprint = None
        if data["pm_vertices"] is not None:
            self.pmprint = {}
            for k in data["pm_vertices"].keys():
                self.pmprint[k] = Footprint2D(
                    data["pm_vertices"][k],
                    footprint_type="sky",
                    stream_frame=self.stream_frame,
                )  # polygon(s) in proper-motion space mu_phi1, mu_phi2
        else:
            self.pmprint = None

        self.track = data["track"]

    # ===============================================================
    # Constructors

    @classmethod
    def from_galstreams(cls, stream_name, pawprint_ID):
        # LOCAL
        from .io.galstreams import pawprint_from_galstreams

        return pawprint_from_galstreams(cls, stream_name, pawprint_ID)

    # ===============================================================

    def add_cmd_footprint(self, new_footprint, color, mag, name):
        if self.cmd_filters is None:
            self.cmd_filters = {}
            self.cmdprint = {}

        self.cmd_filters[name] = [color, mag]
        self.cmdprint[name] = new_footprint

    def add_pm_footprint(self, new_footprint, name):
        if self.pmprint is None:
            self.pmprint = {}
        self.pmprint[name] = new_footprint
