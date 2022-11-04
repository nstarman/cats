from __future__ import annotations

# STDLIB
import os
import pathlib
from typing import Any, TypeVar, overload

# THIRD-PARTY
import asdf
import galstreams

# LOCAL
from cats.pawprint.connect import readwrite_registry
from cats.pawprint.pawprint import Pawprint

PP = TypeVar("PP", bound="Pawprint")


GALSTREAMS_DIR = pathlib.Path(galstreams.__file__).parent
GALSTREAMS_TRACKS = GALSTREAMS_DIR / "tracks"


def _make_track_file_name(stream_name: str, pawprint_ID: str) -> str:
    return str(GALSTREAMS_TRACKS / f"track.st.{stream_name}.{pawprint_ID}.ecsv")


def _make_summary_file_name(stream_name: str, pawprint_ID: str) -> pathlib.Path:
    return GALSTREAMS_TRACKS / f"track.st.{stream_name}.{pawprint_ID}.summary.ecsv"


@overload
def read_asdf(
    filename: str | bytes | os.PathLike, pawprint_cls: type[PP] = ..., **kwargs: Any
) -> PP:
    ...


@overload
def read_asdf(
    filename: str | bytes | os.PathLike, pawprint_cls: None = ..., **kwargs: Any
) -> Pawprint:
    ...


def read_asdf(
    filename: str | bytes | os.PathLike,
    pawprint_cls: type[PP] | None = None,
    **kwargs: Any,
) -> PP:
    PPC = Pawprint if pawprint_cls is None else pawprint_cls

    data = {}
    with asdf.open(filename) as a:
        # first transfer the stuff that goes directly
        data["stream_name"] = a["stream_name"]
        data["pawprint_ID"] = a["pawprint_ID"]
        data["stream_frame"] = a["stream_frame"]
        data["width"] = a["width"]
        data["cmd_filters"] = a["cmd_filters"]

        # now create footprints from vertices
        data["stream_vertices"] = a["on_stream"]["sky"]["vertices"][:]
        data["background_vertices"] = a["off_stream"]["vertices"][:]

        if a["on_stream"]["cmd"] is not None:
            data["cmd_vertices"] = {
                k: a["on_stream"]["cmd"][k]["vertices"]
                for k in a["on_stream"]["cmd"].keys()
            }

        if a["on_stream"]["pm"] is not None:
            data["pm_vertices"] = {
                k: a["on_stream"]["pm"][k]["vertices"]
                for k in a["on_stream"]["pm"].keys()
            }

        # right now getting track from galstreams since I can't save it yet
        galstreams_dir = os.path.dirname(galstreams.__file__)
        os.path.join(galstreams_dir, "tracks/")
        track_file = _make_track_file_name(data["stream_name"], data["pawprint_ID"])
        summary_file = _make_summary_file_name(data["stream_name"], data["pawprint_ID"])
        data["track"] = galstreams.Track6D(
            stream_name=data["stream_name"],
            track_name=data["pawprint_ID"],
            track_file=track_file,
            summary_file=summary_file,
        )

    return PPC(data)


def write_asdf(pawprint: Pawprint, file: str | bytes | os.PathLike) -> None:
    # WARNING this doesn't save the track yet - need schema
    # WARNING the stream frame doesn't save right either
    fname = f"{pawprint.stream_name}{pawprint.pawprint_ID}.asdf"

    tree = {
        "stream_name": pawprint.stream_name,
        "pawprint_ID": pawprint.pawprint_ID,
        "stream_frame": pawprint.stream_frame,  # needs a schema to save properly
        "cmd_filters": pawprint.cmd_filters,
        "width": pawprint.width,
        "on_stream": {"sky": pawprint.skyprint["stream"].export()},
        "off_stream": pawprint.skyprint["background"].export(),
        #    'track':pawprint.track   #TODO
    }
    if pawprint.cmdprint is not None:
        tree["on_stream"]["cmd"] = {
            k: pawprint.cmdprint[k].export() for k in pawprint.cmd_filters.keys()
        }
    else:
        tree["on_stream"]["cmd"] = None

    if pawprint.pmprint is not None:
        tree["on_stream"]["pm"] = {
            k: pawprint.pmprint[k].export() for k in pawprint.pmprint.keys()
        }
    else:
        tree["on_stream"]["pm"] = None

    out = asdf.AsdfFile(tree)
    out.write_to(fname)


def asdf_identify(
    origin: Any, filepath: str | None, fileobj: Any, *args: Any, **kwargs: Any
) -> bool:
    return filepath is not None and filepath.endswith(".asdf")


# ===================================================================
# Register

readwrite_registry.register_reader("asdf", Pawprint, read_asdf)
readwrite_registry.register_writer("asdf", Pawprint, write_asdf)
readwrite_registry.register_identifier("asdf", Pawprint, asdf_identify)
