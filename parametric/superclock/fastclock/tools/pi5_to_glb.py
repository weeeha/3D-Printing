"""Blender headless: turn the 2,711-part Pi 5 OBJ into a light, coloured GLB (units stay in mm).

The STEP has no colours or part names, so parts are coloured by shape and position:
board green, tall shells at the port end and other large cans metal, flat packages black,
the GPIO header black with gold pins, everything else a neutral solder-grey.
"""
import bpy, sys, numpy as np
from mathutils import Vector

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=src, forward_axis="Y", up_axis="Z")
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
print("RESULT imported", len(objs), "objects")


def mat(name, col, rough, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*col, 1)
    return m


MATS = {
    "board": mat("Pi5 board", (0.015, 0.20, 0.08), 0.45),
    "metal": mat("Pi5 metal", (0.72, 0.72, 0.70), 0.32, 1.0),
    "chip": mat("Pi5 chip", (0.025, 0.025, 0.028), 0.4),
    "plastic": mat("Pi5 black plastic", (0.02, 0.02, 0.022), 0.5),
    "gold": mat("Pi5 gold", (0.85, 0.62, 0.20), 0.3, 1.0),
    "blue": mat("Pi5 USB3 blue", (0.02, 0.12, 0.55), 0.45),
    "small": mat("Pi5 small parts", (0.42, 0.40, 0.36), 0.5),
}
groups = {k: [] for k in MATS}
for o in objs:
    c = np.array([list(o.matrix_world @ Vector(b)) for b in o.bound_box])
    lo, hi = c.min(0), c.max(0)
    sx, sy, sz = hi - lo
    cx, cy, cz = (lo + hi) / 2
    if sx > 80 and sy > 50 and sz < 2:
        k = "board"
    elif cy > 49 and 6 < cx < 59 and cz > 1.3:                 # the 40-pin header strip
        k = "gold" if (sx < 1.2 and sy < 1.2) else "plastic"
    elif cx > 66 and sz > 9:                                   # USB and Ethernet at the port end
        k = "metal" if min(sx, sy) > 12 else ("blue" if (cy < 20 and sz < 3 and sx > 5) else "plastic")
    elif sz < 2.6 and sx > 3.5 and sy > 3.5 and cz > 1.3:      # flat packages on top
        k = "chip" if max(sx, sy) < 16 else "metal"
    elif max(sx, sy, sz) > 6 and sz > 2.5:                     # other connectors and cans
        k = "metal"
    else:
        k = "small"
    groups[k].append(o)
print("RESULT groups", {k: len(v) for k, v in groups.items()})

RATIO = {"board": 1.0, "metal": 0.10, "chip": 0.3, "plastic": 0.08, "gold": 0.06, "blue": 0.2, "small": 0.05}
keep = []
for k, members in groups.items():
    if not members:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    for o in members:
        o.select_set(True)
    bpy.context.view_layer.objects.active = members[0]
    bpy.ops.object.join()
    j = bpy.context.view_layer.objects.active
    j.name = "Pi5 " + k
    before = len(j.data.polygons)
    if RATIO[k] < 1.0:
        d = j.modifiers.new("dec", "DECIMATE")
        d.ratio = RATIO[k]
        new = bpy.data.meshes.new_from_object(j.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        j.modifiers.clear()
        j.data = new
    j.data.materials.clear()
    j.data.materials.append(MATS[k])
    for p in j.data.polygons:
        p.use_smooth = False
    print("RESULT %s: %d -> %d faces" % (k, before, len(j.data.polygons)))
    keep.append(j)
bpy.ops.object.select_all(action="DESELECT")
for o in keep:
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True)
print("RESULT wrote", out)
