"""Fastclock product render: the fixed (flat-base) shell + the real 5-inch round display.

Run headless:
  Blender -b --python product_render.py -- <preview|final> <view[,view...]> <screen.png> <out_dir> [white|black] [key=value ...]

Options (key=value):
  ports=covered|open   the window on the right side is the Raspberry Pi port opening; "covered"
                       closes it with a flush door set back 0.4 mm
  grille=on|off|sunflower|dial|waves|slots|burst
                       speaker grille cut into the back ("on" is the sunflower pattern)
  cable=on|off         arched cable exit at the bottom back, with a cable
  internals=on|off     stand-in electronics inside (on by default for the frosted body)
  buttons=on|off       four keycap buttons along the top: orange, wide white, two black
  bg=light|dark        backdrop colour
  frost=0.38           roughness of the frosted body (lower is clearer)
Body colours: white, black, frosted.
  export=path.stl      write the modified shell (grille + cable exit) for printing

Sources
  body     clock_body_fixed.stl   (the flat-base shell, exported in metres, March 2026)
  display  built here to the vendor CAD's outline (5inch-1080x1080-lcd-sku243692):
           a 150 mm disc, 7.8 mm thick, with a 127 mm round active area.
The display caps the shell: the shell's rim is 149.6 mm across, the glass is 150 mm.
Nothing here has been test-fitted against the real hardware. The grille and cable exit are
drawn for the render; their positions are not checked against the speaker or the Pi's sockets.
"""
import bpy, bmesh, glob, math, os, sys
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
pos = [a for a in argv if "=" not in a]
opt = dict(a.split("=", 1) for a in argv if "=" in a)
MODE = pos[0] if len(pos) > 0 else "preview"
VIEWS = (pos[1] if len(pos) > 1 else "hero").split(",")
SCREEN = pos[2] if len(pos) > 2 else ""
OUT = pos[3] if len(pos) > 3 else os.path.join(HERE, "renders", "product")
BODY = pos[4] if len(pos) > 4 else "white"
PORTS = opt.get("ports", "covered")
GRILLE = opt.get("grille", "on")
CABLE = opt.get("cable", "on")
BODY_STL = os.path.join(HERE, "clock_body_fixed.stl")

GLASS_R = 0.075        # vendor CAD: 150 mm disc
GLASS_T = 0.0078       # vendor CAD: front face to the back of the panel
ACTIVE_R = 0.0635      # 127 mm active area (CLOCK_SPECS.txt)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene


def link(obj):
    scn.collection.objects.link(obj)
    return obj


# ---------------------------------------------------------------- body
bpy.ops.wm.stl_import(filepath=BODY_STL)
body = bpy.context.selected_objects[0]
body.name = "Body"
bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
zmin = min(v.co.z for v in bm.verts)
bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, -zmin))   # base on the ground
bm.to_mesh(body.data)
bm.free()
vs = np.array([list(v.co) for v in body.data.vertices])

# rim plane: the direction near (0, -0.76, 0.65) with the most vertices on its far plane
best = None
for el in np.arange(30, 55.01, 0.25):
    e = math.radians(el)
    n = np.array([0.0, -math.cos(e), math.sin(e)])
    p = vs @ n
    c = int((p > p.max() - 0.00015).sum())
    if best is None or c > best[0]:
        best = (c, n, el)
_, n, el = best
p = vs @ n
rim = vs[p > p.max() - 0.0004]
u_ax = np.array([1.0, 0.0, 0.0])
v_ax = np.cross(n, u_ax)                      # up along the screen
pts = np.c_[rim @ u_ax, rim @ v_ax]


def hull(points):
    points = sorted(map(tuple, points))
    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (q[1] - out[-2][1]) - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(q)
        return out[:-1]
    return np.array(half(points) + half(reversed(points)))


h = hull(pts)
A = np.c_[2 * h, np.ones(len(h))]
sol = np.linalg.lstsq(A, (h ** 2).sum(1), rcond=None)[0]
c2 = sol[:2]
rim_r = math.sqrt(sol[2] + c2 @ c2)
rim_c = u_ax * c2[0] + v_ax * c2[1] + n * p.max()
print("RESULT rim elev %.2f deg, centre mm %s, outer radius %.2f mm" % (el, (rim_c * 1000).round(1), rim_r * 1000))

body_mat = bpy.data.materials.new("Body plastic")
body_mat.use_nodes = True
b = body_mat.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.80, 0.79, 0.76, 1)
b.inputs["Roughness"].default_value = 0.46
b.inputs["Subsurface Weight"].default_value = 0.12
b.inputs["Subsurface Radius"].default_value = (0.004, 0.003, 0.002)
b.inputs["Subsurface Scale"].default_value = 0.5
if BODY == "black":
    # matte black plastic, a touch lighter than the glass so the two still read as separate parts
    b.inputs["Base Color"].default_value = (0.022, 0.022, 0.024, 1)
    b.inputs["Roughness"].default_value = 0.74        # matte
    b.inputs["Subsurface Weight"].default_value = 0.0
if BODY == "frosted":
    # frosted clear plastic: the wall is a real 3 mm solid, so rough refraction does the blurring
    b.inputs["Base Color"].default_value = (0.93, 0.95, 0.96, 1)
    b.inputs["Roughness"].default_value = float(opt.get("frost", 0.38))
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["IOR"].default_value = 1.49
    b.inputs["Subsurface Weight"].default_value = 0.0
    fnt = body_mat.node_tree
    mix = fnt.nodes.new("ShaderNodeMixShader")
    clear = fnt.nodes.new("ShaderNodeBsdfTransparent")
    clear.inputs["Color"].default_value = (0.9, 0.92, 0.93, 1)
    lp = fnt.nodes.new("ShaderNodeLightPath")
    amt = fnt.nodes.new("ShaderNodeMath"); amt.operation = "MULTIPLY"; amt.inputs[1].default_value = 0.9
    fnt.links.new(lp.outputs["Is Shadow Ray"], amt.inputs[0])       # let light reach the parts inside
    fnt.links.new(amt.outputs["Value"], mix.inputs["Fac"])
    fnt.links.new(b.outputs["BSDF"], mix.inputs[1])
    fnt.links.new(clear.outputs["BSDF"], mix.inputs[2])
    fnt.links.new(mix.outputs["Shader"], fnt.nodes["Material Output"].inputs["Surface"])

# ---------------------------------------------------------------- surface probing
bvh = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
STEP = 0.0005


def height_map(axis):
    """First hit of parallel rays shot at the shell from +X (axis 0) or +Y (axis 1)."""
    a_vals = np.arange(vs[:, 1 - axis].min(), vs[:, 1 - axis].max(), STEP)
    z_vals = np.arange(0.004, vs[:, 2].max(), STEP)
    H = np.full((len(a_vals), len(z_vals)), np.nan)
    d = Vector((-1, 0, 0)) if axis == 0 else Vector((0, -1, 0))
    for i, a in enumerate(a_vals):
        for j, z in enumerate(z_vals):
            o = Vector((0.3, a, z)) if axis == 0 else Vector((a, 0.3, z))
            hit = bvh.ray_cast(o, d)
            if hit[0] is not None:
                H[i, j] = hit[0][axis]
    return a_vals, z_vals, H


