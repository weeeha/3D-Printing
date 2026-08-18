# Emit an SVG preview per sign, traced from the REAL artwork geometry in the saved
# .FCStd -- not re-typeset in a browser. What you see is the inlay footprint that
# gets extruded, so preview and print cannot drift apart.
#
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd make_preview.py

import os
import FreeCAD as App

PLATE_W, PLATE_H, PLATE_T = 256.0, 200.0, 4.0
DEFL = 0.14   # preview only; coarser than the 0.06 used for the printed mesh
OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()


def wire_pts(w):
    try:
        return w.discretize(Deflection=DEFL)
    except Exception:
        pts = []
        for e in w.Edges:
            try:
                pts.extend(e.discretize(Deflection=DEFL))
            except Exception:
                pts.extend([e.Vertexes[0].Point, e.Vertexes[-1].Point])
        return pts


def face_path(f):
    """One SVG path, all contours as subpaths -> evenodd punches the counters."""
    subs = []
    for w in f.Wires:
        pts = wire_pts(w)
        if len(pts) < 3:
            continue
        d = "M %.3f %.3f " % (pts[0].x, PLATE_H - pts[0].y)
        d += " ".join("L %.3f %.3f" % (p.x, PLATE_H - p.y) for p in pts[1:])
        subs.append(d + " Z")
    return " ".join(subs)


def top_faces(shape):
    """Faces lying on the top plane, i.e. the visible artwork footprint."""
    out = []
    for f in shape.Faces:
        bb = f.BoundBox
        if abs(bb.ZMin - PLATE_T) < 1e-4 and abs(bb.ZLength) < 1e-4:
            out.append(f)
    return out


def emit(name, plate_col="#E8E4DA", art_col="#16181C"):
    doc = App.openDocument(os.path.join(OUT, name + ".FCStd"))
    art = doc.getObject("Artwork").Shape
    plate = doc.getObject("Plate").Shape

    faces = top_faces(art)
    paths = [face_path(f) for f in faces]
    paths = [p for p in paths if p]

    # plate silhouette (rounded corners + mounting holes) from its own top faces
    plate_paths = [face_path(f) for f in top_faces(plate)]
    plate_paths = [p for p in plate_paths if p]

    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
               'width="100%%" role="img" aria-label="%s preview">' % (PLATE_W, PLATE_H, name))
    svg.append('<defs><filter id="sh" x="-8%%" y="-8%%" width="120%%" height="120%%">'
               '<feDropShadow dx="0" dy="1.6" stdDeviation="1.8" flood-opacity="0.32"/>'
               '</filter></defs>')
    svg.append('<g filter="url(#sh)">')
    for p in plate_paths:
        svg.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (p, plate_col))
    svg.append('</g>')
    for p in paths:
        svg.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (p, art_col))
    svg.append('</svg>')

    dst = os.path.join(OUT, name + ".svg")
    with open(dst, "w") as fh:
        fh.write("\n".join(svg))
    print("PREVIEW %-16s faces=%d plate_faces=%d bytes=%d"
          % (name, len(paths), len(plate_paths), os.path.getsize(dst)))
    App.closeDocument(doc.Name)


for n in ("sign_airgap", "sign_clankers", "sign_bilingual"):
    emit(n)
print("PREVIEWS DONE")
