"""
smallclock dome, flush face: the "fixed body" dome (smallclock_dome.py) with no
bezel. The display panel IS the front of the clock: the body starts right
behind it and its outer surface continues the glass edge.

Measured off the vendor STEP (vendor/3_4inch-DSI-LCD_C.stp):
  glass and module   r 57.5 for the first ~4.5 mm, stepping to r 56.5 at the back (6.0 mm)
  M4 holes           4x Ø3.3 tapped, 3.5 mm deep, at (±37.5, ±37.5), r 53, in the panel back
  display board      r <= 50.3, directly behind the panel (6.0..9.1 mm)
That leaves a free ring between r 50.3 and r 57.5 behind the panel. The body
seats against the panel there, flush with the glass edge.

How it holds together: the stack (display, Pi, PiPower, battery) slides in
from the front until the panel's back lands on the body's front ring. Four
M4x12 button-head screws go through bosses in the ring into the panel's M4
holes. The bosses sit behind the display board, at 45 degrees, where every
board stays inside r 45, so nothing crosses them on the way in. Each screw
drops down a slim guide tube and is driven with a long 2.5 mm hex key: the
top two tubes open in the back of the dome, the bottom two in the underside
of the foot.

Body frame: Z=0 is the glass front, +Z toward the back, +Y up (the PiPower's
charge-port edge is down), the Pi's port end at -X, 3 o'clock seen from the front.

    DOME=balanced ~/ClaudeCode\\ Projects/cad-skill/.venv/bin/python smallclock_dome_flush.py

Print orientation: front ring down (a flat 3 mm ring on the bed); tree
supports inside the dome only.
"""
import math
import os
import cadquery as cq

# ============================================================
# PARAMETERS - Edit these to customize the model
# ============================================================
DOME = os.environ.get("DOME", "balanced")
# widest outer radius over the radius at the face: smallclock_dome.py's ratios (Ø132 over a
# 60.3 rim for balanced), so each variant keeps its shape, resized to the bezel-free face
bulge = {"egg": 1.0, "balanced": 66.0 / 60.3, "wide": 70.0 / 60.3}[DOME]

# Display (vendor STEP, measured above)
panel_r = 57.5          # mm - glass edge, the body's outer radius where it meets the panel
dome_max_r = panel_r * bulge                   # 62.9 mm for balanced
panel_t = 6.0           # mm - glass front to the panel's back face
board_r = 50.3          # mm - display board, the largest radius right behind the panel
m4_square = 75.0        # mm - panel M4 hole pattern
m4_hole_depth = 3.5     # mm - blind M4 threads in the panel back

# Measured stack (fitcheck.py), z from the glass front
stack_back = 64.8       # mm - glass front to the back of the battery
bat_corner_r = 45.8     # mm - battery's farthest corner from the axis
pi_port_r = 53.5        # mm - Pi's USB/Ethernet corners, the widest part that slides through the ring
low_points = [(-57.5, 6.0),    # (y, z) bottom of the panel at its back face
              (-46.8, 45.0),   # bottom of the right-angle charge plug
              (-28.0, 44.8),   # PiPower bottom edge, back face
              (-21.8, 64.8)]   # battery bottom back edge

# Screws: M4x12 button head (ISO 7380), head Ø7.6
screw_len = 12.0        # mm
thread_engage = 3.0     # mm - leaves 0.5 mm before the hole bottom
screw_clear_d = 4.5     # mm
head_clear_d = 8.4      # mm - guide tube bore, head Ø7.6 + clearance

# Body
wall = 2.4              # mm
dome_clear = 2.0        # mm - inside the dome, over the battery's back corners
ring_in_r = 54.5        # mm - front ring opening: clears the Pi's ports (r 53.5) as the stack slides in
boss_d = 11.0           # mm - screw bosses in the ring
boss_from = 9.4         # mm - bosses start behind the display board (it ends at 9.1)
tube_od = 11.4          # mm - screw guide tubes, seat to the back of the dome
front_chamfer = 0.4     # mm - outer front edge (bed side)

# Stand (the original stands at 41 degrees; measured off clock_body_fixed.stl)
tilt_deg = 41.0
foot_clear = 3.0

