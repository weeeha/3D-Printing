"""
Export the smallclock variants, assembled on the desk, as GLB for the 3D Models viewer.

    ~/ClaudeCode\\ Projects/cad-skill/.venv/bin/python export_glb.py OUT_DIR [puck pebble block]

Each GLB holds one mesh per part plus the display glass, in metres, Y up, face toward +Z,
the same frame as the viewer's existing smallclock.glb. It prints the ScreenSpec for
lib/models.ts so Realistic mode can put a SuperClock face on the glass.
"""
import json
import os
import sys

import numpy as np
import trimesh

import fitcheck as F

PETG = [228, 227, 223, 255]          # matches the viewer's existing smallclock.glb
GLASS = [4, 4, 4, 255]
EDGE = [18, 18, 19, 255]             # the module's frame behind the glass, matte
ACTIVE_R = 43.8                      # mm, Waveshare 3.4" active area radius


def to_glb_frame(points_mm):
    """Desk frame (mm, Z up, face toward +Y) -> GLB frame (m, Y up, face toward +Z)."""
    p = np.asarray(points_mm, float)
    return np.stack([-p[..., 0], p[..., 2], p[..., 1]], axis=-1) * 0.001


def export(model, out_dir):
    ns = F.enclosure(F.MODELS[model])
    tilt, lift = ns["DESK"]["tilt"], ns["DESK"]["lift"]
    to_desk = lambda wp: wp.rotate((0, 0, 0), (1, 0, 0), 90.0 + tilt).translate((0, 0, lift))
    parts = [(n, to_desk(p)) for n, p in ns["FIT_PARTS"]] + list(ns.get("FIT_WORLD_EXTRA", []))
    glass = [wp for name, col, wp in F.stack_body_frame(ns["lip_t"]) if col == "glass"]
    parts += [("glass", to_desk(g)) for g in glass]

    def add(m, name, color, roughness):
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=color, roughnessFactor=roughness, metallicFactor=0.0))
        scene.add_geometry(m, geom_name=name, node_name=name)

    rot = np.radians(90.0 + tilt)
    def body_to_desk(v, point=True):
        x, y, z = v
        w = np.array([x, y * np.cos(rot) - z * np.sin(rot), y * np.sin(rot) + z * np.cos(rot)])
        return w + (np.array([0, 0, lift]) if point else 0)
    normal = to_glb_frame(body_to_desk((0, 0, -1), point=False)) * 1000   # out of the glass

    scene = trimesh.Scene()
    for name, wp in parts:
        m = F.to_tm(wp)
        m.vertices = to_glb_frame(m.vertices)
        m.fix_normals()
        if name != "glass":
            add(m, name, PETG, 0.45)
            continue
        # the module is one solid: glossy only on the glass front, its edge is the matte black frame
        front = m.face_normals @ normal > 0.9
        add(m.submesh([np.where(front)[0]], append=True), name, GLASS, 0.1)
        if (~front).any():
            add(m.submesh([np.where(~front)[0]], append=True), f"{name}_edge", EDGE, 0.7)
    variant = f"-{os.environ.get('DOME', 'balanced')}" if model.startswith("dome") else ""
    path = os.path.join(out_dir, f"smallclock-{model.replace('_', '-')}{variant}.glb")
    scene.export(path)

    # screen: on the glass front (body z = lip_t), nudged 0.3 mm out
    center = to_glb_frame(body_to_desk((0, 0, ns["lip_t"] - 0.3)))
    up =to_glb_frame(body_to_desk((0, 1, 0), point=False)) * 1000
    spec = dict(center=[round(float(v), 6) for v in center], normal=[round(float(v), 5) for v in normal],
                up=[round(float(v), 5) for v in up], radius=ACTIVE_R / 1000)
    ext = scene.extents * 1000
    print(json.dumps(dict(model=model, file=os.path.basename(path), size_mm=[round(float(v), 1) for v in ext],
                          screen=spec)))
    return path


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for model in sys.argv[2:] or ["puck", "pebble", "block"]:
        export(model, out)
