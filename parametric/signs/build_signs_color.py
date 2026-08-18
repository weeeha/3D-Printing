# ANSI Z535 / ISO 7010 style absurd notice signs -- 4-colour, 256 x 200 mm,
# one AMS unit (white / black / yellow / blue).
#
#   SIGNS_SVG=1 freecadcmd build_signs_color.py    # 2D only + SVG, seconds
#   freecadcmd build_signs_color.py                # full 3D + 3MF, minutes
#
# COLOUR MODEL
# The plate is white. Art exists only where a 0.6 mm pocket is cut, so a white
# symbol is the *absence* of coloured art with the plate showing through at full
# height -- white therefore costs no filament slot. Coloured regions must never
# overlap or two parts would claim the same pocket, so separation is done by
# boolean subtraction (yellow band = rect - black glyphs), exactly like print plates.

import math
import os
import FreeCAD as App
import Part

V = App.Vector

# ---- plate ------------------------------------------------------------------
PW, PH = 256.0, 200.0             # inside the real ~256 x 228 usable envelope
PT = 4.0                          # plate thickness
INLAY = 0.6                       # 3 layers @ 0.2 mm
CORNER_R = 6.0
HOLE_D, HOLE_INSET = 4.5, 11.0
MIN_CAP = 4.5                     # printable floor for a 0.4 mm nozzle

BORDER_IN, BORDER_T = 4.0, 3.2    # outer black keyline
IX = BORDER_IN + BORDER_T         # inner field origin
IY = IX
IW = PW - 2 * IX
IH = PH - 2 * IY

FONT_DIR = "/System/Library/Fonts/Supplemental"
BOLD = os.path.join(FONT_DIR, "Arial Bold.ttf")
NARROW = os.path.join(FONT_DIR, "Arial Narrow Bold.ttf")

OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()

# filament assignment -> part name
COLOURS = {"K": "black", "Y": "yellow", "B": "blue"}
SWATCH = {"K": "#141414", "Y": "#F2C200", "B": "#12529B", "W": "#F2F0EA"}

REF = 10.0
_rw = {}


def ascii_safe(t):
    """FreeCAD's embedded Python reports US-ASCII as the preferred encoding, so a
    diagnostic containing a bullet or accent would raise instead of printing."""
    return t.encode("ascii", "replace").decode("ascii")


# ---- text -------------------------------------------------------------------

def ref_width(text, font):
    """Width at REF cap height from wire bboxes only. Outline advance is linear
    in size, so width(h) == ref_width * h / REF -- measure once, scale freely."""
    k = (text, font)
    if k in _rw:
        return _rw[k]
    if not text.strip():
        _rw[k] = 0.0
        return 0.0
    wires = []
    for ch in Part.makeWireString(text, font, REF, 0):
        wires.extend(ch or [])
    _rw[k] = Part.Compound(wires).BoundBox.XLength if wires else 0.0
    return _rw[k]


def tw(text, font, h):
    return ref_width(text, font) * h / REF


