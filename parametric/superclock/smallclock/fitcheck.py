"""
Fit check: the measured smallclock hardware stack inside the enclosure.

Builds the stack, reports every clash with the enclosure's parts and between
the parts, checks that it stands (every part's centre of mass over the foot),
and renders a cutaway sheet and an on-the-desk sheet.

    ~/ClaudeCode\\ Projects/cad-skill/.venv/bin/python fitcheck.py [puck|pebble|block|dome|dome_flush]

puck (the default) writes fitcheck_cutaway_preview.png and fitcheck_assembly_preview.png;
the others write fitcheck_<model>_cutaway_preview.png and fitcheck_<model>_assembly_preview.png.
Each model script exposes FIT_PARTS, FIT_ENVELOPE, FIT_PRESS_FITS, FIT_BACK_HIDE and DESK.

Where each part's geometry comes from:
  display, driver board, hex standoffs   vendor/3_4inch-DSI-LCD_C.stp (exact)
  Raspberry Pi 4B                        Raspberry Pi STEP (not redistributed here;
                                         path in PI_STEP), seated on the vendor
                                         standoffs, which match its holes to 0.2 mm
  Pi -> PiPower spacers                  24.5 mm, measured off a side photo with the
                                         Ethernet jack (21.6 x 13.5) as the ruler
  PiPower v2 board, holes, ports         SunFounder dimension drawing and layout,
                                         github.com/sunfounder/pipower (docs-v2.0)
  2S pack                                74 x 38 mm off a back photo (PiPower holes
                                         58 mm apart as the ruler); 19.5 thick = 2x18650
  USB mic                                SuziePi B0CYM618H7, 23 x 20 x 5 mm, outer port
                                         of the USB3 stack (side photo)

Frame: built in the vendor STEP frame (glass front at z=+3.95, +Z toward the
viewer, -Y is the FPC / GPIO / charge-port edge), then turned 180 degrees
about Y into the enclosure's body frame.
"""
import math
import os
import sys
import tempfile

import cadquery as cq
import numpy as np
import pyrender
import trimesh
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor", "3_4inch-DSI-LCD_C.stp")
PI_STEP = os.environ.get("PI_STEP", os.path.expanduser(
    "~/Product Design/SuperClock/Component CAD models/CAD RasperiPI/Raspberry Pi 4 Model B.STEP"))

# ---- stack, STEP frame ----
GLASS_Z = 3.95
PI_UNDER_Z = -13.15             # end of the vendor hex standoffs
PI_PCB_T = 1.6
SPACER_L = 24.5
PP_T = 1.6
TAPE_T = 0.5
BAT = dict(l=74.0, w=38.0, t=19.5, cx=-3.3, cy=-2.8)
PP_X0 = -39.2 - 5.7             # PiPower SD-end edge: its first hole is 5.7 mm in
PP_W, PP_H = 90.0, 56.0
HOLES = [(18.8, 24.5), (18.8, -24.5), (-39.2, 24.5), (-39.2, -24.5)]

pi_comp = PI_UNDER_Z - PI_PCB_T                 # Pi component face
pp_comp = pi_comp - SPACER_L                    # PiPower component face, faces the Pi
pp_back = pp_comp - PP_T
bat_top = pp_back - TAPE_T
bat_back = bat_top - BAT["t"]


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def display():
    out = []
    for s in cq.importers.importStep(VENDOR).solids().vals():
        b = s.BoundingBox()
        col = "glass" if b.xlen > 100 else "driver" if b.xlen > 80 else "steel" if b.zlen > 9 else "conn"
        out.append(("display", col, cq.Workplane("XY").add(s)))
    return out


