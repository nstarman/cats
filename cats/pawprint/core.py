"""Pawprint stuff."""

from __future__ import annotations

# THIRD-PARTY
from astropy.io.registry import UnifiedReadWriteMethod

# LOCAL
from cats.pawprint.footprint.cmd import CMDFootprint
from cats.pawprint.footprint.pm import PMFootprint
from cats.pawprint.footprint.sky import SkyFootprint
from cats.pawrint.connect import (
    PawprintFromFormat,
    PawprintRead,
    PawprintToFormat,
    PawprintWrite,
)

# class densityClass: #TODO: how to represent densities?


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
            "stream": SkyFootprint(
                data["stream_vertices"],
                footprint_type="sky",
                stream_frame=self.stream_frame,
            ),
            "background": SkyFootprint(
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
                self.cmdprint[k] = CMDFootprint(
                    data["cmd_vertices"][k], footprint_type="cartesian"
                )
        else:
            self.cmdprint = None
        if data["pm_vertices"] is not None:
            self.pmprint = {}
            for k in data["pm_vertices"].keys():
                self.pmprint[k] = PMFootprint(
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
