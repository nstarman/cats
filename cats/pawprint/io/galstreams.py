from __future__ import annotations

# STDLIB
import pathlib
from typing import TYPE_CHECKING

# THIRD-PARTY
import astropy.units as u
import galstreams
from astropy.coordinates import SkyCoord
from astropy.table import QTable
from gala.coordinates import GreatCircleICRSFrame

if TYPE_CHECKING:
    # THIRD-PARTY
    from astropy.units import Quantity

    # LOCAL
    from cats.pawprint.pawprint import Pawprint


GALSTREAMS_DIR = pathlib.Path(galstreams.__file__).parent
GALSTREAMS_TRACKS = GALSTREAMS_DIR / "tracks"


def _make_track_file_name(stream_name: str, pawprint_ID: str) -> str:
    return str(GALSTREAMS_TRACKS / f"track.st.{stream_name}.{pawprint_ID}.ecsv")


def _make_summary_file_name(stream_name: str, pawprint_ID: str) -> pathlib.Path:
    return GALSTREAMS_TRACKS / f"track.st.{stream_name}.{pawprint_ID}.summary.ecsv"


def _get_stream_frame_from_file(summary_file: pathlib.Path):
    t = QTable.read(summary_file)

    x = {}
    atts = (x.replace("mid.", "") for x in t.keys() if "mid" in x)
    # we're effectively looping over skycoords defined for mid here (ra,
    # dec, ...)
    for att in atts:
        # make sure to set it up as a scalar. if not, frame conversions
        # get into trouble
        x[att] = t[f"mid.{att}"][0]
    mid_point = SkyCoord(**x)

    # we're effectively looping over sskycoords defined for pole here
    # (ra, dec, ...)
    x = {}
    atts = [x.replace("pole.", "") for x in t.keys() if "pole" in x]
    for att in atts:
        x[att] = t[f"pole.{att}"][0]
    # Make sure to set the pole's distance attribute to 1 (zero causes
    # problems, when transforming to stream frame coords) it shouldn't
    # matter, but if it's zero it does crazy things
    x["distance"] = 1.0 * u.kpc
    mid_pole = SkyCoord(**x)

    return GreatCircleICRSFrame(pole=mid_pole, ra0=mid_point.icrs.ra)


def get_recommended_stream_width(stream_name: str) -> Quantity:
    """Get stream width.

    As recommended by Cecilia. This will eventually pulled from
    galstreams as an attribute of the track.
    """
    if "Jhelum" in stream_name:
        if "Jhelum-a" in stream_name:
            return 0.4 * u.deg
        else:
            return 0.94 * u.deg
    elif "Fjorm" in stream_name:
        return 0.9 * u.deg
    elif "Pal-5" in stream_name:
        return 0.5 * u.deg
    elif "GD-1" in stream_name:
        return 0.53 * u.deg
    elif "PS1-A" in stream_name:
        return 0.45 * u.deg
    else:  # default
        return 1.0 * u.deg


def pawprint_from_galstreams(
    cls: type[Pawprint], stream_name: str, pawprint_ID: str
) -> Pawprint:

    data = {}
    data["stream_name"] = stream_name
    data["pawprint_ID"] = pawprint_ID

    track_file = _make_track_file_name(stream_name, pawprint_ID)
    summary_file = _make_summary_file_name(stream_name, pawprint_ID)
    data["stream_frame"] = _get_stream_frame_from_file(summary_file)

    data["track"] = galstreams.Track6D(
        stream_name=data["stream_name"],
        track_name=data["pawprint_ID"],
        track_file=track_file,
        summary_file=summary_file,
    )
    data["width"] = 2.0 * get_recommended_stream_width(stream_name)
    data["stream_vertices"] = data["track"].create_sky_polygon_footprint_from_track(
        width=data["width"], phi2_offset=0.0 * u.deg
    )
    data["background_vertices"] = data["track"].create_sky_polygon_footprint_from_track(
        width=data["width"], phi2_offset=3.0 * u.deg
    )
    data["cmd_filters"] = None
    data["cmd_vertices"] = None
    data["pm_vertices"] = None

    return cls(data)
