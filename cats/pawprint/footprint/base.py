"""Pawprint stuff."""

from __future__ import annotations
from dataclasses import dataclass
from 


@dataclass(frozen=True)
class FootprintBase:

    @classmethod
    def from_file(cls, fname):
        with QTable.read(fname) as t:
            vertices = t["vertices"]
        return cls(vertices)

    # ===============================================================
    # Construction

    # @classmethod
    # def from_vertices(cls, vertex_coordinates, footprint_type, frame=None):
    #     return cls(vertex_coordinates, footprint_type, frame)

    # @classmethod
    # def from_box(cls, min1, max1, min2, max2, footprint_type, frame=None):
    #     def get_vertices_from_box(min1, max1, min2, max2):
    #         return [[min1, min2], [min1, max2], [max1, min2], [max1, max2]]

    #     vertices = get_vertices_from_box(min1, max1, min2, max2)
    #     return cls(vertices, footprint_type, frame)

    # @classmethod
    # def from_file(cls, fname):
    #     with QTable.read(fname) as t:
    #         vertices = t["vertices"]
    #         footprint_type = t["footprint_type"]
    #     return cls(vertices, footprint_type)

    # def get_vertices_from_box(self, min1, max1, min2, max2):
    #     return [[min1, min2], [min1, max2], [max1, min2], [max1, max2]]

    # def inside_footprint(self, data):
    #     if isinstance(data, SkyCoord):
    #         if self.frame is None:
    #             raise NotImplementedError("TODO!")
    #             return
    #         else:
    #             pts = np.array(
    #                 [
    #                     data.transform_to(self.frame).phi1.value,
    #                     data.transform_to(self.frame).phi2.value,
    #                 ]
    #             ).T
    #             return self.footprint.contains_points(pts)
    #     else:
    #         return self.footprint.contains_points(data)

    # def export(self):
    #     data = {}
    #     data["frame"] = self.frame
    #     data["vertices"] = self.vertices
    #     data["footprint_type"] = self.footprint_type
    #     return data