def holes_in(H, floor):
    """Cells with no near surface that are enclosed by surface on all four sides."""
    surf = np.nan_to_num(H, nan=-1.0) > floor
    L = np.maximum.accumulate(surf, axis=0)
    Rr = np.maximum.accumulate(surf[::-1], axis=0)[::-1]
    D = np.maximum.accumulate(surf, axis=1)
    U = np.maximum.accumulate(surf[:, ::-1], axis=1)[:, ::-1]
    hole = L & Rr & D & U & ~surf
    comps, seen = [], np.zeros_like(hole)
    for i0, j0 in zip(*np.nonzero(hole)):
        if seen[i0, j0]:
            continue
        stack, cells = [(i0, j0)], []
        seen[i0, j0] = True
        while stack:
            i, j = stack.pop()
            cells.append((i, j))
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a2, b2 = i + di, j + dj
                if 0 <= a2 < hole.shape[0] and 0 <= b2 < hole.shape[1] and hole[a2, b2] and not seen[a2, b2]:
                    seen[a2, b2] = True
                    stack.append((a2, b2))
        comps.append(np.array(cells))
    comps.sort(key=len, reverse=True)
    return surf, hole, comps


def dilate(mask, k):
    out = mask.copy()
    for di in range(-k, k + 1):
        for dj in range(-k, k + 1):
            out |= np.roll(np.roll(mask, di, 0), dj, 1)
    return out


TERMS = [(i, j) for i in range(5) for j in range(5 - i)]


def basis(a, z):
    return np.stack([a ** i * z ** j for i, j in TERMS], axis=-1)


# ---------------------------------------------------------------- port cover
port_win = None
if PORTS == "covered":
    ys, zs, H = height_map(0)
    surf, hole, comps = holes_in(H, 0.04)
    win = comps[0]
    wy, wz = ys[win[:, 0]], zs[win[:, 1]]
    print("RESULT side holes (cells of 0.25 mm2):", [len(c) for c in comps[:5]],
          "window centre y %.1f z %.1f mm, span %.1f x %.1f mm" % (wy.mean() * 1000, wz.mean() * 1000, np.ptp(wy) * 1000, np.ptp(wz) * 1000))
    yc, zc, sc = wy.mean(), wz.mean(), 0.05
    YY, ZZ = np.meshgrid(ys, zs, indexing="ij")
    ring = surf & ~dilate(hole, 4) & (np.abs(YY - yc) < np.ptp(wy) / 2 + 0.012) & (np.abs(ZZ - zc) < np.ptp(wz) / 2 + 0.012)
    Bm = basis((YY[ring] - yc) / sc, (ZZ[ring] - zc) / sc)
    coef = np.linalg.lstsq(Bm, H[ring], rcond=None)[0]
    print("RESULT port cover surface fit p95 %.3f mm over %d cells" % (np.percentile(np.abs(Bm @ coef - H[ring]), 95) * 1000, ring.sum()))
    port_win = Vector((float(basis(np.float64(0.0), np.float64(0.0)) @ coef), float(yc), float(zc)))   # outer surface at the window centre
    st = np.c_[wy - yc, wz - zc]
    _, _, pv = np.linalg.svd(st - st.mean(0))
    st2 = st @ pv.T
    lo, hi = st2.min(0) - 0.0012, st2.max(0) + 0.0012
    cm = bpy.data.meshes.new("Port cover")
    cb = bmesh.new()
    NU, NV = 64, 32
    grid = []
    for i in range(NU + 1):
        row = []
        for j in range(NV + 1):
            q = np.array([lo[0] + (hi[0] - lo[0]) * i / NU, lo[1] + (hi[1] - lo[1]) * j / NV]) @ pv
            x = float(basis(q[0] / sc, q[1] / sc) @ coef) - 0.0004
            row.append(cb.verts.new((x, yc + q[0], zc + q[1])))
        grid.append(row)
    for i in range(NU):
        for j in range(NV):
            f = cb.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
            f.smooth = True
    cb.normal_update()
    if sum(f.normal.x for f in cb.faces) < 0:
        bmesh.ops.reverse_faces(cb, faces=cb.faces)
    cb.to_mesh(cm)
    cb.free()
    door_mat = body_mat
    if BODY == "frosted":
        # a clear window in the frosted shell, so the ports read even though they sit well behind it
        door_mat = body_mat.copy()
        door_mat.name = "Port door clear"
        door_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = float(opt.get("door_frost", 0.07))
    cm.materials.append(door_mat)
    link(bpy.data.objects.new("Port cover", cm))