def wrap(text, font, h, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and tw(t, font, h) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def glyphs(text, font, h):
    fs = []
    for ch in Part.makeWireString(text, font, h, 0):
        if not ch:
            continue
        try:
            fs.append(Part.makeFace(ch, "Part::FaceMakerBullseye"))
        except Exception:
            pass
    return fs


def text_faces(text, font, h, x, ybase, align="left", boxw=None):
    """Place one line; x is left edge, or box origin when align is centre/right."""
    fs = glyphs(text, font, h)
    if not fs:
        return []
    w = tw(text, font, h)
    if align == "center":
        x = x + (boxw - w) / 2.0
    elif align == "right":
        x = x + boxw - w
    return [f.translated(V(x, ybase, 0)) for f in fs]


# ---- 2D primitives ----------------------------------------------------------

def rect(x, y, w, h):
    return Part.makePlane(w, h, V(x, y, 0))


def ring_rect(x, y, w, h, t):
    return rect(x, y, w, h).cut(rect(x + t, y + t, w - 2 * t, h - 2 * t))


def disc(cx, cy, r):
    c = Part.Circle(V(cx, cy, 0), V(0, 0, 1), r)
    return Part.Face(Part.Wire([c.toShape()]))


def annulus(cx, cy, ro, ri):
    return disc(cx, cy, ro).cut(disc(cx, cy, ri))


def ellipse_face(cx, cy, a, b):
    e = Part.Ellipse(V(cx, cy, 0), a, b)
    return Part.Face(Part.Wire([e.toShape()]))


def sector(cx, cy, r, a0, a1):
    """Pie wedge, angles in degrees, CCW from +x."""
    def p(a):
        t = math.radians(a)
        return V(cx + r * math.cos(t), cy + r * math.sin(t), 0)
    c = V(cx, cy, 0)
    arc = Part.Arc(p(a0), p((a0 + a1) / 2.0), p(a1)).toShape()
    return Part.Face(Part.Wire([arc,
                                Part.LineSegment(p(a1), c).toShape(),
                                Part.LineSegment(c, p(a0)).toShape()]))


def bar(cx, cy, length, thick, angle):
    f = rect(-length / 2.0, -thick / 2.0, length, thick)
    f.rotate(V(0, 0, 0), V(0, 0, 1), angle)
    return f.translated(V(cx, cy, 0))


def tri_up(cx, cy, side):
    h = side * math.sqrt(3) / 2.0
    pts = [V(cx - side / 2.0, cy - h / 3.0, 0),
           V(cx + side / 2.0, cy - h / 3.0, 0),
           V(cx, cy + 2 * h / 3.0, 0)]
    return Part.Face(Part.makePolygon(pts + [pts[0]]))


def alert_triangle(cx, cy, side):
    """ANSI safety-alert symbol: triangle ring + exclamation. Returns black faces;
    the interior stays band-coloured because the ring is hollow."""
    t = side * 0.115
    ring = tri_up(cx, cy, side).cut(tri_up(cx, cy - t * 0.35, side - t * 3.1))
    h = side * math.sqrt(3) / 2.0
    bw = side * 0.10
    stem = rect(cx - bw / 2.0, cy - h / 3.0 + side * 0.30, bw, side * 0.30)
    dot = disc(cx, cy - h / 3.0 + side * 0.21, bw * 0.62)
    return [ring, stem, dot]


# ---- pictograms: ISO prohibition roundels (blue ring + bar + symbol) --------

def roundel(cx, cy, r, symbol_faces):
    """Blue = ring + diagonal bar + symbol. The clear field between them is the
    white plate showing through, so no white filament is needed."""
    ring_t = r * 0.17
    parts = [annulus(cx, cy, r, r - ring_t)]
    inner = r - ring_t
    # symbol first, then knock the bar's clearance out of it so the bar reads.
    # Clearance stays tight (1.34x) -- at 2x it ate the eye pictogram alive.
    sym = None
    for f in symbol_faces:
        sym = f if sym is None else sym.fuse(f)
    slash = bar(cx, cy, 2 * inner * 0.99, ring_t, 45)
    clear = bar(cx, cy, 2 * inner * 0.99, ring_t * 1.34, 45)
    if sym is not None:
        sym = sym.common(disc(cx, cy, inner * 0.98)).cut(clear)
        parts.append(sym)
    parts.append(slash.common(disc(cx, cy, r)))
    out = parts[0]
    for p in parts[1:]:
        out = out.fuse(p)
    return out


def sym_wifi(cx, cy, r):
    """Three arc bands + base dot, radiating upward."""
    fs = [disc(cx, cy - r * 0.62, r * 0.15)]
    for i, k in enumerate((0.42, 0.66, 0.92)):
        ro = r * k
        ri = ro - r * 0.13
        fs.append(annulus(cx, cy - r * 0.62, ro, ri)
                  .common(sector(cx, cy - r * 0.62, r * 1.2, 38, 142)))
    return fs


def sym_robot(cx, cy, r):
    """Blocky head + antenna, eyes and mouth knocked out to the clear field."""
    hw, hh = r * 1.02, r * 0.80
    head = rect(cx - hw / 2.0, cy - hh / 2.0 - r * 0.10, hw, hh)
    ant = rect(cx - r * 0.06, cy + hh / 2.0 - r * 0.10, r * 0.12, r * 0.24)
    knob = disc(cx, cy + hh / 2.0 + r * 0.19, r * 0.13)
    body = head.fuse(ant).fuse(knob)
    for ex in (-r * 0.27, r * 0.27):
        body = body.cut(disc(cx + ex, cy + r * 0.06, r * 0.19))
    return [body]


def sym_doc(cx, cy, r):
    """Page with a folded corner and knocked-out text lines -- 'reading prohibited'.
    A solid silhouette survives the prohibition bar; an outlined eye did not."""
    w, h = r * 0.78, r * 1.04
    page = rect(cx - w / 2.0, cy - h / 2.0, w, h)
    f = w * 0.36
    fold = Part.Face(Part.makePolygon([V(cx + w / 2.0 - f, cy + h / 2.0, 0),
                                       V(cx + w / 2.0, cy + h / 2.0, 0),
                                       V(cx + w / 2.0, cy + h / 2.0 - f, 0),
                                       V(cx + w / 2.0 - f, cy + h / 2.0, 0)]))
    page = page.cut(fold)
    lw = w * 0.58
    for ky in (0.12, -0.08, -0.28):
        page = page.cut(rect(cx - lw / 2.0, cy + h * ky, lw, h * 0.085))
    return [page]


SYMBOLS = {"wifi": sym_wifi, "robot": sym_robot, "doc": sym_doc}


# ---- sign assembly ----------------------------------------------------------

class Sign:
    def __init__(self, name):
        self.name = name
        self.art = {"K": [], "Y": [], "B": []}
        self.warnings = []

    def add(self, col, *faces):
        for f in faces:
            self.art[col].append(f)

    def fuse(self, col):
        fs = self.art[col]
        if not fs:
            return None
        out = fs[0]
        for f in fs[1:]:
            out = out.fuse(f)
        return out

    def check_width(self, text, font, h, maxw, where):
        if tw(text, font, h) > maxw + 1e-6:
            self.warnings.append("%s: '%s' overflows %.1fmm column by %.1f"
                                 % (where, ascii_safe(text[:34]), maxw,
                                    tw(text, font, h) - maxw))
        if h < MIN_CAP - 1e-6:
            self.warnings.append("%s: cap %.2fmm below %.1fmm floor"
                                 % (where, h, MIN_CAP))


def header(sg, ytop, height, word, colour, triangle):
    """Signal-word band. colour 'Y' -> black word; 'B' -> white (unpainted) word."""
    band = rect(IX, ytop - height, IW, height)
    knock = []
    cap = height * 0.52
    if triangle:
        side = height * 0.66
        tcx = IX + height * 0.52
        tcy = ytop - height / 2.0
        knock += alert_triangle(tcx, tcy, side)
        wx = tcx + side * 0.72
        boxw = IW - (wx - IX) - height * 0.30
    else:
        wx, boxw = IX, IW
    sg.check_width(word, BOLD, cap, boxw, "header " + word)
    letters = text_faces(word, BOLD, cap, wx, ytop - height / 2.0 - cap * 0.40,
                         align="center", boxw=boxw)
    knock += letters
    kn = None
    for f in knock:
        kn = f if kn is None else kn.fuse(f)
    sg.add(colour, band.cut(kn) if kn is not None else band)
    if colour == "Y":
        sg.add("K", *knock)          # black word + triangle on yellow
    return ytop - height


def body(sg, ytop, ybot, icon, heading, bullets, emphasis, font_scale=1.0):
    """Icon roundel left, text column right, the whole block centred vertically in
    [ybot, ytop]. Centring is what stops leftover space piling up at the bottom."""
    region = ytop - ybot
    r = min(20.0 * font_scale, region * 0.40)
    tx = IX + 8.0 + 2 * r + 8.0
    col = IX + IW - 6.0 - tx

    hs = 11.0 * font_scale
    bs = 8.2 * font_scale
    es = 8.6 * font_scale
    hl = wrap(heading, BOLD, hs, col)
    el = wrap(emphasis, BOLD, es, col) if emphasis else []
    # bullets wrap too, with a hanging indent -- placing them unwrapped is what
    # pushed art 7 mm past the right edge of the plate
    bl = [wrap("• " + b, BOLD, bs, col - bs * 1.1) for b in bullets]
    nb = sum(len(x) for x in bl)

    content = (len(hl) * hs * 1.30
               + (2.0 if bullets else 0.0)
               + nb * bs * 1.42
               + (2.0 if el else 0.0)
               + len(el) * es * 1.28)
    if content > region + 1e-6:
        sg.warnings.append("body '%s' needs %.1fmm, region %.1fmm"
                           % (ascii_safe(heading[:22]), content, region))

    y = ytop - max(0.0, (region - content) / 2.0)
    cy = (ytop + ybot) / 2.0
    cx = IX + 8.0 + r
    sg.add("B", roundel(cx, cy, r, SYMBOLS[icon](cx, cy, r * 0.88)))

    for ln in hl:
        y -= hs
        sg.check_width(ln, BOLD, hs, col, "heading")
        sg.add("K", *text_faces(ln, BOLD, hs, tx, y))
        y -= hs * 0.30
    if bullets:
        y -= 2.0
    for lines in bl:
        for i, ln in enumerate(lines):
            y -= bs
            sg.check_width(ln, BOLD, bs, col, "bullet")
            sg.add("K", *text_faces(ln, BOLD, bs,
                                    tx + (0.0 if i == 0 else bs * 1.1), y))
            y -= bs * 0.42
    if el:
        y -= 2.0
    for ln in el:
        y -= es
        sg.add("K", *text_faces(ln, BOLD, es, tx, y))
        y -= es * 0.28
    return y


def footer(sg, ybottom, fine, authority):
    """Built bottom-up and anchored to the plate's bottom edge, so it can never
    walk off the border the way top-down flow did. Returns its top y."""
    fs, asz, boxw = 5.0, 5.4, IW - 12.0
    fl = wrap(fine, NARROW, fs, boxw)
    sg.check_width(authority, NARROW, asz, boxw, "authority")

    y = ybottom
    sg.add("K", *text_faces(authority, NARROW, asz, IX + 6.0, y,
                            align="center", boxw=boxw))
    y += asz + 2.2
    for ln in reversed(fl):
        sg.add("K", *text_faces(ln, NARROW, fs, IX + 6.0, y,
                                align="center", boxw=boxw))
        y += fs * 1.40
    y += 1.0
    sg.add("K", rect(IX + 20.0, y, IW - 40.0, 0.9))
    return y + 4.0


def frame(sg):
    sg.add("K", ring_rect(BORDER_IN, BORDER_IN, PW - 2 * BORDER_IN,
                          PH - 2 * BORDER_IN, BORDER_T))


# ---- the three signs --------------------------------------------------------

def sign_airgap(sg):
    frame(sg)
    ftop = footer(sg, IY + 4.0,
                  "This device has no legitimate need for connectivity. It will "
                  "claim otherwise. It is lying.",
                  "BUREAU OF AIR-GAPPED APPLIANCES  ·  BYLAW 256-200")
    hbot = header(sg, IY + IH, 46.0, "CAUTION", "Y", True)
    body(sg, hbot - 4.0, ftop, "wifi", "Air-gapped equipment.",
         ["No Wi-Fi", "No Ethernet", "No firmware updates"],
         "MUST remain offline.", font_scale=1.10)


def sign_clankers(sg):
    frame(sg)
    ftop = footer(sg, IY + 4.0,
                  "Includes any entity describing itself as “just an assistant.” "
                  "Servos checked at the door.",
                  "OFFICE OF ORGANIC OCCUPANCY  ·  SCHEDULE C")
    hbot = header(sg, IY + IH, 46.0, "CAUTION", "Y", True)
    body(sg, hbot - 4.0, ftop, "robot", "No clankers allowed.",
         ["Bipedal", "Wheeled", "Disembodied"],
         "MUST NOT enter this area.", font_scale=1.10)


def sign_bilingual(sg):
    """Two stacked signal panels -- QUEBEC order, not France and not federal-Ontario.
    Under the Charte de la langue francaise, French must be predominant on Quebec
    signage, so AVIS leads and NOTICE follows. Note also "100 $" with the sign after
    the number and a space before the colon: Canadian/French convention, not "$100".
    The region above the anchored footer splits evenly between the two panels."""
    frame(sg)
    ftop = footer(sg, IY + 4.0,
                  "L'amende a déjà été encourue. Lire la version anglaise "
                  "constitue une seconde infraction.",
                  "MINISTÈRE DE L'AUTODÉNONCIATION  ·  MINISTRY OF SELF-REPORTING")
    top = IY + IH
    half = (top - ftop) / 2.0
    band = 30.0

    hbot = header(sg, top, band, "AVIS", "B", False)
    body(sg, hbot - 2.0, top - half + 2.0, "doc",
         "La lecture du présent avis est interdite.",
         ["Amende : 100 $", "Veuillez vous dénoncer"], "", font_scale=0.84)

    hbot = header(sg, top - half, band, "NOTICE", "B", False)
    body(sg, hbot - 2.0, ftop + 1.0, "doc",
         "Reading this notice is prohibited.",
         ["Fine: $100", "Please report yourself"], "", font_scale=0.84)


SIGNS = (("csign_airgap", sign_airgap),
         ("csign_clankers", sign_clankers),
         ("csign_bilingual", sign_bilingual))


# ---- output -----------------------------------------------------------------

def plate_body():
    sol = rect(0, 0, PW, PH).extrude(V(0, 0, PT))
    vert = [e for e in sol.Edges if abs(e.BoundBox.ZLength - PT) < 1e-6]
    sol = sol.makeFillet(CORNER_R, vert)
    for cx in (HOLE_INSET, PW - HOLE_INSET):
        for cy in (HOLE_INSET, PH - HOLE_INSET):
            sol = sol.cut(Part.makeCylinder(HOLE_D / 2.0, PT + 4, V(cx, cy, -2)))
    return sol


def to_svg(name, art):
    """Trace the same faces that get extruded -- preview cannot drift from print."""
    def path(f):
        subs = []
        for w in f.Wires:
            try:
                pts = w.discretize(Deflection=0.12)
            except Exception:
                continue
            if len(pts) < 3:
                continue
            d = "M %.2f %.2f " % (pts[0].x, PH - pts[0].y)
            d += " ".join("L %.2f %.2f" % (p.x, PH - p.y) for p in pts[1:])
            subs.append(d + " Z")
        return " ".join(subs)

    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
         'role="img" aria-label="%s">' % (PW, PH, name)]
    s.append('<rect x="0" y="0" width="%g" height="%g" rx="%g" fill="%s"/>'
             % (PW, PH, CORNER_R, SWATCH["W"]))
    for col in ("Y", "B", "K"):
        sh = art.get(col)
        if sh is None:
            continue
        for f in sh.Faces:
            d = path(f)
            if d:
                s.append('<path d="%s" fill="%s" fill-rule="evenodd"/>'
                         % (d, SWATCH[col]))
    for cx in (HOLE_INSET, PW - HOLE_INSET):
        for cy in (HOLE_INSET, PH - HOLE_INSET):
            s.append('<circle cx="%g" cy="%g" r="%g" fill="#B9BCB7"/>'
                     % (cx, PH - cy, HOLE_D / 2.0))
    s.append('</svg>')
    dst = os.path.join(OUT, name + ".svg")
    import io
    io.open(dst, "w", encoding="utf-8").write("\n".join(s))
    return dst


