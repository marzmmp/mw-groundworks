"""Convert text to outlined SVG paths using real font files.

Produces fully self-contained SVG logos with zero web-font dependency —
the letterforms become geometry, so they render identically in every
browser, in Illustrator, on a vinyl cutter, and in an embroidery digitizer.
"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import ControlBoundsPen
from fontTools.misc.transform import Transform

_CACHE = {}


def load(path):
    if path not in _CACHE:
        f = TTFont(path, fontNumber=0)
        _CACHE[path] = f
    return _CACHE[path]


def text_path(font_path, text, size=100, tracking=0.0, x=0.0, y=0.0, scale_x=1.0):
    """Return (path_d, advance_width) for `text`.

    size      : cap-to-cap font size in user units (em size)
    tracking  : extra letter-spacing, in em fractions (0.04 = 4% of size)
    x, y      : position of the text origin (y = baseline)
    scale_x   : horizontal squeeze (0.92 = 8% condensed)
    """
    font = load(font_path)
    glyphset = font.getGlyphSet()
    cmap = font.getBestCmap()
    upem = font["head"].unitsPerEm
    s = size / upem
    hmtx = font["hmtx"]

    pen = SVGPathPen(glyphset, ntos=lambda v: f"{v:.2f}")
    cursor = 0.0
    track_units = (tracking * size) / s if s else 0.0

    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            gname = cmap.get(ord(" "))
            if gname is None:
                continue
        # y flips because font space is y-up, SVG is y-down
        t = Transform(s * scale_x, 0, 0, -s, x + cursor * s * scale_x, y)
        tpen = TransformPen(pen, t)
        glyphset[gname].draw(tpen)
        cursor += hmtx[gname][0] + track_units

    width = cursor * s * scale_x
    if text:
        width -= track_units * s * scale_x  # no trailing track
    return pen.getCommands(), width


def text_bounds(font_path, text, size=100, tracking=0.0, scale_x=1.0):
    """Return (x_min, y_min, x_max, y_max) of the rendered text in SVG space."""
    font = load(font_path)
    glyphset = font.getGlyphSet()
    cmap = font.getBestCmap()
    upem = font["head"].unitsPerEm
    s = size / upem
    hmtx = font["hmtx"]
    bp = ControlBoundsPen(glyphset)
    cursor = 0.0
    track_units = (tracking * size) / s if s else 0.0
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            continue
        t = Transform(s * scale_x, 0, 0, -s, cursor * s * scale_x, 0)
        glyphset[gname].draw(TransformPen(bp, t))
        cursor += hmtx[gname][0] + track_units
    return bp.bounds


def centered(font_path, text, size, cx, baseline, tracking=0.0, scale_x=1.0):
    """Path `d` for text horizontally centered on cx, sitting on `baseline`."""
    d, w = text_path(font_path, text, size, tracking, 0, 0, scale_x)
    b = text_bounds(font_path, text, size, tracking, scale_x)
    if b is None:
        return ""
    x0, _, x1, _ = b
    dx = cx - (x0 + x1) / 2.0
    d, _ = text_path(font_path, text, size, tracking, dx, baseline, scale_x)
    return d


def measure(font_path, text, size, tracking=0.0, scale_x=1.0):
    b = text_bounds(font_path, text, size, tracking, scale_x)
    if b is None:
        return 0.0, 0.0
    x0, y0, x1, y1 = b
    return x1 - x0, y1 - y0