# ---------------------------------------------------------------- grille + cable exit
cutter = bmesh.new()
cable_y = None
STYLE = "sunflower" if GRILLE == "on" else GRILLE
if STYLE != "off":
    ge = math.radians(float(opt.get("grille_elev", 24)))
    dg = Vector((0, math.cos(ge), math.sin(ge)))               # the grille faces back and a little up
    gu = Vector((1, 0, 0))
    gv = dg.cross(gu)
    inside = Vector(rim_c) - Vector(n) * 0.03 + Vector((0, 0, float(opt.get("grille_dz", 0))))   # a point in the cavity on the vent's axis
    if "grille_o" in opt:                                      # a point on the vent's axis, "x,y,z" in metres
        inside = Vector([float(v_) for v_ in opt["grille_o"].split(",")])
    GR = float(opt.get("grille_r", 0.023))
    GOLD = math.radians(137.508)

    def prism(outline):
        """Cut one opening: a polygon in the grille plane, pushed through the wall along the grille axis."""
        probes = outline[::max(1, len(outline) // 10)] + [tuple(np.mean(outline, axis=0))]
        depths = []
        for u, v in probes:
            hit = bvh.ray_cast(inside + gu * u + gv * v + dg * 0.3, -dg)
            if hit[0] is None:
                return 0
            depths.append((hit[0] - inside).dot(dg))
        t0, t1 = min(depths) - 0.006, max(depths) + 0.004
        lo_ring = [cutter.verts.new(inside + gu * u + gv * v + dg * t0) for u, v in outline]
        hi_ring = [cutter.verts.new(inside + gu * u + gv * v + dg * t1) for u, v in outline]
        cutter.faces.new(lo_ring)
        cutter.faces.new(hi_ring)
        for i in range(len(outline)):
            j = (i + 1) % len(outline)
            cutter.faces.new((lo_ring[i], lo_ring[j], hi_ring[j], hi_ring[i]))
        return 1

    def dot(u, v, r, seg=16):
        return prism([(u + r * math.cos(2 * math.pi * i / seg), v + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)])

    def capsule(a, b_, r, seg=8):
        ang = math.atan2(b_[1] - a[1], b_[0] - a[0])
        pts = [(b_[0] + r * math.cos(ang - math.pi / 2 + math.pi * i / seg), b_[1] + r * math.sin(ang - math.pi / 2 + math.pi * i / seg)) for i in range(seg + 1)]
        pts += [(a[0] + r * math.cos(ang + math.pi / 2 + math.pi * i / seg), a[1] + r * math.sin(ang + math.pi / 2 + math.pi * i / seg)) for i in range(seg + 1)]
        return prism(pts)

    def arc(rad, th0, th1, width, seg=6):
        steps = max(6, int((th1 - th0) * rad / 0.0012))
        ro, ri = rad + width / 2, rad - width / 2
        pts = [(ro * math.cos(th0 + (th1 - th0) * i / steps), ro * math.sin(th0 + (th1 - th0) * i / steps)) for i in range(steps + 1)]
        ce = (rad * math.cos(th1), rad * math.sin(th1))
        pts += [(ce[0] + width / 2 * math.cos(th1 + math.pi * i / seg), ce[1] + width / 2 * math.sin(th1 + math.pi * i / seg)) for i in range(1, seg)]
        pts += [(ri * math.cos(th1 - (th1 - th0) * i / steps), ri * math.sin(th1 - (th1 - th0) * i / steps)) for i in range(steps + 1)]
        cs = (rad * math.cos(th0), rad * math.sin(th0))
        pts += [(cs[0] + width / 2 * math.cos(th0 + math.pi + math.pi * i / seg), cs[1] + width / 2 * math.sin(th0 + math.pi + math.pi * i / seg)) for i in range(1, seg)]
        return prism(pts)

    count = 0
    if STYLE == "sunflower":          # dots on a sunflower spiral, shrinking outward
        cgap = 0.0019
        for k in range(1, int((GR / cgap) ** 2) + 1):
            r = cgap * math.sqrt(k)
            count += dot(r * math.cos(k * GOLD), r * math.sin(k * GOLD), 0.00105 - 0.00055 * (r / GR))
    elif STYLE == "dial":             # a clock dial: 60 minute ticks, every fifth one long, and 12 hour dots
        for k in range(60):
            th = math.pi / 2 - k * math.pi / 30
            r0, wid = (0.0125, 0.0008) if k % 5 == 0 else (0.0175, 0.00055)
            count += capsule((r0 * math.cos(th), r0 * math.sin(th)), (0.0222 * math.cos(th), 0.0222 * math.sin(th)), wid)
        for k in range(12):
            th = math.pi / 2 - k * math.pi / 6
            count += dot(0.0075 * math.cos(th), 0.0075 * math.sin(th), 0.0009)
        count += dot(0, 0, 0.0016)
    elif STYLE == "waves":            # broken concentric rings, each turned against the last
        count += dot(0, 0, 0.0017)
        for i, rad in enumerate((0.0055, 0.0097, 0.0139, 0.0181, 0.0223)):
            for s in range(3):
                th0 = s * 2 * math.pi / 3 + i * math.pi / 3 + math.radians(10)
                count += arc(rad, th0, th0 + 2 * math.pi / 3 - math.radians(20), 0.0016)
    elif STYLE == "slots":            # level slots clipped to a circle
        pitch = 0.0034
        for k in range(-6, 7):
            v = k * pitch
            half = math.sqrt(max(0.0, 0.0225 ** 2 - v ** 2)) - 0.0008
            if half > 0.002:
                count += capsule((-half, v), (half, v), 0.00075)
    elif STYLE == "burst":            # dashes on the sunflower spiral, pointing outward and growing longer
        cgap = 0.0024
        for k in range(2, int((GR / cgap) ** 2) + 1):
            r = cgap * math.sqrt(k)
            th = k * GOLD
            half = 0.0003 + 0.0012 * (r / GR)
            count += capsule(((r - half) * math.cos(th), (r - half) * math.sin(th)), ((r + half) * math.cos(th), (r + half) * math.sin(th)), 0.0005)
        count += dot(0, 0, 0.0011)
    else:
        raise SystemExit("unknown grille style " + STYLE)
    bmesh.ops.recalc_face_normals(cutter, faces=cutter.faces)
    print("RESULT grille %s: %d openings" % (STYLE, count))
if CABLE == "on":
    hit = bvh.ray_cast(Vector((0, 0.3, 0.005)), Vector((0, -1, 0)))
    cable_y = hit[0].y
    prof = [(-0.0065, -0.001), (0.0065, -0.001)]
    for i in range(0, 17):
        a = math.pi * i / 16
        prof.append((0.0065 * math.cos(a), 0.0035 + 0.0065 * math.sin(a)))
    front = [cutter.verts.new((x, cable_y - 0.009, z)) for x, z in prof]
    back = [cutter.verts.new((x, cable_y + 0.006, z)) for x, z in prof]
    arch = [cutter.faces.new(front), cutter.faces.new(back)]
    for i in range(len(prof)):
        j = (i + 1) % len(prof)
        arch.append(cutter.faces.new((front[i], front[j], back[j], back[i])))
    bmesh.ops.recalc_face_normals(cutter, faces=arch)
    print("RESULT cable exit at y %.1f mm, 13 mm wide, 10 mm tall" % (cable_y * 1000))
if cutter.faces:
    cmesh = bpy.data.meshes.new("Cutters")
    cutter.to_mesh(cmesh)
    cobj = link(bpy.data.objects.new("Cutters", cmesh))
    before = len(body.data.polygons)
    mod = body.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cobj
    for solver in ("MANIFOLD", "EXACT"):
        try:
            mod.solver = solver
            break
        except TypeError:
            pass
    cut_mesh = bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    body.modifiers.remove(mod)
    body.data = cut_mesh
    bpy.data.objects.remove(cobj)
    print("RESULT boolean (%s): faces %d -> %d" % (solver, before, len(body.data.polygons)))
cutter.free()

# shading: smooth, with hard edges kept hard
bm = bmesh.new()
bm.from_mesh(body.data)
sharp = math.radians(32)
for e in bm.edges:
    e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0) > sharp)
for f in bm.faces:
    f.smooth = True
bm.to_mesh(body.data)
bm.free()
body.data.materials.clear()
body.data.materials.append(body_mat)
if "export" in opt:
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.ops.wm.stl_export(filepath=opt["export"], export_selected_objects=True, global_scale=1000)
    print("RESULT exported", opt["export"])

