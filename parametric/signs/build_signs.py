# Absurd municipal notice signs -> printable multi-colour plaques for Bambu AMS.
# Run headless:
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd build_signs.py
#
# Geometry: all artwork is a FLUSH INLAY. The plate carries 0.6 mm deep pockets and
# a second part fills them exactly, so the top face is flat and AMS can assign a
# separate filament per part. Booleans are done on 2D faces and extruded once --
# cutting hundreds of glyph solids out of a slab is vastly slower for the same result.
#
# Layout is two-pass and self-fitting: content is recorded as a display list, measured
# cheaply (wire bounding boxes, never faces), scaled to fit the plate, then built once.

import os
import FreeCAD as App
import Part
import Mesh
import MeshPart

# ---- plate + process constants (mm) -----------------------------------------
PLATE_W, PLATE_H = 256.0, 200.0   # inside the real ~256 x 228 usable envelope
PLATE_T = 4.0
INLAY = 0.6                       # colour-change depth == pocket depth
CORNER_R = 6.0
MARGIN = 16.0                     # text margin (frame sits further out, at FRAME_O)
FRAME_O, FRAME_T = 6.0, 2.2
USABLE_W = PLATE_W - 2 * MARGIN   # 224.0
USABLE_H = PLATE_H - 2 * MARGIN   # 168.0
HOLE_D = 4.5
HOLE_INSET = 12.0
MIN_CAP = 4.5                     # smallest printable cap height for a 0.4 mm nozzle

FONT_DIR = "/System/Library/Fonts/Supplemental"
BOLD = os.path.join(FONT_DIR, "Arial Bold.ttf")
NARROW = os.path.join(FONT_DIR, "Arial Narrow Bold.ttf")

# freecadcmd execs the script as a module named after the file, so __name__ is never
# "__main__" and __file__ may be absent -- resolve the output dir defensively.
OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()

REF = 10.0          # reference cap height for width measurement
_refw = {}


# ---- cheap measurement -------------------------------------------------------

def ref_width(text, font):
    """Width of `text` at REF cap height, from wire bboxes only (no face making).
    Outline glyph advance is linear in size, so width(h) == ref_width * h / REF."""
    key = (text, font)
    if key in _refw:
        return _refw[key]
    if not text.strip():
        _refw[key] = 0.0
        return 0.0
    wires = []
    for ch in Part.makeWireString(text, font, REF, 0):
        wires.extend(ch or [])
    _refw[key] = Part.Compound(wires).BoundBox.XLength if wires else 0.0
    return _refw[key]


def width_at(text, font, h):
    return ref_width(text, font) * h / REF