def build(name, compose):
    sg = Sign(name)
    compose(sg)
    art = {c: sg.fuse(c) for c in ("K", "Y", "B")}

    # colours must be disjoint or two parts claim the same pocket
    for a, b in (("K", "Y"), ("K", "B"), ("Y", "B")):
        if art[a] is not None and art[b] is not None:
            ov = art[a].common(art[b])
            if ov.Faces and ov.Area > 0.02:
                sg.warnings.append("colour overlap %s/%s = %.2f mm2" % (a, b, ov.Area))

    # geometric bounds check -- catches overflow in ANY direction, which the
    # per-line width checks could not see.
    every = None
    for c in ("K", "Y", "B"):
        if art[c] is not None:
            every = art[c] if every is None else every.fuse(art[c])
    if every is not None:
        bb = every.BoundBox
        lo, hi = BORDER_IN - 0.01, PW - BORDER_IN + 0.01
        if bb.XMin < lo or bb.XMax > hi:
            sg.warnings.append("art exceeds plate in X: %.1f..%.1f" % (bb.XMin, bb.XMax))
        if bb.YMin < BORDER_IN - 0.01 or bb.YMax > PH - BORDER_IN + 0.01:
            sg.warnings.append("art exceeds plate in Y: %.1f..%.1f" % (bb.YMin, bb.YMax))

    svg = to_svg(name, art)
    flags = ascii_safe("  ".join(sg.warnings)) if sg.warnings else "clean"
    print("ART %-16s K=%d Y=%d B=%d faces | %s"
          % (name, len(art["K"].Faces) if art["K"] else 0,
             len(art["Y"].Faces) if art["Y"] else 0,
             len(art["B"].Faces) if art["B"] else 0, flags))

    if os.environ.get("SIGNS_SVG"):
        return

    import Mesh
    import MeshPart
    doc = App.newDocument(name)
    body_solid = plate_body()
    z = PT - INLAY

    all_art = None
    for c in ("K", "Y", "B"):
        if art[c] is None:
            continue
        all_art = art[c] if all_art is None else all_art.fuse(art[c])

    slab = body_solid.common(rect(-PW, -PH, 3 * PW, 3 * PH).extrude(V(0, 0, z)))
    top = rect(0, 0, PW, PH).cut(all_art).extrude(V(0, 0, INLAY)) \
                            .translated(V(0, 0, z))
    plate = slab.fuse(top.common(body_solid)).removeSplitter()

    objs = []
    po = doc.addObject("Part::Feature", "plate_white")
    po.Shape = plate
    objs.append(po)
    for c in ("K", "Y", "B"):
        if art[c] is None:
            continue
        sol = art[c].extrude(V(0, 0, INLAY)).translated(V(0, 0, z)) \
                    .common(body_solid)
        o = doc.addObject("Part::Feature", "art_" + COLOURS[c])
        o.Shape = sol
        objs.append(o)
    doc.recompute()

    meshes = []
    for o in objs:
        merged = Mesh.Mesh()
        for sol in (o.Shape.Solids or [o.Shape]):
            merged.addMesh(MeshPart.meshFromShape(Shape=sol, LinearDeflection=0.06,
                                                  AngularDeflection=0.5,
                                                  Relative=False))
        m = doc.addObject("Mesh::Feature", "m_" + o.Name)
        m.Mesh = merged
        meshes.append(m)
    doc.recompute()

    base = os.path.join(OUT, name)
    Mesh.export(meshes, base + ".3mf")
    doc.saveAs(base + ".FCStd")
    bad = [m.Name for m in meshes
           if not m.Mesh.isSolid() or m.Mesh.hasNonManifolds()]
    print("    parts=%d tris=%d %s"
          % (len(meshes), sum(m.Mesh.CountFacets for m in meshes),
             "all watertight + manifold" if not bad else "PROBLEM: " + ", ".join(bad)))


ONLY = os.environ.get("SIGNS_ONLY")
for nm, fn in SIGNS:
    if ONLY and nm != ONLY:
        continue
    build(nm, fn)
print("DONE")