# ---------------------------------------------------------------- cable
if CABLE == "on":
    cu = bpy.data.curves.new("Cable", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.0018
    cu.bevel_resolution = 6
    sp = cu.splines.new("BEZIER")
    path = [(0, cable_y - 0.012, 0.0045), (0, cable_y + 0.03, 0.0019), (0.035, cable_y + 0.085, 0.0018), (0.16, cable_y + 0.10, 0.0018), (0.9, cable_y + 0.07, 0.0018)]
    sp.bezier_points.add(len(path) - 1)
    for bp, co in zip(sp.bezier_points, path):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    cable = link(bpy.data.objects.new("Cable", cu))
    cab_mat = bpy.data.materials.new("Cable")
    cab_mat.use_nodes = True
    cbsdf = cab_mat.node_tree.nodes["Principled BSDF"]
    cbsdf.inputs["Base Color"].default_value = (0.03, 0.03, 0.032, 1) if BODY == "black" else (0.78, 0.78, 0.76, 1)
    cbsdf.inputs["Roughness"].default_value = 0.5
    cu.materials.append(cab_mat)

# ---------------------------------------------------------------- display
N = Vector(n)
X = Vector((1, 0, 0))
Y = Vector(v_ax)
centre = Vector(rim_c) + N * (GLASS_T / 2 + 0.0001)
bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=GLASS_R, depth=GLASS_T, end_fill_type="NGON")
disp = bpy.context.object
disp.name = "Display"
rot = Matrix((X, Y, N)).transposed().to_4x4()
disp.matrix_world = Matrix.Translation(centre) @ rot
for f in disp.data.polygons:
    f.use_smooth = True
uv = disp.data.uv_layers.new(name="screen")
for loop in disp.data.loops:
    co = disp.data.vertices[loop.vertex_index].co
    uv.data[loop.index].uv = (co.x / (2 * ACTIVE_R) + 0.5, co.y / (2 * ACTIVE_R) + 0.5)
bev = disp.modifiers.new("Bevel", "BEVEL")
bev.width = 0.0009
bev.segments = 4
bev.limit_method = "ANGLE"
bev.angle_limit = math.radians(40)
bev.harden_normals = True

glass = bpy.data.materials.new("Display glass")
glass.use_nodes = True
nt = glass.node_tree
g = nt.nodes["Principled BSDF"]
g.inputs["Base Color"].default_value = (0.004, 0.004, 0.005, 1)
g.inputs["Roughness"].default_value = 0.035
g.inputs["IOR"].default_value = 1.5
g.inputs["Coat Weight"].default_value = 1.0
g.inputs["Coat Roughness"].default_value = 0.02
if SCREEN:
    img = bpy.data.images.load(SCREEN)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "CLIP"
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = "screen"
    nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
    # round mask for the 127 mm active area, front face only
    sub = nt.nodes.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (0.5, 0.5, 0)
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.5
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    front = nt.nodes.new("ShaderNodeMath"); front.operation = "GREATER_THAN"; front.inputs[1].default_value = GLASS_T / 2 - 0.0002
    both = nt.nodes.new("ShaderNodeMath"); both.operation = "MULTIPLY"
    nt.links.new(uvn.outputs["UV"], sub.inputs[0])
    nt.links.new(sub.outputs["Vector"], ln.inputs[0])
    nt.links.new(ln.outputs["Value"], lt.inputs[0])
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], front.inputs[0])
    nt.links.new(lt.outputs["Value"], both.inputs[0])
    nt.links.new(front.outputs["Value"], both.inputs[1])
    # lit panel: the image plus a faint backlight floor, so black pixels are not pure black
    floor = nt.nodes.new("ShaderNodeMixRGB"); floor.blend_type = "ADD"; floor.inputs["Fac"].default_value = 1.0
    floor.inputs["Color2"].default_value = (0.004, 0.004, 0.005, 1)
    nt.links.new(tex.outputs["Color"], floor.inputs["Color1"])
    nt.links.new(floor.outputs["Color"], g.inputs["Emission Color"])
    strength = nt.nodes.new("ShaderNodeMath"); strength.operation = "MULTIPLY"; strength.inputs[1].default_value = 1.0
    nt.links.new(both.outputs["Value"], strength.inputs[0])
    nt.links.new(strength.outputs["Value"], g.inputs["Emission Strength"])
disp.data.materials.append(glass)
# the edge and back of the disc are the black frame of the panel, not glass
frame = bpy.data.materials.new("Display frame")
frame.use_nodes = True
fr = frame.node_tree.nodes["Principled BSDF"]
fr.inputs["Base Color"].default_value = (0.012, 0.012, 0.013, 1)
fr.inputs["Roughness"].default_value = 0.38
disp.data.materials.append(frame)
for f in disp.data.polygons:
    f.material_index = 0 if f.normal.z > 0.5 else 1