def pi4():
    # Pi STEP frame: ports at +X, components at +Y, GPIO at -Z.
    # -90 about X puts the components toward the back and the GPIO at -Y.
    if os.path.exists(PI_STEP):
        out = []
        for s in cq.importers.importStep(PI_STEP).solids().vals():
            s2 = s.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90).translate(cq.Vector(-0.2, 0, PI_UNDER_Z - 0.8))
            out.append(("pi", "pi" if s.BoundingBox().xlen > 80 else "pi_part", cq.Workplane("XY").add(s2)))
        return out
    print(f"Pi STEP not found ({PI_STEP}); using its envelope instead")
    x0 = -42.7
    return [("pi", "pi", box(x0, x0 + 85, -28, 28, pi_comp, PI_UNDER_Z)),
            ("pi", "pi_part", box(x0 + 66.9, x0 + 89.0, -26, 27, pi_comp - 16.2, pi_comp))]


def pipower():
    x = lambda d: PP_X0 + d                         # distance from the SD-end edge
    up = lambda z0, h: (pp_comp + z0, pp_comp + z0 + h)
    pcb = (cq.Workplane("XY").rect(PP_W, PP_H).extrude(PP_T).edges("|Z").fillet(3.0)
           .translate((PP_X0 + PP_W / 2, 0, pp_back)))
    parts = [("pipower", "pp", pcb),
             ("usb_a_out", "metal", box(x(14) - 7.3, x(14) + 7.3, -29.0, -15.0, *up(-3.0, 7.0))),
             ("usb_c_in", "metal", box(x(55.7) - 4.5, x(55.7) + 4.5, -28.8, -21.3, *up(0, 3.3))),
             ("battery_conn", "white", box(x(82.5) - 3.0, x(82.5) + 3.0, -19.0, -7.0, *up(0, 6.0))),
             ("switch", "metal", box(x(78) - 4.5, x(78) + 4.5, 22.0, 30.3, *up(0, 4.0))),
             ("inductor", "pp_part", box(x(48) - 5.0, x(48) + 5.0, 2.0, 12.0, *up(0, 4.0))),
             ("battery", "battery", box(BAT["cx"] - BAT["l"] / 2, BAT["cx"] + BAT["l"] / 2,
                                        BAT["cy"] - BAT["w"] / 2, BAT["cy"] + BAT["w"] / 2,
                                        bat_back, bat_top)),
             ("screw_terminal", "green", box(x(PP_W) - 8.0, x(PP_W) - 1.0, 8.0, 19.0, pp_back - 10.0, pp_back)),
             ("5v_header_dupont", "pp_part", box(x(0.5), x(5.5), -6.0, 4.0, pp_back - 16.0, pp_back))]
    for hx, hy in HOLES:
        parts.append(("spacer", "brass", cq.Workplane("XY").circle(2.5).extrude(SPACER_L)
                      .translate((hx, hy, pp_comp))))
    # right-angle USB-C charge plug, cable turning toward the back
    c, zc = x(55.7), pp_comp + 1.65
    parts.append(("charge_plug_90", "cable", box(c - 6.0, c + 6.0, -28.8 - 18.0, -28.8, zc - 3.5, zc + 3.5)))
    return parts


def mic():
    # outer port of the USB3 stack, port face at x = 46.3
    head = cq.Workplane("YZ").circle(10.0).extrude(11.0).translate((46.3, 1.0, PI_UNDER_Z - 0.8 - 12.3))
    return [("usb_mic", "mic", head)]


def stack_body_frame(lip_t):
    """All stack parts, turned into the enclosure's body frame."""
    out = []
    for name, col, wp in display() + pi4() + pipower() + mic():
        out.append((name, col, wp.rotate((0, 0, 0), (0, 1, 0), 180).translate((0, 0, lip_t + GLASS_Z))))
    return out


# ---- enclosure, built by the model script in a temp dir (it writes its exports to cwd) ----
MODELS = {"puck": "smallclock_enclosure.py", "pebble": "smallclock_pebble.py", "block": "smallclock_block.py",
          "dome": "smallclock_dome.py", "dome_flush": "smallclock_dome_flush.py"}   # DOME=egg|balanced|wide


