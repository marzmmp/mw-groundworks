#!/usr/bin/env python3
"""Generate the M&W GroundWorks identity system as self-contained SVGs.

Every letterform is converted to outline geometry — no web-font dependency,
so the files render identically in a browser, Illustrator, a vinyl cutter,
and an embroidery digitiser.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import brand as B
import textpath as T

OUT = os.path.join(os.path.dirname(__file__), "..", "website", "assets", "logos")
os.makedirs(OUT, exist_ok=True)

CAP = 0.708  # Barlow Condensed cap-height as a fraction of em


def cx_text(txt, size, cx, baseline, fill, tracking=0.0, font=B.F_COND_700,
            sx=1.0, extra=""):
    d = T.centered(font, txt, size, cx, baseline, tracking, sx)
    return f'<path d="{d}" fill="{fill}"{extra}/>'


def lx_text(txt, size, x, baseline, fill, tracking=0.0, font=B.F_COND_700, sx=1.0):
    d, _ = T.text_path(font, txt, size, tracking, x, baseline, sx)
    return f'<path d="{d}" fill="{fill}"/>'


def w_of(txt, size, tracking=0.0, font=B.F_COND_700, sx=1.0):
    return T.measure(font, txt, size, tracking, sx)[0]


def fit(txt, max_w, size, tracking=0.0, font=B.F_COND_700):
    """Largest size <= `size` at which `txt` fits inside `max_w`."""
    s = size
    while s > 6 and w_of(txt, s, tracking, font) > max_w:
        s -= 0.5
    return s


def write(name, content):
    p = os.path.join(OUT, name)
    with open(p, "w") as f:
        f.write(content)
    return p


# ═══════════════════════════════════════════════════════════════════════
# CONCEPT 01 — GROUNDLINE BADGE
# The story in one shape: the horizon starts wild on the left and ends
# graded and clean on the right. That transition *is* the business.
# ═══════════════════════════════════════════════════════════════════════
def concept_01(mono=None, reverse=False):
    W, H = 620, 700
    ink = mono or (B.BONE if reverse else B.INK_900)
    moss = mono or B.MOSS_500
    bone = mono and B.INK_900 or B.BONE
    plate = "none" if mono else (B.INK_900 if not reverse else B.INK_900)

    s = []
    # plate
    s.append(f'<path d="{B.octagon(10, 10, W - 20, H - 20, 62)}" fill="{plate}" '
             f'stroke="{moss}" stroke-width="9"/>')
    s.append(f'<path d="{B.octagon(30, 30, W - 60, H - 60, 50)}" fill="none" '
             f'stroke="{moss if mono else B.MOSS_700}" stroke-width="3"/>')

    # ── scene band: wild → cleared ──────────────────────────────────
    gy = 250                       # ground baseline inside the badge
    sx0, sx1 = 58, W - 58
    cut = 322                      # where the blade line falls

    s.append(f'<clipPath id="c1scene"><rect x="{sx0}" y="86" '
             f'width="{sx1 - sx0}" height="{gy - 86}"/></clipPath>')
    s.append(f'<g clip-path="url(#c1scene)">')
    # uncleared half
    s.append(f'<path d="{B.brush_silhouette(sx0 - 10, cut, gy, 74, seed=11, density=20)}" '
             f'fill="{moss if mono else B.MOSS_700}"/>')
    s.append(f'<path d="{B.conifer(112, gy, 132, 74)}" fill="{moss if mono else B.MOSS_600}"/>')
    s.append(f'<path d="{B.hardwood(232, gy, 150, 120)}" fill="{moss if mono else B.MOSS_500}"/>')
    s.append(f'<path d="{B.conifer(300, gy, 96, 54)}" fill="{moss if mono else B.MOSS_700}"/>')
    # cleared half — graded terrace + one kept specimen tree
    s.append(f'<path d="M{cut},{gy} H{sx1 + 10} V{gy - 22} H{cut + 96} '
             f'L{cut + 40},{gy - 46} H{cut} Z" fill="{moss if mono else B.MOSS_600}"/>')
    s.append(f'<path d="{B.hardwood(468, gy - 22, 118, 96)}" fill="{moss if mono else B.MOSS_500}"/>')
    s.append("</g>")
    # the cut — a blade line through the horizon
    s.append(f'<path d="M{cut + 26},80 L{cut - 16},{gy + 6}" stroke="{B.AMBER_500 if not mono else mono}" '
             f'stroke-width="7" stroke-linecap="square"/>')
    # ground rule
    s.append(f'<rect x="{sx0}" y="{gy}" width="{sx1 - sx0}" height="9" fill="{moss}"/>')

    # ── wordmark ────────────────────────────────────────────────────
    s.append(cx_text("M&W", 284, W / 2, 470, bone if not mono else mono, -0.012))
    s.append(cx_text("GROUNDWORKS", 92, W / 2, 540, moss, 0.055))

    # ── strapline bar ───────────────────────────────────────────────
    by, bw = 566, sx1 - sx0
    s.append(f'<rect x="{sx0}" y="{by}" width="{bw}" height="52" fill="{moss}"/>')
    fs = fit("CLEAR · BUILD · MAINTAIN", bw - 56, 42, 0.16)
    s.append(cx_text("CLEAR · BUILD · MAINTAIN", fs, W / 2, by + 26 + fs * CAP / 2,
                     B.INK_900 if not mono else B.BONE, 0.16))
    fs2 = fit("JEFFERSON COUNTY, MISSOURI", bw - 40, 30, 0.19, B.F_COND_600)
    s.append(cx_text("JEFFERSON COUNTY, MISSOURI", fs2, W / 2, 652,
                     (B.BONE_MUTE if not mono else mono), 0.19, font=B.F_COND_600))

    bg = None if mono else (B.BONE if reverse else None)
    return B.svg(W, H, "".join(s), bg=bg,
                 title="M&W GroundWorks — Groundline Badge")


# ═══════════════════════════════════════════════════════════════════════
# CONCEPT 02 — THE CUT (horizontal lockup)
# Built for the side of a truck and the top of a website. Reads at 30 feet.
# ═══════════════════════════════════════════════════════════════════════
def cut_icon(x, y, size, moss, amber, uid="c2"):
    """The square 'cut' icon: wild on the left, graded on the right,
    with an amber blade line marking where the work happened."""
    k = size / 200.0
    s = [f'<path d="{B.octagon(x, y, size, size, 30 * k)}" fill="none" '
         f'stroke="{moss}" stroke-width="{7 * k:.1f}"/>']
    s.append(f'<clipPath id="{uid}"><path '
             f'd="{B.octagon(x + 8 * k, y + 8 * k, size - 16 * k, size - 16 * k, 26 * k)}"/></clipPath>')
    s.append(f'<g clip-path="url(#{uid})">')
    gy = y + size * 0.66
    mid = x + size * 0.52
    s.append(f'<path d="{B.brush_silhouette(x, mid, gy, size * 0.30, seed=5, density=9)}" fill="{moss}"/>')
    s.append(f'<path d="{B.conifer(x + size * 0.20, gy, size * 0.44, size * 0.22)}" fill="{moss}"/>')
    s.append(f'<path d="M{mid},{gy} H{x + size} V{gy - size * 0.10} '
             f'H{mid + size * 0.26:.1f} Z" fill="{moss}"/>')
    s.append(f'<rect x="{x}" y="{gy}" width="{size}" height="{size * 0.055:.1f}" fill="{moss}"/>')
    for i in range(3):
        s.append(f'<rect x="{x}" y="{gy + size * (0.10 + i * 0.09):.1f}" width="{size}" '
                 f'height="{size * 0.055:.1f}" fill="{moss}" opacity="{0.55 - i * 0.15:.2f}"/>')
    s.append(f'<path d="M{mid + size * 0.10:.1f},{y + size * 0.10:.1f} '
             f'L{mid - size * 0.06:.1f},{gy + size * 0.04:.1f}" stroke="{amber}" '
             f'stroke-width="{8 * k:.1f}" stroke-linecap="square"/>')
    s.append("</g>")
    return "".join(s)


def concept_02(mono=None):
    """Horizontal lockup built for a truck door and a website header."""
    W, H = 1240, 300
    bone = mono or B.BONE
    moss = mono or B.MOSS_500
    dim = mono or B.BONE_DIM
    amber = mono or B.AMBER_500
    s = []
    if not mono:
        s.append(f'<rect width="{W}" height="{H}" fill="{B.INK_900}"/>')

    ic = 196
    s.append(cut_icon(52, (H - ic) / 2, ic, moss, amber))

    tx = 52 + ic + 54
    # M&W over GROUNDWORKS, optically locked to the same left edge
    mw_size, gw_size = 168, 82
    s.append(lx_text("M&W", mw_size, tx, 154, bone, -0.012))
    s.append(lx_text("GROUNDWORKS", gw_size, tx, 232, moss, 0.072))
    block_w = max(w_of("M&W", mw_size, -0.012), w_of("GROUNDWORKS", gw_size, 0.072))

    # rule + stacked descriptor, placed after the widest line
    rx = tx + block_w + 40
    s.append(f'<rect x="{rx}" y="{H / 2 - 76}" width="4" height="152" fill="{moss}" opacity="0.75"/>')
    dx = rx + 30
    for i, line in enumerate(["LAND &", "PROPERTY", "SERVICES"]):
        s.append(lx_text(line, 46, dx, 112 + i * 48, dim, 0.07, font=B.F_COND_600))
    s.append(lx_text("JEFFERSON COUNTY, MO", 26, dx, 252,
                     mono or B.MOSS_400, 0.14, font=B.F_COND_600))
    return B.svg(W, H, "".join(s), title="M&W GroundWorks — The Cut lockup")


# ═══════════════════════════════════════════════════════════════════════
# CONCEPT 03 — STRATA STACK
# Three bars = three service families = a soil cross-section.
# ═══════════════════════════════════════════════════════════════════════
def concept_03(mono=None):
    W, H = 720, 596
    bone = mono or B.BONE
    s = [f'<rect width="{W}" height="{H}" fill="{B.INK_900}"/>'] if not mono else []
    cx = W / 2
    s.append(cx_text("M&W", 272, cx, 208, bone, -0.014))
    rows = [("CLEAR", B.MOSS_500, B.INK_900),
            ("BUILD", B.AMBER_500, B.INK_900),
            ("MAINTAIN", B.MOSS_700, B.BONE)]
    y = 246
    for i, (label, fill, txt) in enumerate(rows):
        inset = 40 + i * 26
        s.append(f'<rect x="{inset}" y="{y}" width="{W - inset * 2}" height="58" '
                 f'fill="{mono or fill}"/>')
        s.append(cx_text(label, 44, cx, y + 42, (B.INK_900 if mono else txt), 0.22))
        y += 68
    s.append(cx_text("GROUNDWORKS", 76, cx, 522, mono or B.MOSS_500, 0.10))
    return B.svg(W, H, "".join(s), title="M&W GroundWorks — Strata Stack")


# ═══════════════════════════════════════════════════════════════════════
# CONCEPT 04 — BUCKET MARK (standalone icon)
# The W becomes an excavator bucket. Works at favicon size.
# ═══════════════════════════════════════════════════════════════════════
def concept_04(size=512, mono=None, plate=True):
    W = H = size
    k = size / 512.0
    moss = mono or B.MOSS_500
    bone = mono or B.BONE
    s = []
    if plate and not mono:
        s.append(f'<rect width="{W}" height="{H}" rx="{96 * k:.0f}" fill="{B.INK_900}"/>')
        s.append(f'<rect x="{14 * k:.0f}" y="{14 * k:.0f}" width="{W - 28 * k:.0f}" '
                 f'height="{H - 28 * k:.0f}" rx="{84 * k:.0f}" fill="none" '
                 f'stroke="{B.MOSS_700}" stroke-width="{6 * k:.0f}"/>')
    # M&W tight monogram
    s.append(cx_text("M&W", 196 * k, W / 2, 268 * k, bone, -0.03))
    # bucket teeth biting the baseline
    s.append(f'<rect x="{92 * k:.0f}" y="{296 * k:.0f}" width="{328 * k:.0f}" '
             f'height="{22 * k:.0f}" fill="{moss}"/>')
    s.append(f'<path d="{B.bucket_teeth(92 * k, 420 * k, 318 * k, 6, 30 * k)}" fill="{moss}"/>')
    s.append(cx_text("GROUNDWORKS", 46 * k, W / 2, 424 * k, moss, 0.10))
    return B.svg(W, H, "".join(s), title="M&W GroundWorks — Bucket Mark")


# ═══════════════════════════════════════════════════════════════════════
# CONCEPT 05 — SECTION RULE (premium editorial)
# For estimates, invoices, letterhead. The quiet one.
# ═══════════════════════════════════════════════════════════════════════
def concept_05(mono=None, on_bone=True):
    W, H = 1000, 340
    ink = mono or (B.INK_900 if on_bone else B.BONE)
    moss = mono or (B.MOSS_700 if on_bone else B.MOSS_500)
    s = []
    if not mono:
        s.append(f'<rect width="{W}" height="{H}" fill="{B.BONE if on_bone else B.INK_900}"/>')
    cx = W / 2
    s.append(cx_text("M & W", 128, cx, 148, ink, 0.02))
    s.append(f'<rect x="{cx - 300}" y="176" width="600" height="3" fill="{moss}"/>')
    s.append(f'<rect x="{cx - 300}" y="186" width="600" height="1.5" fill="{moss}" opacity="0.6"/>')
    s.append(f'<rect x="{cx - 300}" y="193" width="600" height="1" fill="{moss}" opacity="0.35"/>')
    s.append(cx_text("GROUNDWORKS", 78, cx, 258, ink, 0.30))
    s.append(cx_text("LAND & PROPERTY SERVICES · JEFFERSON COUNTY, MO", 26, cx, 300,
                     mono or (B.INK_500 if on_bone else B.BONE_MUTE), 0.22, font=B.F_COND_600))
    return B.svg(W, H, "".join(s), title="M&W GroundWorks — Section Rule")


# ═══════════════════════════════════════════════════════════════════════
# CONCEPT 06 — THE SEAL
# Circular. Embroiders, stamps, and survives a 32px favicon.
# ═══════════════════════════════════════════════════════════════════════
def concept_06(mono=None):
    W = H = 560
    c = W / 2
    moss = mono or B.MOSS_500
    bone = mono or B.BONE
    s = []
    if not mono:
        s.append(f'<circle cx="{c}" cy="{c}" r="{c - 6}" fill="{B.INK_900}"/>')
    s.append(f'<circle cx="{c}" cy="{c}" r="{c - 14}" fill="none" stroke="{moss}" stroke-width="8"/>')
    s.append(f'<circle cx="{c}" cy="{c}" r="{c - 40}" fill="none" stroke="{moss}" '
             f'stroke-width="2" opacity="0.55"/>')

    # circular type
    rr = c - 62
    s.append(f'<path id="sealTop" d="M{c - rr},{c} A{rr},{rr} 0 0 1 {c + rr},{c}" fill="none"/>')
    s.append(f'<path id="sealBot" d="M{c - rr + 8},{c + 6} A{rr - 8},{rr - 8} 0 0 0 {c + rr - 8},{c + 6}" fill="none"/>')

    # horizon inside
    gy = c + 22
    s.append(f'<clipPath id="s6"><circle cx="{c}" cy="{c}" r="{c - 44}"/></clipPath>')
    s.append('<g clip-path="url(#s6)">')
    s.append(f'<path d="{B.brush_silhouette(40, c, gy, 46, seed=3, density=12)}" fill="{moss}" opacity="0.85"/>')
    s.append(f'<path d="{B.conifer(112, gy, 74, 44)}" fill="{moss}" opacity="0.85"/>')
    s.append(f'<rect x="{c}" y="{gy - 10}" width="{c}" height="12" fill="{moss}" opacity="0.85"/>')
    s.append("</g>")
    s.append(f'<rect x="72" y="{gy}" width="{W - 144}" height="6" fill="{moss}"/>')

    s.append(cx_text("M&W", 156, c, gy - 24, bone, -0.02))
    s.append(cx_text("GROUNDWORKS", 44, c, gy + 60, moss, 0.14))
    s.append(cx_text("CLEAR · BUILD · MAINTAIN", 26, c, gy + 96,
                     mono or B.BONE_MUTE, 0.18, font=B.F_COND_600))
    fs = fit("JEFFERSON COUNTY · MISSOURI", W - 190, 30, 0.20, B.F_COND_600)
    s.append(cx_text("JEFFERSON COUNTY · MISSOURI", fs, c, 118,
                     mono or B.BONE_DIM, 0.20, font=B.F_COND_600))
    return B.svg(W, H, "".join(s), title="M&W GroundWorks — The Seal")


# ═══════════════════════════════════════════════════════════════════════
# SUPPORTING MARKS
# ═══════════════════════════════════════════════════════════════════════
def favicon(size=64):
    k = size / 64.0
    s = [f'<rect width="{size}" height="{size}" rx="{12 * k:.1f}" fill="{B.INK_900}"/>']
    s.append(cx_text("M&W", 34 * k, size / 2, 38 * k, B.BONE, -0.03))
    s.append(f'<rect x="{10 * k:.1f}" y="{43 * k:.1f}" width="{44 * k:.1f}" '
             f'height="{4 * k:.1f}" fill="{B.MOSS_500}"/>')
    s.append(f'<path d="{B.bucket_teeth(10 * k, 54 * k, 47 * k, 4, 6 * k)}" fill="{B.MOSS_500}"/>')
    return B.svg(size, size, "".join(s), title="M&W GroundWorks")


def nav_lockup():
    """Compact horizontal mark for the site header. Legible at 34px tall."""
    H = 92
    ic = 78
    s = [cut_icon(2, (H - ic) / 2, ic, B.MOSS_500, B.AMBER_500, uid="nv")]
    tx = 2 + ic + 20
    mw_s, gw_s = 56, 25
    s.append(lx_text("M&W", mw_s, tx, 50, B.BONE, -0.012))
    s.append(lx_text("GROUNDWORKS", gw_s, tx, 76, B.MOSS_400, 0.095))
    block = max(w_of("M&W", mw_s, -0.012), w_of("GROUNDWORKS", gw_s, 0.095))
    W = int(tx + block + 8)
    return B.svg(W, H, "".join(s), title="M&W GroundWorks")


if __name__ == "__main__":
    files = {
        "01-groundline-badge.svg": concept_01(),
        "01-groundline-badge-1c.svg": concept_01(mono=B.INK_900),
        "02-the-cut.svg": concept_02(),
        "02-the-cut-1c.svg": concept_02(mono=B.INK_900),
        "03-strata-stack.svg": concept_03(),
        "04-bucket-mark.svg": concept_04(),
        "04-bucket-mark-1c.svg": concept_04(mono=B.INK_900, plate=False),
        "05-section-rule.svg": concept_05(),
        "05-section-rule-dark.svg": concept_05(on_bone=False),
        "06-the-seal.svg": concept_06(),
        "06-the-seal-1c.svg": concept_06(mono=B.INK_900),
        "favicon.svg": favicon(),
        "nav-lockup.svg": nav_lockup(),
    }
    for name, content in files.items():
        p = write(name, content)
        print(f"{os.path.getsize(p):>7,}  {name}")