# ---------------------------------------------------------------- parts inside (stand-ins)
# Shown through the frosted shell. The display's driver board is the vendor CAD; the computer is
# the Raspberry Pi 4 model from the component folder standing in for the Pi 5 (same 85 x 56 mm
# board). The Fusion HAT, battery and speaker are not modelled, and positions are not measured.
PARTS = os.path.expanduser("~/Product Design/SuperClock")
if opt.get("internals", "on" if BODY == "frosted" else "off") == "on":
    bpy.ops.wm.stl_import(filepath=os.path.join(PARTS, "Component CAD models", "5inch-1080x1080-lcd-sku243692.stl"))
    drv = bpy.context.selected_objects[0]
    drv.name = "Display driver board"
    dbm = bmesh.new()
    dbm.from_mesh(drv.data)
    bmesh.ops.delete(dbm, geom=[v for v in dbm.verts if v.co.y < 7.7], context="VERTS")   # keep what sits behind the panel
    for f in dbm.faces:
        f.smooth = False
    dbm.to_mesh(drv.data)
    dbm.free()
    drv.matrix_world = Matrix.Translation(centre + N * (GLASS_T / 2)) @ Matrix((X, -N, Y)).transposed().to_4x4() @ Matrix.Scale(0.001, 4)
    pcb = bpy.data.materials.new("PCB")
    pcb.use_nodes = True
    pb = pcb.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = (0.01, 0.10, 0.045, 1)
    pb.inputs["Roughness"].default_value = 0.45
    drv.data.materials.append(pcb)

    # the Fast runs a Pi 5: use the official model (converted from Raspberry Pi's STEP, coloured by
    # part type because the STEP carries no colours) when it is there, else the Pi 4 stand-in
    pi5_glb = os.path.join(PARTS, "Component CAD models", "CAD RaspberryPi5", "rpi-5b.glb")
    pi_model = pi5_glb if os.path.exists(pi5_glb) and opt.get("pi_model", "5") == "5" else os.path.join(PARTS, "Raspberry Pi 4 Model B.glb")
    print("RESULT Pi model:", os.path.basename(pi_model))
    bpy.ops.import_scene.gltf(filepath=pi_model)
    pi_objs = [o for o in bpy.context.selected_objects]
    bpy.context.view_layer.update()
    corners = np.array([list(o.matrix_world @ Vector(c)) for o in pi_objs if o.type == "MESH" for c in o.bound_box])
    lo3, hi3 = corners.min(0), corners.max(0)
    dims = hi3 - lo3
    unit = 0.001 if dims.max() > 1 else 1.0
    order = np.argsort(dims)                      # thin, mid, long
    # find the end with the USB and Ethernet stacks (the tall end) and the side the parts stand on
    allv = np.concatenate([np.array([list(o.matrix_world @ v.co) for v in o.data.vertices]) for o in pi_objs if o.type == "MESH"])
    lng, thn = allv[:, order[2]], allv[:, order[0]]
    edge = 0.12 * dims[order[2]]
    hi_end = np.ptp(thn[lng > hi3[order[2]] - edge]) > np.ptp(thn[lng < lo3[order[2]] + edge])
    end_t = thn[lng > hi3[order[2]] - edge] if hi_end else thn[lng < lo3[order[2]] + edge]
    parts_up = end_t.mean() > np.median(thn)
    cols = [None, None, None]
    cols[order[2]] = X if hi_end else -X          # port end points at the port door (+X)
    cols[order[0]] = -N if parts_up else N        # parts face the back of the clock
    cols[order[1]] = Y
    Rm = Matrix(cols).transposed()
    if Rm.determinant() < 0:
        cols[order[1]] = -Y
        Rm = Matrix(cols).transposed()
    if port_win is not None:
        # level with the port window. pi=door pushes the port end up to the door (the battery board
        # then no longer fits); the default keeps the stack centred behind the display.
        rel = port_win - Vector(rim_c)
        shift = (rel.dot(X) - 0.0065 - dims[order[2]] * unit / 2) if opt.get("pi") == "door" else 0.0
        pi_c = Vector(rim_c) + Y * rel.dot(Y) + N * rel.dot(N) + X * shift
    else:
        pi_c = Vector(rim_c) - N * 0.0227
    T = Matrix.Translation(pi_c) @ Rm.to_4x4() @ Matrix.Scale(unit, 4) @ Matrix.Translation(-Vector((lo3 + hi3) / 2))
    for o in pi_objs:
        if o.parent is None:
            o.matrix_world = T @ o.matrix_world
    print("RESULT internals: display driver board + Pi, Pi size mm", (dims * unit * 1000).round(1))

    # the battery board (UPS HAT) and the speaker from the component CAD folder
    def place_stl(fname, name, cols_, centre_pt, material):
        bpy.ops.wm.stl_import(filepath=os.path.join(PARTS, "Component CAD models", fname))
        ob = bpy.context.selected_objects[0]
        ob.name = name
        vv = np.array([list(x_.co) for x_ in ob.data.vertices])
        mid_ = (vv.min(0) + vv.max(0)) / 2
        ob.matrix_world = Matrix.Translation(centre_pt) @ Matrix(cols_).transposed().to_4x4() @ Matrix.Scale(0.001, 4) @ Matrix.Translation(-Vector(mid_))
        ob.data.materials.append(material)
        return ob

    def flat(name, col, rough=0.5, metal=0.0):
        m_ = bpy.data.materials.new(name)
        m_.use_nodes = True
        pp = m_.node_tree.nodes["Principled BSDF"]
        pp.inputs["Base Color"].default_value = (*col, 1)
        pp.inputs["Roughness"].default_value = rough
        pp.inputs["Metallic"].default_value = metal
        return m_

    cav = Vector(rim_c) - N * 0.03
    pi_half = (dims[order[2]] * unit / 2 + 0.001, dims[order[1]] * unit / 2 + 0.001, dims[order[0]] * unit / 2 + 0.001)

    def outside(q_):
        """True when a point is past the inner face of the shell (or in front of the rim)."""
        dq = q_ - cav
        if dq.length < 1e-6:
            return False
        sh_ = bvh.ray_cast(cav + dq.normalized() * 0.3, -dq.normalized())
        if sh_[0] is None:
            return (q_ - Vector(rim_c)).dot(N) > 0
        return dq.length > (sh_[0] - cav).length - 0.003

    def in_pi(q_):
        dq = q_ - pi_c
        return abs(dq.dot(X)) < pi_half[0] and abs(dq.dot(Y)) < pi_half[1] and abs(dq.dot(N)) < pi_half[2]

    # battery board: flat on the floor of the shell. Try both headings and every position front to
    # back, and keep the one with the fewest points outside the shell or inside the Pi.
    hat = place_stl("Raspberry Pi UPS HAT.stl", "Battery board (UPS HAT)", (Vector((0, -1, 0)), X, Vector((0, 0, 1))), Vector((0, 0, 0.0166)), flat("Battery board", (0.015, 0.06, 0.30)))
    hv_ = np.array([list(x_.co) for x_ in hat.data.vertices])
    hv_ = (hv_ - (hv_.min(0) + hv_.max(0)) / 2)[:: max(1, len(hv_) // 350)] * 0.001
    Zw, Yw = Vector((0, 0, 1)), Vector((0, 1, 0))
    HEADINGS = [("long side across", (-Yw, X, Zw)), ("long side across, turned around", (Yw, -X, Zw)),
                ("long side front to back", (X, Yw, Zw)), ("long side front to back, turned around", (-X, -Yw, Zw))]
    trials = []
    for hi_, (heading, cols_h) in enumerate(HEADINGS):
        if "battery_h" in opt and int(opt["battery_h"]) != hi_:
            continue
        Rn = np.array(Matrix(cols_h).transposed())
        for yy in ([float(opt["battery_y"])] if "battery_y" in opt else np.arange(-0.045, 0.0451, 0.0015)):
            cpt = Vector((float(rim_c[0]), float(yy), 0.0029 + 0.001 + 0.0253 / 2))
            pts_ = [Vector(row) + cpt for row in hv_ @ Rn.T]
            trials.append((sum(1 for q_ in pts_ if outside(q_) or in_pi(q_)), hi_, heading, cols_h, cpt))
    # the fewest conflicts, then the furthest back among positions within 3 points of that
    least = min(t_[0] for t_ in trials)
    bad_h, hi_, heading, cols_h, cpt = max((t_ for t_ in trials if t_[0] <= least + 3), key=lambda t_: t_[4].y)
    for hh in sorted(set(t_[1] for t_ in trials)):
        bh = min((t_ for t_ in trials if t_[1] == hh), key=lambda t_: (t_[0], -t_[4].y))
        print("RESULT battery heading %d (%s): best %d conflicts at y %.1f mm" % (hh, bh[2], bh[0], bh[4].y * 1000))
    print("RESULT battery chosen: battery_h=%d battery_y=%.4f" % (hi_, cpt.y))
    hv_all = np.array([list(x_.co) for x_ in hat.data.vertices])
    hat.matrix_world = Matrix.Translation(cpt) @ Matrix(cols_h).transposed().to_4x4() @ Matrix.Scale(0.001, 4) @ Matrix.Translation(-Vector((hv_all.min(0) + hv_all.max(0)) / 2))
    print("RESULT battery board: on the floor, %s, centre y %.1f mm; %d of %d sampled points conflict" % (heading, cpt.y * 1000, bad_h, len(hv_)))

    sge = math.radians(float(opt.get("grille_elev", 24)))
    sdg = Vector((0, math.cos(sge), math.sin(sge)))                 # same axis as the grille
    sgv = sdg.cross(X)
    s_in = Vector(rim_c) - N * 0.03 + Vector((0, 0, float(opt.get("grille_dz", 0))))
    ts = []
    # the speaker's flange is a 102 x 45 mm pill: probe its outline, not the corners of its box
    flange = [(0, 0), (0, 0.0225), (0, -0.0225)]
    flange += [(sx_ * (0.0287 + 0.0225 * math.cos(a_)), 0.0225 * math.sin(a_)) for sx_ in (-1, 1) for a_ in np.linspace(-math.pi / 2, math.pi / 2, 9)]
    for su, sv in flange:
        sh = bvh.ray_cast(s_in + X * su + sgv * sv + sdg * 0.3, -sdg)
        ts.append(None if sh[0] is None else (sh[0] - s_in).dot(sdg))
    if None in ts:
        print("RESULT speaker: the 102 x 45 mm speaker is wider than the shell behind the grille, left out")
        parts_in = [hat]
    else:
        t_face = min(ts) - 0.004
        spk = place_stl("Speaker_5W_8Ohm_100mm_45mm_2.stl", "Speaker", (X, sdg, X.cross(sdg)), s_in + sdg * (t_face - 0.0137), flat("Speaker", (0.03, 0.03, 0.032), 0.4, 0.3))
        print("RESULT speaker: face sits %.1f mm inside the outer surface at the grille centre" % ((ts[0] - t_face) * 1000))
        parts_in = [hat, spk]

    # positions set by hand in Blender win over the placement above
    layout_file = os.path.join(HERE, "fastclock_layout.json")
    if os.path.exists(layout_file) and opt.get("layout", "on") == "on":
        import json
        for lname, vals in json.load(open(layout_file)).items():
            if lname in bpy.data.objects:
                bpy.data.objects[lname].matrix_world = Matrix([vals[i:i + 4] for i in range(0, 16, 4)])
                print("RESULT layout: %s placed from fastclock_layout.json" % lname)
        bpy.context.view_layer.update()

    # honest fit report: how much of each part pokes outside the shell or into the Pi
    for ob in parts_in:
        pts_ = [ob.matrix_world @ v_.co for v_ in ob.data.vertices][::max(1, len(ob.data.vertices) // 600)]
        print("RESULT fit %s: of %d sampled points, %d outside the shell, %d inside the Pi" % (ob.name, len(pts_), sum(map(outside, pts_)), sum(map(in_pi, pts_))))
    if len(parts_in) == 2 and "layout_search" in opt:
        # Search speaker tilt, speaker height and battery position together. Hard rule: no speaker
        # point inside the Pi. Then fewest other conflicts, then the battery as far back as it goes.
        sv0 = np.array([list(x_.co) for x_ in spk.data.vertices])
        sv0 = (sv0 - (sv0.min(0) + sv0.max(0)) / 2)[:: max(1, len(sv0) // 300)] * 0.001
        cands = []
        for elev_ in range(-30, 31, 5):
            for dz_ in np.arange(-0.010, 0.0201, 0.0025):
                e_ = math.radians(elev_)
                d_ = Vector((0, math.cos(e_), math.sin(e_)))
                v_ = d_.cross(X)
                o_ = Vector(rim_c) - N * 0.03 + Zw * float(dz_)
                tt = []
                for su, sv in flange:
                    sh = bvh.ray_cast(o_ + X * su + v_ * sv + d_ * 0.3, -d_)
                    tt.append(None if sh[0] is None else (sh[0] - o_).dot(d_))
                if None in tt:
                    continue
                tf = min(tt) - 0.004
                P_ = sv0 @ np.array(Matrix((X, d_, X.cross(d_))).transposed()).T + np.array(o_ + d_ * (tf - 0.0137))
                pv_ = [Vector(r_) for r_ in P_]
                cands.append((elev_, float(dz_), P_, sum(map(in_pi, pv_)), sum(map(outside, pv_)), (tt[0] - tf) * 1000))
        RnA = np.array(Matrix((-Yw, X, Zw)).transposed())
        batt = []
        for yy in np.arange(-0.010, 0.0451, 0.0015):
            bp_ = [Vector(r_) + Vector((float(rim_c[0]), float(yy), 0.0029 + 0.001 + 0.0253 / 2)) for r_ in hv_ @ RnA.T]
            batt.append((float(yy), sum(map(outside, bp_)), sum(map(in_pi, bp_))))
        best_l = None
        for elev_, dz_, P_, npi, nout, gap in cands:
            for yy, bo, bpi in batt:
                inb = int(((np.abs(P_[:, 0] - rim_c[0]) < 0.04425) & (np.abs(P_[:, 1] - yy) < 0.0285) & (P_[:, 2] < 0.0297)).sum())
                score = npi * 1000 + (nout + inb + bo + bpi) * 10 - yy * 500
                if best_l is None or score < best_l[0]:
                    best_l = (score, elev_, dz_, yy, npi, nout, inb, bo, bpi, gap)
        _, elev_, dz_, yy, npi, nout, inb, bo, bpi, gap = best_l
        print("RESULT layout: grille_elev=%d grille_dz=%.4f battery_y=%.4f | speaker: %d in the Pi, %d outside, %d in the battery board; battery board: %d outside, %d in the Pi (of %d); speaker face %.1f mm in" % (
            elev_, dz_, yy, npi, nout, inb, bo, bpi, len(hv_), gap))
    if len(parts_in) == 2 and "speaker_search" in opt:
        # where on the back does the speaker clear the Pi? Try every vent height.
        sv0 = np.array([list(x_.co) for x_ in spk.data.vertices])
        sv0 = (sv0 - (sv0.min(0) + sv0.max(0)) / 2)[:: max(1, len(sv0) // 300)] * 0.001
        for elev_ in range(-20, 71, 5):
            e_ = math.radians(elev_)
            d_ = Vector((0, math.cos(e_), math.sin(e_)))
            v_ = d_.cross(X)
            tt = []
            for su, sv in flange:
                sh = bvh.ray_cast(s_in + X * su + v_ * sv + d_ * 0.3, -d_)
                tt.append(None if sh[0] is None else (sh[0] - s_in).dot(d_))
            if None in tt:
                print("RESULT search elev %d: does not fit" % elev_)
                continue
            tf = min(tt) - 0.004
            Rs = np.array(Matrix((X, d_, X.cross(d_))).transposed())
            cs_ = s_in + d_ * (tf - 0.0137)
            pp_ = [Vector(row) + cs_ for row in sv0 @ Rs.T]
            print("RESULT search elev %d: face %.1f mm in, %d of %d points in the Pi, %d outside, %d below the battery top" % (
                elev_, (tt[0] - tf) * 1000, sum(map(in_pi, pp_)), len(pp_), sum(map(outside, pp_)), sum(1 for q_ in pp_ if q_.z < 0.0292)))
    if len(parts_in) == 2:
        inv = spk.matrix_world.inverted()
        sv_ = np.array([list(x_.co) for x_ in spk.data.vertices])
        lo_s, hi_s = sv_.min(0), sv_.max(0)
        hv = np.array([list(inv @ (hat.matrix_world @ v_.co)) for v_ in hat.data.vertices])
        clash = int(((hv > lo_s) & (hv < hi_s)).all(1).sum())
        print("RESULT fit: %d of %d battery-board points fall inside the speaker's box" % (clash, len(hv)))

# ---------------------------------------------------------------- buttons
# Keycap-style buttons in an arc along the top, just behind the display: orange, a wide white
# one, two black. Sizes and positions are a design draft; no switches are modelled under them.
if opt.get("buttons", "on") == "on":
    # the white is kept a little under paper-white so the cut-in mark still shows a shadow
    BLK, WHT, RED, INK = (0.018, 0.018, 0.02), (0.72, 0.72, 0.70), (0.75, 0.03, 0.02), (0.05, 0.05, 0.055)
    # name, width, cap colour, symbol, symbol colour  (left to right seen from the front)
    ORG = (0.80, 0.21, 0.02)
    # the marks are cut 0.6 mm into the caps, in the cap's own colour; nothing is printed on
    KEYS = [("record", 0.015, ORG, "dot", ORG), ("play", 0.032, WHT, "play", WHT), ("plus", 0.015, BLK, "plus", BLK), ("minus", 0.015, BLK, "minus", BLK)]
    GAP, KD, ARC_R, SETBACK = 0.003, 0.015, 0.072, 0.0145

    def mat(name, col, rough=0.42):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        pbs = m.node_tree.nodes["Principled BSDF"]
        pbs.inputs["Base Color"].default_value = (*col, 1)
        pbs.inputs["Roughness"].default_value = rough
        return m

    def pill(w, d, seg=20):
        """Outline of a round or pill-shaped cap: a circle when w == d."""
        r, half = d / 2, (w - d) / 2
        pts = [(half + r * math.cos(-math.pi / 2 + math.pi * i / seg), r * math.sin(-math.pi / 2 + math.pi * i / seg)) for i in range(seg + 1)]
        pts += [(-half + r * math.cos(math.pi / 2 + math.pi * i / seg), r * math.sin(math.pi / 2 + math.pi * i / seg)) for i in range(seg + 1)]
        return pts

    def solid(name, outline, z0, z1, world, material, inset=0.0, bevel=0.0):
        me_ = bpy.data.meshes.new(name)
        sbm = bmesh.new()
        cx = sum(p_[0] for p_ in outline) / len(outline)
        cy = sum(p_[1] for p_ in outline) / len(outline)
        def shrink(pt):
            dx, dy = pt[0] - cx, pt[1] - cy
            ln_ = math.hypot(dx, dy) or 1.0
            return (pt[0] - dx / ln_ * inset, pt[1] - dy / ln_ * inset)
        lo_r = [sbm.verts.new((px, py, z0)) for px, py in outline]
        hi_r = [sbm.verts.new((*shrink(pt), z1)) for pt in outline]
        sbm.faces.new(lo_r[::-1])
        sbm.faces.new(hi_r)
        for i in range(len(outline)):
            j = (i + 1) % len(outline)
            sbm.faces.new((lo_r[i], lo_r[j], hi_r[j], hi_r[i]))
        for f in sbm.faces:
            f.smooth = True
        bmesh.ops.recalc_face_normals(sbm, faces=sbm.faces)
        sbm.to_mesh(me_)
        sbm.free()
        ob = link(bpy.data.objects.new(name, me_))
        ob.matrix_world = world
        if bevel:
            bv = ob.modifiers.new("Bevel", "BEVEL")
            bv.width = bevel
            bv.segments = 5
            bv.limit_method = "ANGLE"
            bv.angle_limit = math.radians(40)
            bv.harden_normals = True
        me_.materials.append(material)
        return ob

    def symbol(kind):
        if kind == "dot":
            return [(0.0027 * math.cos(2 * math.pi * i / 32), 0.0027 * math.sin(2 * math.pi * i / 32)) for i in range(32)]
        if kind == "play":
            return [(-0.0024, -0.0031), (0.0034, 0.0), (-0.0024, 0.0031)]
        a_, t_ = 0.0032, 0.0009
        if kind == "minus":
            return [(-a_, -t_), (a_, -t_), (a_, t_), (-a_, t_)]
        return [(-a_, -t_), (-t_, -t_), (-t_, -a_), (t_, -a_), (t_, -t_), (a_, -t_), (a_, t_), (t_, t_), (t_, a_), (-t_, a_), (-t_, t_), (-a_, t_)]
    total = sum(k[1] for k in KEYS) + GAP * (len(KEYS) - 1)
    run = -total / 2
    for name, kw, col, sym, sym_col in KEYS:
        phi = (run + kw / 2) / ARC_R
        run += kw + GAP
        radial = Y * math.cos(phi) + X * math.sin(phi)
        hit = bvh.ray_cast(Vector(rim_c) - N * SETBACK + radial * 0.2, -radial)
        if hit[0] is None:
            continue
        up = hit[1].normalized()
        if up.dot(radial) < 0:
            up = -up
        tang = X * math.cos(phi) - Y * math.sin(phi)
        tang = (tang - up * tang.dot(up)).normalized()
        dep = up.cross(tang)
        world = Matrix.Translation(hit[0]) @ Matrix((tang, dep, up)).transposed().to_4x4()
        top_z = float(opt.get("button_h", 0.005))      # cap height above the shell
        cap = solid("Key " + name, pill(kw, KD), -0.0035, top_z, world, mat("Keycap " + name, col), inset=0.0012, bevel=0.0016)
        cut = solid("Key cut " + name, symbol(sym), top_z - 0.00097, top_z + 0.00113, world, mat("Key cut " + name, sym_col))   # 1 mm deep
        cut.hide_render = True
        cut.hide_viewport = True
        eng = cap.modifiers.new("Engrave", "BOOLEAN")
        eng.operation = "DIFFERENCE"
        eng.object = cut
        for solver_ in ("MANIFOLD", "EXACT"):
            try:
                eng.solver = solver_
                break
            except TypeError:
                pass
        crisp = cap.modifiers.new("Crisp edges", "EDGE_SPLIT")
        crisp.split_angle = math.radians(40)
        # keep the flat top flat: without this the top borrows the rounded edge's normals and
        # the cut-out face shades with creases
        flatn = cap.modifiers.new("Flat faces", "WEIGHTED_NORMAL")
        flatn.mode = "FACE_AREA"
        flatn.weight = 100
        flatn.keep_sharp = True
        for m_ in cap.modifiers:
            if m_.type == "BEVEL":
                m_.harden_normals = False
    print("RESULT buttons: %d round caps over a %.0f mm arc" % (len(KEYS), total * 1000))

# ---------------------------------------------------------------- studio
prof = [(-2.0, 0.0)]
R = 0.45
for i in range(0, 25):
    a = math.radians(-90 + i * 90 / 24)
    prof.append((0.55 + R * math.cos(a), R + R * math.sin(a)))
prof.append((0.55 + R, 1.8))
sm = bpy.data.meshes.new("Sweep")
sb = bmesh.new()
rows = []
for x in (-2.5, 2.5):
    rows.append([sb.verts.new((x, y, z)) for y, z in prof])
for i in range(len(prof) - 1):
    sb.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
for f in sb.faces:
    f.smooth = True
sb.normal_update()
sb.to_mesh(sm)
sb.free()
sweep = link(bpy.data.objects.new("Sweep", sm))
sweep_mat = bpy.data.materials.new("Sweep paper")
sweep_mat.use_nodes = True
s = sweep_mat.node_tree.nodes["Principled BSDF"]
s.inputs["Base Color"].default_value = (0.022, 0.022, 0.026, 1) if opt.get("bg") == "dark" else (0.50, 0.495, 0.485, 1)
s.inputs["Roughness"].default_value = 0.7
sm.materials.append(sweep_mat)


def area(name, loc, target, size, power, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, "AREA")
    l.shape = "RECTANGLE"
    l.size, l.size_y = size
    l.energy = power
    l.color = color
    o = link(bpy.data.objects.new(name, l))
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


tgt = centre
area("Key", (-0.75, -0.55, 0.85), tgt, (0.9, 0.7), 30, (1.0, 0.97, 0.93))
area("Fill", (0.9, -0.5, 0.35), tgt, (0.8, 0.8), 5, (0.93, 0.96, 1.0))
area("Rim", (0.45, 0.75, 0.65), tgt, (0.6, 0.4), 20)
area("Top", (0.0, 0.05, 1.1), tgt, (1.2, 1.2), 10)

world = bpy.data.worlds.new("World")
world.use_nodes = True
scn.world = world
wn = world.node_tree
bg = wn.nodes["Background"]
hdrs = glob.glob(os.path.join(os.path.dirname(bpy.app.binary_path), "..", "Resources", "*", "datafiles", "studiolights", "world", "interior.exr"))
if hdrs:
    env = wn.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.abspath(hdrs[0]))
    wn.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.14
else:
    bg.inputs["Color"].default_value = (0.5, 0.5, 0.5, 1)
    bg.inputs["Strength"].default_value = 0.25

# ---------------------------------------------------------------- camera + render
cam_d = bpy.data.cameras.new("Cam")
cam_d.lens = 85
cam_d.sensor_width = 36
cam_d.dof.use_dof = True
cam_d.dof.aperture_fstop = 11
cam = link(bpy.data.objects.new("Cam", cam_d))
scn.camera = cam
focus = link(bpy.data.objects.new("Focus", None))
cam_d.dof.focus_object = focus
body_mid = Vector((0, float(vs[:, 1].mean()), float(vs[:, 2].max()) / 2))

# name: (azimuth from front, elevation, distance, look-at)
SHOTS = {
    "hero":  (-26, 20, 0.80, centre.lerp(body_mid, 0.35)),
    "front": (0, 34, 0.74, centre),
    "side":  (88, 6, 0.82, body_mid),
    "back":  (152, 16, 0.82, body_mid),
    "rear":  (180, 24, 0.80, body_mid),
    "top":   (-32, 46, 0.72, centre.lerp(body_mid, 0.5) + Vector((0, 0, 0.02))),
    "ports": (62, 14, 0.76, body_mid + Vector((0.01, 0, 0.005))),
    "keys":  (176, 66, 0.36, Vector(rim_c) + Vector((0, 0.035, 0.058))),
}

scn.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
try:
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scn.cycles.device = "GPU"
except Exception as exc:
    print("RESULT gpu unavailable", exc)
final = MODE == "final"
scn.cycles.samples = 320 if final else 40
scn.cycles.use_denoising = True
scn.render.resolution_x = 2400 if final else 960
scn.render.resolution_y = 1350 if final else 540
scn.view_settings.view_transform = "AgX"
scn.view_settings.look = "AgX - Medium High Contrast"
scn.render.image_settings.file_format = "PNG" if final else "JPEG"
if MODE == "model":
    # plain model view: flat colours per part and a see-through shell, to check the assembly
    for m_ in bpy.data.materials:
        nm = m_.name
        if nm.startswith("Body plastic"):
            col_ = (0.80, 0.86, 0.93, 0.20)
        elif nm.startswith("Port door"):
            col_ = (0.45, 0.75, 1.0, 0.30)
        elif nm.startswith("Display glass"):
            col_ = (0.03, 0.03, 0.035, 1)
        elif nm.startswith("Display frame"):
            col_ = (0.09, 0.09, 0.10, 1)
        elif nm == "PCB":
            col_ = (0.55, 0.20, 0.75, 1)          # display driver board: purple
        elif nm.startswith("Battery"):
            col_ = (0.12, 0.28, 0.90, 1)          # battery board: blue
        elif nm.startswith("Speaker"):
            col_ = (0.06, 0.06, 0.065, 1)         # speaker: black, as the real one is
        elif nm.startswith(("Keycap", "Key cut", "Cable", "Pi5")):
            col_ = tuple(m_.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value)
        elif nm.startswith(("Sweep", "World")):
            continue
        else:
            col_ = (0.15, 0.62, 0.30, 1)          # the Pi: green
        m_.diffuse_color = col_
    sweep.hide_render = True
    sweep.hide_viewport = True
    scn.render.engine = "BLENDER_WORKBENCH"
    scn.display.shading.light = "STUDIO"
    scn.display.shading.color_type = "MATERIAL"
    scn.display.shading.show_cavity = True
    scn.display.shading.show_shadows = False
    world.use_nodes = False
    world.color = (0.95, 0.95, 0.95)
    scn.view_settings.view_transform = "Standard"
    scn.view_settings.look = "None"
    scn.render.resolution_x, scn.render.resolution_y = 1200, 800
os.makedirs(OUT, exist_ok=True)
tag = os.path.splitext(os.path.basename(SCREEN))[0] if SCREEN else "off"
if BODY != "white":
    tag = BODY + "_" + tag
if STYLE not in ("sunflower", "off"):
    tag += "_" + STYLE
if opt.get("bg") == "dark":
    tag += "_dark"
for name in VIEWS:
    az, elv, dist, look = SHOTS[name]
    a, e = math.radians(az), math.radians(elv)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    cam.location = look + d * dist
    cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler()
    focus.location = look if name == "keys" else (centre if abs(az) < 60 else look + d * 0.06)
    sweep.rotation_euler = (0, 0, a)          # keep the backdrop behind the clock in every shot
    scn.render.filepath = os.path.join(OUT, "fastclock_%s_%s" % (name, tag))
    bpy.ops.render.render(write_still=True)
    print("RESULT rendered", scn.render.filepath)
    if MODE == "model":
        shell = [o for o in scn.objects if o.name in ("Body", "Port cover")]
        for o in shell:
            o.hide_render = True
        scn.render.filepath += "_open"
        bpy.ops.render.render(write_still=True)
        for o in shell:
            o.hide_render = False

if MODE == "model":
    bpy.ops.file.pack_all()
    # a separate file, so a model view never overwrites the scene Nick is editing by hand
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "fastclock_assembly_latest.blend"))
    print("RESULT saved model blend")

if final:
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "fastclock_product%s.blend" % ("" if BODY == "white" else "_" + BODY)))
    print("RESULT saved blend")