def enclosure(script="smallclock_enclosure.py"):
    ns = {}
    cwd = os.getcwd()
    os.chdir(tempfile.mkdtemp())
    try:
        with open(os.path.join(HERE, script)) as f:
            exec(f.read(), ns)
    finally:
        os.chdir(cwd)
    return ns


def volume(wp):
    return sum(s.Volume() for s in wp.solids().vals()) if wp.solids().size() else 0.0


# ---- render ----
COL = {
    "glass": [0.05, 0.05, 0.06, 1], "driver": [0.10, 0.16, 0.30, 1], "steel": [0.75, 0.76, 0.78, 1],
    "conn": [0.85, 0.85, 0.82, 1], "pi": [0.16, 0.52, 0.27, 1], "pi_part": [0.78, 0.78, 0.80, 1],
    "pp": [0.10, 0.10, 0.11, 1], "pp_part": [0.30, 0.30, 0.32, 1], "metal": [0.80, 0.80, 0.82, 1],
    "white": [0.95, 0.95, 0.93, 1], "battery": [0.18, 0.42, 0.88, 1], "green": [0.25, 0.75, 0.35, 1],
    "brass": [0.80, 0.62, 0.25, 1], "mic": [0.12, 0.12, 0.12, 1], "cable": [0.97, 0.97, 0.97, 1],
    "shell": [0.62, 0.48, 0.80, 1], "lid": [0.55, 0.42, 0.72, 1], "cradle": [0.88, 0.87, 0.85, 1],
    "body": [0.62, 0.48, 0.80, 1], "bezel": [0.50, 0.38, 0.66, 1], "back": [0.55, 0.42, 0.72, 1],
    "hit": [0.95, 0.10, 0.10, 1],
}


def to_tm(wp):
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        cq.exporters.export(wp, f.name, tolerance=0.05, angularTolerance=0.2)
        return trimesh.load(f.name, force="mesh")


def render(items, eye, up, size=720, ortho=False, zoom=1.0):
    from preview import _add_edges
    scene = pyrender.Scene(bg_color=[0.96, 0.96, 0.97, 1.0], ambient_light=[0.4, 0.4, 0.4])
    verts = []
    for tm, col in items:
        verts.append(tm.vertices)
        scene.add(pyrender.Mesh.from_trimesh(tm, smooth=False, material=pyrender.MetallicRoughnessMaterial(
            baseColorFactor=COL[col], metallicFactor=0.05, roughnessFactor=0.7, doubleSided=True)))
    for d in ([1, 1, 1], [-1, 0.5, 0.6], [0, -1, 0.8], [0.3, 1, -0.4]):
        d = np.array(d, float) / np.linalg.norm(d)
        pose = np.eye(4); pose[:3, 2] = d
        scene.add(pyrender.DirectionalLight(color=[1, 1, 1], intensity=2.0), pose=pose)
    v = np.vstack(verts)
    center, radius = (v.min(0) + v.max(0)) / 2, np.linalg.norm(v.max(0) - v.min(0)) / 2
    eye = np.array(eye, float) / np.linalg.norm(eye)
    right = np.cross(-eye, up); right /= np.linalg.norm(right)
    pose = np.eye(4); pose[:3, 0], pose[:3, 1], pose[:3, 2] = right, np.cross(right, -eye), eye
    if ortho:
        cam = pyrender.OrthographicCamera(xmag=radius * 0.8 / zoom, ymag=radius * 0.8 / zoom, znear=1, zfar=5000)
        pose[:3, 3] = center + eye * radius * 4
    else:
        yfov = math.radians(28)
        cam = pyrender.PerspectiveCamera(yfov=yfov)
        pose[:3, 3] = center + eye * radius / math.sin(yfov / 2) * 1.02 / zoom
    scene.add(cam, pose=pose)
    r = pyrender.OffscreenRenderer(size, size)
    color, depth = r.render(scene)
    r.delete()
    return Image.fromarray(_add_edges(color, depth, strength=0.6))