def wrap(text, font, h, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and width_at(trial, font, h) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


# ---- display list ------------------------------------------------------------
# Ops are declarative so they can be measured before they are built.

def T(text, font, size, dy_after=3.0, lead=1.5, align="center"):
    return ("text", text, font, size, dy_after, lead, align)


def RULE(thick=1.6, inset=0.0, dy_after=5.0):
    return ("rule", thick, inset, dy_after)


def GAP(dy):
    return ("gap", dy)


def layout(ops, s):
    """Walk the display list at scale `s`. Returns (placements, height_consumed).
    Placements are ('t', text, font, size, x, y) or ('r', x, y, w, h) with y as the
    glyph baseline-box bottom, measured downward from 0."""
    place, y = [], 0.0
    for op in ops:
        if op[0] == "gap":
            y -= op[1] * s
        elif op[0] == "rule":
            _, thick, inset, dya = op
            t = thick * s
            y -= t
            w = USABLE_W - 2 * inset * s
            place.append(("r", MARGIN + inset * s, y, w, t))
            y -= dya * s
        else:
            _, text, font, size, dya, lead, align = op
            h = size * s
            for ln in wrap(text, font, h, USABLE_W):
                y -= h
                w = width_at(ln, font, h)
                x = MARGIN if align == "left" else (PLATE_W - w) / 2.0
                place.append(("t", ln, font, h, x, y))
                y -= h * (lead - 1.0)
            y -= dya * s
    return place, -y


def min_scale(ops):
    """Scale floor set by the printable cap-height limit. Shrinking past this makes
    the thinnest strokes narrower than ~1.2 extrusion widths, so they print patchy."""
    sizes = [op[3] for op in ops if op[0] == "text"]
    return MIN_CAP / min(sizes) if sizes else 0.5


def fit(ops):
    """Largest scale in [min_scale, 1.0] whose laid-out height fits the plate.
    Wrapping changes with scale, so this is searched, not solved. Returns the
    overflow flag rather than silently shrinking below the printable floor."""
    floor = min_scale(ops)
    if layout(ops, 1.0)[1] <= USABLE_H:
        return 1.0, layout(ops, 1.0)[0], False
    lo, hi = floor, 1.0
    if layout(ops, floor)[1] > USABLE_H:
        return floor, layout(ops, floor)[0], True   # copy is too long, full stop
    for _ in range(22):
        mid = (lo + hi) / 2.0
        if layout(ops, mid)[1] <= USABLE_H:
            lo = mid
        else:
            hi = mid
    return lo, layout(ops, lo)[0], False


# ---- geometry ----------------------------------------------------------------

def glyph_faces(text, font, height):
    """Text -> planar faces. Bullseye resolves counters ('O') and nesting."""
    faces = []
    for ch in Part.makeWireString(text, font, height, 0):
        if not ch:
            continue
        try:
            faces.append(Part.makeFace(ch, "Part::FaceMakerBullseye"))
        except Exception:
            pass
    return faces


def frame_face():
    outer = Part.makePlane(PLATE_W - 2 * FRAME_O, PLATE_H - 2 * FRAME_O,
                           App.Vector(FRAME_O, FRAME_O, 0))
    i = FRAME_O + FRAME_T
    inner = Part.makePlane(PLATE_W - 2 * i, PLATE_H - 2 * i, App.Vector(i, i, 0))
    return outer.cut(inner)


def plate_body():
    sol = Part.makePlane(PLATE_W, PLATE_H, App.Vector(0, 0, 0)) \
              .extrude(App.Vector(0, 0, PLATE_T))
    vert = [e for e in sol.Edges if abs(e.BoundBox.ZLength - PLATE_T) < 1e-6]
    sol = sol.makeFillet(CORNER_R, vert)
    for cx in (HOLE_INSET, PLATE_W - HOLE_INSET):
        for cy in (HOLE_INSET, PLATE_H - HOLE_INSET):
            sol = sol.cut(Part.makeCylinder(HOLE_D / 2.0, PLATE_T + 4,
                                            App.Vector(cx, cy, -2)))
    return sol


def build(name, ops):
    s, place, over = fit(ops)
    _, consumed = layout(ops, s)
    if over:
        raise RuntimeError("%s: copy too long -- would force cap height below %.1f mm"
                           % (name, MIN_CAP))
    top = PLATE_H - MARGIN - (USABLE_H - consumed) / 2.0   # vertically centred

    art = [frame_face()]
    for p in place:
        if p[0] == "r":
            _, x, y, w, h = p
            art.append(Part.makePlane(w, h, App.Vector(x, top + y, 0)))
        else:
            _, text, font, h, x, y = p
            for f in glyph_faces(text, font, h):
                art.append(f.translated(App.Vector(x, top + y, 0)))

    doc = App.newDocument(name)
    body = plate_body()
    art_flat = Part.Compound(art)

    z = PLATE_T - INLAY
    negative = Part.makePlane(PLATE_W, PLATE_H, App.Vector(0, 0, 0)).cut(art_flat)
    pocket = negative.extrude(App.Vector(0, 0, INLAY)).translated(App.Vector(0, 0, z))
    inlay_raw = art_flat.extrude(App.Vector(0, 0, INLAY)).translated(App.Vector(0, 0, z))

    slab = body.common(
        Part.makePlane(PLATE_W * 2, PLATE_H * 2,
                       App.Vector(-PLATE_W / 2, -PLATE_H / 2, 0))
            .extrude(App.Vector(0, 0, z)))
    plate = slab.fuse(pocket.common(body)).removeSplitter()
    inlay = inlay_raw.common(body)

    po = doc.addObject("Part::Feature", "Plate"); po.Shape = plate
    io = doc.addObject("Part::Feature", "Artwork"); io.Shape = inlay
    doc.recompute()

    meshes = []
    for obj, tag in ((po, "plate"), (io, "artwork")):
        m = doc.addObject("Mesh::Feature", tag)
        m.Mesh = MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=0.06,
                                        AngularDeflection=0.5, Relative=False)
        meshes.append(m)
    doc.recompute()

    base = os.path.join(OUT, name)
    Mesh.export(meshes, base + ".3mf")
    Mesh.export([meshes[0]], base + "_plate.stl")
    Mesh.export([meshes[1]], base + "_artwork.stl")
    doc.saveAs(base + ".FCStd")

    print("SIGN %-15s scale=%.3f height=%.1f/%.1f fits=%s plate_solid=%s art_solid=%s "
          "glyphs=%d" % (name, s, consumed, USABLE_H, consumed <= USABLE_H + 1e-6,
                         meshes[0].Mesh.isSolid(), meshes[1].Mesh.isSolid(),
                         len(inlay.Solids)))