# Openings (smallclock_enclosure.py positions, moved to the glass-front frame)
mic_port_w = 24.0
mic_port_r = 3.0
mic_y, mic_z = 1.0, 30.2
switch_slot_w = 14.0
switch_slot_h = 5.0
switch_x, switch_z = -33.0, 41.2
cable_hole_d = 7.0
cable_x = -26.0          # mm - clear of the vent slots (x ±18)
vent_w = 3.0
vent_len = 36.0
vent_pitch = 6.5
vent_rows = 3

# ============================================================
# DERIVED
# ============================================================
lip_t = 0.0                                    # glass front at z=0 (fitcheck places the stack by this)
bore_r = ring_in_r                             # the opening the stack slides through (fitcheck)
panel_back_z = panel_t                         # 6.0, the body's front face
seat_z = panel_back_z + screw_len - thread_engage   # 15.0, screw heads seat here
bat_back_z = stack_back                        # 64.8
post_xy = [(sx * m4_square / 2, sy * m4_square / 2) for sx in (1, -1) for sy in (1, -1)]

assert ring_in_r > pi_port_r + 0.8, "the Pi's ports would catch on the ring"
assert m4_square / 2 * math.sqrt(2) - screw_clear_d / 2 > board_r + 0.3, "screw would touch the display board"
assert panel_back_z - (screw_len - (seat_z - panel_back_z)) > panel_back_z - m4_hole_depth + 0.4, \
    "screw would bottom out in the panel"


def solve_depth():
    """Shortest dome (behind the panel) that keeps dome_clear over the battery corners."""
    s = math.sqrt(max(0.0, 1 - (panel_r / dome_max_r) ** 2))
    k = math.sqrt(1 - (bat_corner_r / (dome_max_r - wall)) ** 2)
    need = bat_back_z + dome_clear - panel_back_z
    lo, hi = need, 400.0
    for _ in range(80):
        T = (lo + hi) / 2
        t0 = T * s / (1 + s)
        lo, hi = (lo, T) if t0 + (T - wall - t0) * k >= need else (T, hi)
    return hi, hi * s / (1 + s)


dome_len, bulge_at = solve_depth()             # behind the panel's back face
depth = panel_back_z + dome_len                # overall, glass front to dome top
rot = math.radians(90.0 + tilt_deg)
up_y, up_z = math.sin(rot), math.cos(rot)


def height(y, z):
    return up_y * y + up_z * z


floor_top = min(height(y, z) for y, z in low_points) - foot_clear
desk = floor_top - wall


def profile(a, length, z0, steps=96):
    """Ellipse in (radius, z): widest (a) at z0, closing on the axis at length, both from the panel back.
    Sampled by angle so the points crowd in near the tip, and ends on a flat ~3 mm across:
    a profile point right on the axis meshes with a crack at the tip."""
    th0 = math.asin(-z0 / (length - z0))                  # the start, at the panel back
    pts = []
    for i in range(steps + 1):
        th = th0 + (math.pi / 2 - th0) * i / steps
        pts.append((a * math.cos(th), panel_back_z + z0 + (length - z0) * math.sin(th)))
    pts[-1] = (0.0, pts[-2][1])
    return pts


def revolve(pts):
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))


def band(h0, h1):
    return (cq.Workplane("XY").box(1000, 1000, h1 - h0, centered=(True, True, False))
            .translate((0, 0, h0)).rotate((0, 0, 0), (1, 0, 0), -(90.0 + tilt_deg)))


def world_to_body(wp):
    return wp.rotate((0, 0, 0), (1, 0, 0), -(90.0 + tilt_deg))


# ============================================================
# BODY
# ============================================================
outer = revolve([(0, panel_back_z)] + profile(dome_max_r, dome_len, bulge_at))
# 45 degree chamfer on the outer front edge: a ring minus a cone
chamfer = (cq.Workplane("XY").add(cq.Solid.makeCylinder(panel_r + 5, front_chamfer, cq.Vector(0, 0, panel_back_z - 0.01)))
           .cut(cq.Workplane("XY").add(cq.Solid.makeCone(panel_r - front_chamfer, panel_r + 0.01, front_chamfer,
                                                          cq.Vector(0, 0, panel_back_z - 0.01)))))
