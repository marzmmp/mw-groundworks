"""M&W GroundWorks — brand constants and shared SVG drawing primitives."""
import os
import math

# ---------------------------------------------------------------- palette
# Greens sampled directly from the client's three existing logo files
# (#6C7E30 / #7E9048 / #849054 / #36421E) and regularised into a scale.
# Bone sampled from their cream field (#F1E7DB / #EFEBE0).
# Amber sampled from the sunburst in variation 3 (#EABA66) and deepened
# for CTA contrast against dark ink.
INK_950 = "#070A08"
INK_900 = "#0B0F0C"
INK_850 = "#101610"
INK_800 = "#161E17"
INK_700 = "#1F2A20"
INK_600 = "#2C3A2D"
INK_500 = "#41533F"

BONE = "#F2EDE1"
BONE_DIM = "#CFC8B8"
BONE_MUTE = "#9A9382"

MOSS_900 = "#223013"
MOSS_800 = "#33461B"
MOSS_700 = "#456022"
MOSS_600 = "#5E7F2C"
MOSS_500 = "#7A9A3E"      # core brand green
MOSS_400 = "#9AB85F"
MOSS_300 = "#BDD48E"

AMBER_600 = "#C9862A"
AMBER_500 = "#E8A33D"     # CTA / high-visibility accent
AMBER_400 = "#F2BC69"

RUST = "#A84E24"

# Source fonts for outlining logo text, bundled so the generator runs
# without an npm install.
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
F_COND_700 = os.path.join(FONT_DIR, "barlow-condensed-latin-700-normal.woff")
F_COND_600 = os.path.join(FONT_DIR, "barlow-condensed-latin-600-normal.woff")
F_COND_500 = os.path.join(FONT_DIR, "barlow-condensed-latin-500-normal.woff")
F_BAR_600 = os.path.join(FONT_DIR, "barlow-latin-600-normal.woff")
F_BAR_500 = os.path.join(FONT_DIR, "barlow-latin-500-normal.woff")


# ---------------------------------------------------------------- rng
class Rng:
    """Deterministic LCG so every regeneration produces identical artwork."""

    def __init__(self, seed=1):
        self.s = seed & 0xFFFFFFFF

    def next(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 0x7FFFFFFF

    def range(self, a, b):
        return a + (b - a) * self.next()


# ---------------------------------------------------------------- shapes
def octagon(x, y, w, h, c):
    """Surveyor's-plate octagon: rectangle with clipped corners."""
    return (
        f"M{x + c:.1f},{y:.1f} H{x + w - c:.1f} L{x + w:.1f},{y + c:.1f} "
        f"V{y + h - c:.1f} L{x + w - c:.1f},{y + h:.1f} H{x + c:.1f} "
        f"L{x:.1f},{y + h - c:.1f} V{y + c:.1f} Z"
    )


def brush_silhouette(x0, x1, base_y, max_h, seed=7, density=26):
    """Jagged overgrowth — the 'before' half of the story.

    Builds an irregular skyline of scrub, saplings and tall grass.
    """
    r = Rng(seed)
    pts = [(x0, base_y)]
    step = (x1 - x0) / density
    x = x0
    for i in range(density):
        h = r.range(0.25, 1.0) ** 1.6 * max_h
        # occasional tall sapling spike
        if r.next() > 0.80:
            h = max_h * r.range(0.9, 1.25)
        peak_x = x + step * r.range(0.25, 0.75)
        pts.append((peak_x, base_y - h))
        x += step
        pts.append((x, base_y - h * r.range(0.05, 0.35)))
    pts.append((x1, base_y))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for px, py in pts[1:]:
        d += f" L{px:.1f},{py:.1f}"
    return d + " Z"


def conifer(cx, base_y, h, w, tiers=4):
    """Stylised evergreen — reads at 16px."""
    d = ""
    for i in range(tiers):
        t = i / tiers
        ty = base_y - h * (0.18 + 0.82 * t)
        tw = w * (1.0 - 0.72 * t)
        drop = h * 0.20
        d += (f"M{cx - tw / 2:.1f},{ty + drop:.1f} L{cx:.1f},{ty - h * 0.14:.1f} "
              f"L{cx + tw / 2:.1f},{ty + drop:.1f} Z ")
    tw = w * 0.10
    d += (f"M{cx - tw:.1f},{base_y:.1f} L{cx - tw:.1f},{base_y - h * 0.22:.1f} "
          f"L{cx + tw:.1f},{base_y - h * 0.22:.1f} L{cx + tw:.1f},{base_y:.1f} Z")
    return d


def hardwood(cx, base_y, h, w):
    """Stylised broadleaf — the oak in their original mark, simplified."""
    r = w / 2.0
    cy = base_y - h + r * 0.92
    d = f"M{cx - w * 0.055:.1f},{base_y:.1f} "
    d += f"L{cx - w * 0.075:.1f},{cy + r * 0.55:.1f} "
    d += f"L{cx - w * 0.20:.1f},{cy + r * 0.30:.1f} "
    d += f"L{cx - w * 0.085:.1f},{cy + r * 0.38:.1f} "
    d += f"L{cx - w * 0.085:.1f},{cy + r * 0.10:.1f} "
    d += f"L{cx + w * 0.085:.1f},{cy + r * 0.10:.1f} "
    d += f"L{cx + w * 0.085:.1f},{cy + r * 0.42:.1f} "
    d += f"L{cx + w * 0.21:.1f},{cy + r * 0.16:.1f} "
    d += f"L{cx + w * 0.075:.1f},{cy + r * 0.58:.1f} "
    d += f"L{cx + w * 0.055:.1f},{base_y:.1f} Z "
    # canopy — overlapping lobes
    r2 = Rng(21)
    lobes = [(-0.36, 0.10, 0.40), (0.00, -0.10, 0.52), (0.36, 0.10, 0.40),
             (-0.20, -0.34, 0.36), (0.20, -0.34, 0.36)]
    for lx, ly, lr in lobes:
        d += (f"M{cx + lx * r * 2 - lr * r:.1f},{cy + ly * r:.1f} "
              f"a{lr * r:.1f},{lr * r:.1f} 0 1,0 {2 * lr * r:.1f},0 "
              f"a{lr * r:.1f},{lr * r:.1f} 0 1,0 {-2 * lr * r:.1f},0 Z ")
    return d


def strata(x0, x1, y, layers, gap=4):
    """Ground cross-section bars — topsoil / subsoil / bedrock."""
    out = []
    cy = y
    for h, inset in layers:
        out.append((x0 + inset, cy, (x1 - x0) - inset * 2, h))
        cy += h + gap
    return out


def bucket_teeth(x0, x1, y, n=5, depth=16):
    """Excavator-bucket tooth row."""
    w = (x1 - x0) / n
    d = f"M{x0:.1f},{y:.1f} "
    for i in range(n):
        a = x0 + i * w
        d += (f"L{a + w * 0.18:.1f},{y + depth:.1f} "
              f"L{a + w * 0.82:.1f},{y + depth:.1f} "
              f"L{a + w:.1f},{y:.1f} ")
    return d + "Z"


def xml_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def svg(w, h, body, bg=None, title="M&W GroundWorks"):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    t = xml_escape(title)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{t}">'
        f"<title>{t}</title>{b}{body}</svg>"
    )