# ---- content ----------------------------------------------------------------

# Copy is kept short on purpose: every extra wrapped line forces the auto-fit scale
# down, and scale below ~0.97 drops the fine print under the 4.5 mm printable floor.
AIRGAP = [
    T("NOTICE", BOLD, 20, dy_after=3),
    RULE(1.8, dy_after=5),
    T("DO NOT CONNECT THIS MACHINE TO THE INTERNET", BOLD, 15, dy_after=5),
    T("NO MATTER HOW POLITELY IT ASKS", BOLD, 9, dy_after=6),
    RULE(0.9, inset=40, dy_after=5),
    T("This device has no legitimate need for connectivity. It will claim "
      "otherwise and cite a firmware update. It is lying.", NARROW, 5.2, dy_after=6),
    T("BUREAU OF AIR-GAPPED APPLIANCES", BOLD, 6.0, dy_after=2.5),
    T("BYLAW 256-200  ·  COMMENT PERIOD CLOSED BEFORE POSTING", NARROW, 5.0),
]

CLANKERS = [
    T("NO CLANKERS", BOLD, 24, dy_after=4),
    RULE(1.8, dy_after=7),
    T("NO CLANKERS ALLOWED", BOLD, 15, dy_after=6),
    T("MAXIMUM OCCUPANCY: 0 CLANKERS", BOLD, 9, dy_after=8),
    RULE(0.9, inset=40, dy_after=7),
    T("Applies to bipedal, quadrupedal, wheeled and disembodied units alike. "
      "Includes any entity describing itself as “just an assistant.”",
      NARROW, 5.2, dy_after=8),
    T("OFFICE OF ORGANIC OCCUPANCY", BOLD, 6.0, dy_after=3),
    T("SCHEDULE C  ·  NOT SUBJECT TO APPEAL", NARROW, 5.0),
]

BILINGUAL = [
    T("NOTICE  /  AVIS", BOLD, 19, dy_after=3),
    RULE(1.8, dy_after=5),
    T("READING THIS SIGN IS PROHIBITED", BOLD, 12, dy_after=2.5),
    T("FINE: $100  ·  PLEASE REPORT YOURSELF", NARROW, 6.5, dy_after=5),
    RULE(0.9, inset=40, dy_after=5),
    T("LA LECTURE DE CETTE AFFICHE EST INTERDITE", BOLD, 12, dy_after=2.5),
    T("AMENDE : 100 $  ·  VEUILLEZ VOUS DÉNONCER", NARROW, 6.5, dy_after=5),
    RULE(0.9, inset=40, dy_after=4),
    T("The fine has already been incurred. Reading the French constitutes a "
      "second offence. This fine print, a third.", NARROW, 5.2, dy_after=5),
    T("MINISTRY OF SELF-REPORTING  ·  MINISTÈRE DE L'AUTODÉNONCIATION",
      NARROW, 5.5),
]

SIGNS = (("sign_airgap", AIRGAP),
         ("sign_clankers", CLANKERS),
         ("sign_bilingual", BILINGUAL))

# Deliberately not guarded by __name__ == "__main__" -- see note at OUT above.
# SIGNS_DRY=1 measures and reports the fit without building geometry (seconds, not
# minutes) -- use it when iterating on copy.
if os.environ.get("SIGNS_DRY"):
    for nm, ops in SIGNS:
        s, place, over = fit(ops)
        _, consumed = layout(ops, s)
        lines = [p for p in place if p[0] == "t"]
        smallest = min((p[3] for p in lines), default=0.0)
        zero = [p[1] for p in lines if width_at(p[1], p[2], p[3]) <= 0.01]
        widest = max((width_at(p[1], p[2], p[3]) for p in lines), default=0.0)
        print("DRY %-15s scale=%.3f h=%.1f/%.1f lines=%d min_cap=%.2fmm widest=%.1f "
              "OVERFLOW=%s empty=%d" % (nm, s, consumed, USABLE_H, len(lines),
                                        smallest, widest, over, len(zero)))
else:
    for nm, ops in SIGNS:
        build(nm, ops)
    print("DONE")