outer = outer.cut(chamfer)
inner = (revolve([(0, panel_back_z)] + profile(dome_max_r - wall, dome_len - wall, bulge_at))
         .intersect(cq.Workplane("XY").workplane(offset=seat_z).circle(500).extrude(depth)))
inner = inner.union(cq.Workplane("XY").workplane(offset=panel_back_z - 1).circle(ring_in_r)
                    .extrude(seat_z - panel_back_z + 1.01))
body = outer.cut(inner)

# screw bosses in the ring, behind the display board, and guide tubes to the back
bosses = (cq.Workplane("XY").workplane(offset=boss_from).pushPoints(post_xy)
          .circle(boss_d / 2).extrude(seat_z - boss_from))
tubes = (cq.Workplane("XY").workplane(offset=seat_z - 0.01).pushPoints(post_xy)
         .circle(tube_od / 2).extrude(depth))
body = body.union(bosses.union(tubes).intersect(outer))
body = body.cut(cq.Workplane("XY").workplane(offset=panel_back_z - 1).pushPoints(post_xy)
                .circle(screw_clear_d / 2).extrude(seat_z - panel_back_z + 1.01))
screw_bores = (cq.Workplane("XY").workplane(offset=seat_z).pushPoints(post_xy)
               .circle(head_clear_d / 2).extrude(depth))
body = body.cut(screw_bores)

# flat foot: cut at the desk, close the cut with a floor; the lower two bores
# run out through the floor, so cut them again (two holes in the underside)
body = body.intersect(band(desk, 1000)).union(outer.intersect(band(desk, floor_top))).cut(screw_bores)

# mic port at 3 o'clock, switch slot at 1 o'clock, cable hole low on the back, vents
body = body.cut(cq.Workplane("YZ").workplane(offset=-(dome_max_r + 3)).center(mic_y, mic_z)
                .rect(mic_port_w, mic_port_w).extrude(dome_max_r - 44).edges("|X").fillet(mic_port_r))
body = body.cut(cq.Workplane("XY").box(switch_slot_w, dome_max_r, switch_slot_h)
                .translate((switch_x, dome_max_r * 0.75, switch_z)))
h_cable = floor_top + cable_hole_d / 2 + 0.5
y_w0 = -math.sin(rot) * (depth * 0.5)
body = body.cut(world_to_body(cq.Workplane("XZ").workplane(offset=-y_w0).center(cable_x, h_cable)
                              .circle(cable_hole_d / 2).extrude(200)))
vent_ys = [s * (16.0 + i * vent_pitch) for s in (1, -1) for i in range(vent_rows)]
body = body.cut(cq.Workplane("XY").workplane(offset=bat_back_z - 18).pushPoints([(0, y) for y in vent_ys])
                .slot2D(vent_len, vent_w).extrude(depth))

# ============================================================
# FIT CHECK INTERFACE (read by fitcheck.py)
# ============================================================
FIT_PARTS = [("body", body)]
FIT_ENVELOPE = outer.intersect(band(desk, 1000)).union(
    cq.Workplane("XY").circle(panel_r).extrude(panel_back_z))      # the panel itself is the front
FIT_PRESS_FITS = []
FIT_BACK_HIDE = []
DESK = dict(tilt=tilt_deg, lift=-desk)

# ============================================================
# EXPORT (print orientation: front ring on the bed)
# ============================================================
if __name__ == "__main__":
    T = dict(tolerance=0.01, angularTolerance=0.1)
    part = body.translate((0, 0, -panel_back_z))
    # fit test: the front ring and bosses only, to screw onto the real panel before the full print
    fit_test = part.intersect(cq.Workplane("XY").circle(200).extrude(seat_z + 2 - panel_back_z))
    for name, p in (("body", part), ("fit_test", fit_test)):
        cq.exporters.export(p, f"smallclock_dome_flush_{DOME}_{name}.stl", **T)
        cq.exporters.export(p, f"smallclock_dome_flush_{DOME}_{name}.3mf", **T)
    print(f"dome flush {DOME}: Ø{2 * dome_max_r:.0f} widest {bulge_at + panel_back_z:.1f} mm behind the glass, "
          f"{depth:.1f} mm overall, front ring r {ring_in_r}..{panel_r}, screws M4x{screw_len:.0f} seated at {seat_z} mm, "
          f"tilt {tilt_deg:.0f} deg")
