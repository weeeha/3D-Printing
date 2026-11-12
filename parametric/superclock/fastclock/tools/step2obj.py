"""FreeCAD headless: read a STEP file and write one OBJ with a named group per part (mm)."""
import os, time
import FreeCAD, Import

src, out = os.environ["STEP_SRC"], os.environ["OBJ_OUT"]
t0 = time.time()
doc = FreeCAD.newDocument("part")
Import.insert(src, doc.Name)
doc.recompute()
feats = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and not o.Shape.isNull()]
print("RESULT imported in %.0f s: %d objects, %d part features" % (time.time() - t0, len(doc.Objects), len(feats)))
types = {}
for o in doc.Objects:
    types[o.TypeId] = types.get(o.TypeId, 0) + 1
print("RESULT types", types)
base = 1
n_tri = 0
with open(out, "w") as fh:
    for o in feats:
        sh = o.Shape.copy()
        sh.Placement = o.getGlobalPlacement()
        try:
            verts, faces = sh.tessellate(0.08)
        except Exception as exc:
            print("RESULT skip", o.Label, exc)
            continue
        if not faces:
            continue
        bb = sh.BoundBox
        name = "%s__%s" % (o.Label.replace(" ", "_"), o.Name)
        fh.write("o %s\n" % name)
        for v in verts:
            fh.write("v %.4f %.4f %.4f\n" % (v.x, v.y, v.z))
        for a, b, c in faces:
            fh.write("f %d %d %d\n" % (a + base, b + base, c + base))
        base += len(verts)
        n_tri += len(faces)
        print("RESULT part %s size %.1f x %.1f x %.1f at %.1f %.1f %.1f tris %d" % (name, bb.XLength, bb.YLength, bb.ZLength, bb.Center.x, bb.Center.y, bb.Center.z, len(faces)))
print("RESULT wrote %s, %d triangles, %.0f s" % (out, n_tri, time.time() - t0))
