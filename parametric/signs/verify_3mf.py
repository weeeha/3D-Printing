#!/usr/bin/env python3
"""End-to-end verification of the SHIPPED .3mf files, per object, in pure Python.

    python3 verify_3mf.py

Why not FreeCAD: re-meshing the .FCStd measures a mesh that was never exported (the
build merges per-solid meshes), and FreeCAD's 3MF *importer* collapses all objects into
one mesh -- which makes legitimately-coincident part boundaries look like
self-intersection. Both answer a question we didn't ask.

This reads the delivered file and checks each object on its own terms:
  * every undirected edge used exactly twice  -> closed surface, watertight
  * every directed edge used exactly once     -> consistently oriented, manifold
  * no degenerate (zero-area index) triangles
Coincident surfaces BETWEEN parts are expected and correct for multi-material, so
each object is judged alone -- never merged.
"""
import os
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ("csign_airgap", "csign_clankers", "csign_bilingual")


def local(tag):
    return tag.rsplit("}", 1)[-1]


def check_object(obj):
    tris, nverts = [], 0
    for child in obj.iter():
        t = local(child.tag)
        if t == "vertex":
            nverts += 1
        elif t == "triangle":
            tris.append((int(child.get("v1")), int(child.get("v2")),
                         int(child.get("v3"))))
    if not tris:
        return None

    degenerate = sum(1 for a, b, c in tris if a == b or b == c or a == c)
    directed = Counter()
    undirected = Counter()
    for a, b, c in tris:
        for e in ((a, b), (b, c), (c, a)):
            directed[e] += 1
            undirected[tuple(sorted(e))] += 1

    open_edges = sum(1 for v in undirected.values() if v != 2)
    bad_orient = sum(1 for v in directed.values() if v != 1)
    return {
        "verts": nverts, "tris": len(tris), "degenerate": degenerate,
        "open_edges": open_edges, "bad_orient": bad_orient,
        "ok": open_edges == 0 and bad_orient == 0 and degenerate == 0,
    }


allgood = True
for name in NAMES:
    path = os.path.join(HERE, name + ".3mf")
    if not os.path.exists(path):
        print("%-17s MISSING" % name)
        allgood = False
        continue
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("3D/3dmodel.model"))
    unit = root.get("unit")
    objs = [e for e in root.iter() if local(e.tag) == "object"]
    print("== %-17s objects=%d unit=%s" % (name, len(objs), unit))
    for i, o in enumerate(objs):
        r = check_object(o)
        if r is None:
            continue
        allgood = allgood and r["ok"]
        print("   object %d  verts=%-6d tris=%-6d openEdges=%-4d badOrient=%-4d "
              "degenerate=%-3d %s"
              % (i + 1, r["verts"], r["tris"], r["open_edges"], r["bad_orient"],
                 r["degenerate"], "WATERTIGHT" if r["ok"] else "<-- PROBLEM"))

print("VERDICT: %s" % ("every shipped object is closed, oriented and manifold"
                       if allgood else "PROBLEMS FOUND"))
sys.exit(0 if allgood else 1)