def sheet(views, title, out):
    f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    w = views[0][0].width
    img = Image.new("RGB", (w * len(views), w + 90), "white")
    d = ImageDraw.Draw(img)
    d.text((14, 10), title, fill=(20, 20, 20), font=f)
    for i, (im, label) in enumerate(views):
        img.paste(im, (i * w, 80))
        d.text((i * w + 14, 48), label, fill=(90, 90, 90), font=f)
    img.save(out)


if __name__ == "__main__":
    sys.path.insert(0, os.path.expanduser("~/ClaudeCode Projects/cad-skill"))
    model = sys.argv[1] if len(sys.argv) > 1 else "puck"
    ns = enclosure(MODELS[model])
    encl = ns["FIT_PARTS"]
    envelope = ns["FIT_ENVELOPE"]
    press = {tuple(sorted(p)) for p in ns.get("FIT_PRESS_FITS", [])}
    hide = ns.get("FIT_BACK_HIDE", [])
    extra = ns.get("FIT_WORLD_EXTRA", [])
    desk_pose = ns["DESK"]
    names = [n for n, _ in encl]
    parts = stack_body_frame(ns["lip_t"])
    suffix = "" if model == "puck" else f"_{model}" + (f"_{os.environ.get('DOME', 'balanced')}" if model.startswith("dome") else "")

    print(f"{model}: clashes with {', '.join(names)} (mm^3); 'outside' = beyond the enclosure envelope")
    hits, clean = [], True
    for name, col, wp in parts:
        if name == "display":
            continue
        vols = [(n, wp.intersect(p)) for n, p in encl] + [("outside", wp.cut(envelope))]
        vols = [(n, w, volume(w)) for n, w in vols]
        if sum(v for _, _, v in vols) > 0.5:
            clean = False
            print(f"  {name:18s} " + "  ".join(f"{n} {v:7.1f}" for n, _, v in vols))
            hits += [w for _, w, v in vols if v > 0.5]
    for i in range(len(encl)):
        for j in range(i + 1, len(encl)):
            (n1, p1), (n2, p2) = encl[i], encl[j]
            v = volume(p1.intersect(p2))
            if v > 0.5:
                tag = "press fit, expected" if tuple(sorted((n1, n2))) in press else "CLASH"
                clean = clean and tag != "CLASH"
                print(f"  {n1} vs {n2}: {v:.1f} ({tag})")
    if clean:
        print("  none")
    # radial room left around the stack while it slides through the bore (mic goes in last)
    worst = min((ns["bore_r"] - float(np.hypot(m.vertices[:, 0], m.vertices[:, 1]).max()), name)
                for name, _, wp in parts if name not in ("display", "usb_mic")
                for m in [to_tm(wp)])
    print(f"tightest radial gap while sliding the stack in: {worst[0]:.1f} mm ({worst[1]})")

    # standing: nothing is weighed yet, so each assembly gets a mass range and every edge of the
    # contact patch is checked at its worst case (parts beyond the edge heaviest, the rest lightest)
    to_desk = lambda wp: wp.rotate((0, 0, 0), (1, 0, 0), 90.0 + desk_pose["tilt"]).translate((0, 0, desk_pose["lift"]))
    shells = [(n, to_desk(p)) for n, p in encl] + list(extra)       # extra (the puck's cradle) is already posed
    feet = np.vstack([to_tm(p).vertices for _, p in shells])
    contact = feet[feet[:, 2] < feet[:, 2].min() + 0.3][:, :2]
    from scipy.spatial import ConvexHull
    edges = ConvexHull(contact).equations                          # outward normal, offset per edge
    groups = {}
    for name, _, wp in parts:                                      # the PiPower takes its plugs and spacers
        g = {"display": "display", "pi": "pi", "battery": "battery", "usb_mic": "mic"}.get(name, "pipower")
        groups.setdefault(g, []).extend(to_desk(wp).solids().vals())
    mass = {"display": (60, 250),    # g - not weighed: deliberately wide
            "pi": (40, 50),          # Raspberry Pi 4B, 46 g
            "pipower": (10, 40), "battery": (80, 110), "mic": (2, 10)}   # 2S pack = 2x 18650 at 45-50 g each
    for n, wp in shells:
        groups[n] = wp.solids().vals()
        mass[n] = tuple(volume(wp) * 1.27e-3 * f for f in (0.6, 1.0))  # PETG, printed 60-100 % solid
    out = {}                                                       # mm beyond each edge, per group
    for g, solids in groups.items():
        c = cq.Shape.centerOfMass(cq.Compound.makeCompound(solids))
        out[g] = edges[:, :2] @ [c.x, c.y] + edges[:, 2]
    worst = np.inf
    for e in range(len(edges)):
        inside = {g: -out[g][e] for g in groups}
        lam = 0.0                                                  # closest the centre of mass gets to this
        for _ in range(20):                                        # edge: heavy below lam, light above
            m = {g: mass[g][1] if inside[g] < lam else mass[g][0] for g in groups}
            lam_next = sum(m[g] * inside[g] for g in groups) / sum(m.values())
            if abs(lam_next - lam) < 1e-6:
                break
            lam = lam_next
        worst = min(worst, lam_next)
    disp = -float(out["display"].max())
    span = contact.max(0) - contact.min(0)
    print(f"standing: contact patch {span[0]:.0f} x {span[1]:.0f} mm; centre of mass at least {worst:.1f} mm "
          f"inside it for any weights in range; the display's own centre {disp:.1f} mm "
          + ("inside" if disp > 0 else "OUTSIDE") + ("" if worst > 0 else "  ** CAN TIP **"))

    hw =[(to_tm(wp), col) for _, col, wp in parts] + [(to_tm(h), "hit") for h in hits]
    near_half = cq.Workplane("XY").box(400, 400, 400).translate((200, 0, 0))   # +X half, toward the camera
    cut = [(to_tm(p.cut(near_half)), n) for n, p in encl]
    full = [(to_tm(p), n) for n, p in encl]
    side = render(hw + cut, eye=(1, 0, 0), up=(0, 1, 0), ortho=True)
    back = render(hw + [(m, n) for m, n in full if n not in hide], eye=(0, 0, 1), up=(0, 1, 0), ortho=True)
    port = render(full + hw, eye=(-1, 0.25, 0.9), up=(0, 1, 0))
    back_label = "from the back, " + (", ".join(hide) + " off" if hide else "closed")
    sheet([(side, "side cutaway (9 o'clock half removed)"), (back, back_label),
           (port, "port side: mic, switch slot")],
          f"smallclock {model} fit check: measured stack inside (red = clash)",
          os.path.join(HERE, f"fitcheck{suffix}_cutaway_preview.png"))

    # on the desk
    desk =([(to_tm(to_desk(p)), n) for n, p in encl] + [(to_tm(p), n) for n, p in extra]
            + [(to_tm(to_desk(wp)), col) for _, col, wp in parts if col == "glass"])
    sheet([(render(desk, eye=(0.75, 1, 0.45), up=(0, 0, 1)), "front"),
           (render(desk, eye=(-0.9, -1, 0.5), up=(0, 0, 1)), "back"),
           (render(desk, eye=(1, 0, 0.05), up=(0, 0, 1), ortho=True), "side")],
          f"smallclock {model} on the desk",
          os.path.join(HERE, f"fitcheck{suffix}_assembly_preview.png"))
    print(f"saved fitcheck{suffix}_cutaway_preview.png, fitcheck{suffix}_assembly_preview.png")
