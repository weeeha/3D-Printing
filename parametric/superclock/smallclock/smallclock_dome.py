"""
smallclock dome: Nick's "fixed body" dome (clock_body_fixed.stl, the 5-inch
fastclock body) resized around the smallclock stack: Waveshare 3.4inch DSI LCD
(C), Raspberry Pi 4B, SunFounder PiPower v2 and its 2S pack (fitcheck.py).

What carries over from the original, measured off its mesh: an ellipsoidal
dome whose rim is near its widest point, the face tilted 41 degrees back, a
flat foot cut under it, and screw posts running straight back from the panel.
What the hardware forces: the 74 mm battery sits right where the dome
narrows, so the dome is either deeper or wider behind the face than a
straight scale of the original. DOME picks how:

    egg       rim stays the widest point, the dome gets deep   (Ø121 x ~108)
    balanced  slight bulge behind the face                      (Ø132 x ~90)
    wide      bulges to Ø140, closest to the original's ratio  (Ø140 x ~85)

    DOME=wide ~/ClaudeCode\\ Projects/cad-skill/.venv/bin/python smallclock_dome.py

How it holds together (same as smallclock_pebble.py): the body is one piece
and open at the front. The stack slides in from the front until the panel's
back lands on four posts that grow out of the wall (75 mm square, VESA-75).
4 M4x40 countersunk screws go down wells in the dome into the panel's blind M4
holes. The bezel ring presses over a rabbet on the front edge.

Body frame: Z=0 is the front face (bezel front), +Z toward the back, +Y up
(the PiPower's charge-port edge is down), the Pi's port end at -X, which is
3 o'clock seen from the front.

Print orientation:
  body  - front edge down; tree supports inside the dome and under the post seats
  bezel - front face down
"""
import math
import os
import cadquery as cq

# ============================================================
# PARAMETERS - Edit these to customize the model
# ============================================================
DOME = os.environ.get("DOME", "balanced")
dome_max_r = {"egg": 60.3, "balanced": 66.0, "wide": 70.0}[DOME]   # mm - widest outer radius

# Display (vendor/3_4inch-DSI-LCD_C.stp, as in smallclock_enclosure.py)
panel_d = 115.0         # mm - round glass/panel diameter
panel_t = 6.0           # mm - glass front to panel back
active_d = 87.6         # mm - visible display area
m4_square = 75.0        # mm - panel M4 hole pattern
m4_hole_depth = 3.5     # mm - blind M4 threads in the panel back

# Measured stack (fitcheck.py), body frame
stack_back = 64.8       # mm - glass front to the back of the battery
bat_corner_r = 45.8     # mm - battery's farthest corner from the axis
pi_half_w = 28.0        # mm - Pi and PiPower are both 56 mm wide
low_points = [(-57.5, 7.6),    # (y, z) bottom of the panel at its back face
              (-46.8, 46.6),   # bottom of the right-angle charge plug
              (-28.0, 46.4),   # PiPower bottom edge, back face
              (-21.8, 66.4)]   # battery bottom back edge

# Screws
screw_len = 40.0        # mm - M4 countersunk (DIN 7991)
thread_engage = 2.7     # mm
csk_d = 8.4             # mm
screw_clear_d = 4.5     # mm

# Body
wall = 2.4              # mm
lip_t = 1.6             # mm - bezel lip thickness, the glass sits right behind it
lip_overlap = 3.0       # mm
fit_clear = 0.4         # mm
dome_clear = 2.0        # mm - inside the dome, over the battery's back corners
bore_depth = 12.0       # mm - straight bore behind the lip for the panel and driver board

# Bezel ring
bezel_skirt = 4.0       # mm
rabbet = 1.2            # mm
press_fit = 0.05        # mm

# Posts
post_od = 8.0           # mm
post_od_wide = 13.0     # mm
post_step_z = 19.0      # mm
web_w = 4.0             # mm
well_d = 8.8            # mm

# Stand (the original stands at 41 degrees; measured off clock_body_fixed.stl)
tilt_deg = 41.0         # deg - face leans back by this much
foot_clear = 3.0        # mm - floor to the lowest hardware

# Openings (positions as in smallclock_enclosure.py)
mic_port_w = 24.0
mic_port_r = 3.0
mic_y, mic_z = 1.0, 31.8
switch_slot_w = 14.0
switch_slot_h = 5.0
switch_x, switch_z = -33.0, 42.8
cable_hole_d = 7.0
cable_x = -8.0
vent_w = 3.0
vent_len = 36.0
vent_pitch = 6.5
vent_rows = 3

front_chamfer = 1.0
window_chamfer = 1.0

# ============================================================
# DERIVED
# ============================================================
bore_r = panel_d / 2 + fit_clear               # 57.9
rim_r = bore_r + wall                          # 60.3, outer radius at the face
front_open_r = panel_d / 2 - lip_overlap       # 54.5
panel_back_z = lip_t + panel_t                 # 7.6
screw_tip_z = panel_back_z - thread_engage     # 4.9
csk_seat_z = screw_tip_z + screw_len           # 44.9
bat_back_z = lip_t + stack_back                # 66.4


def solve_depth():
    """Shortest dome that keeps the inner surface dome_clear behind the battery corners."""
    s = math.sqrt(max(0.0, 1 - (rim_r / dome_max_r) ** 2))
    a_in = dome_max_r - wall
    k = math.sqrt(1 - (bat_corner_r / a_in) ** 2)
    need = bat_back_z + dome_clear
    # outer: rho(t) = A sqrt(1 - ((t - t0) / (T - t0))^2), rho(0) = rim_r  ->  t0 = T s / (1 + s)
    # inner: same t0, depth T - wall, radius A - wall
    lo, hi = need, 400.0
    for _ in range(80):
        T = (lo + hi) / 2
        t0 = T * s / (1 + s)
        reach = t0 + (T - wall - t0) * k
        lo, hi = (lo, T) if reach >= need else (T, hi)
    return hi, hi * s / (1 + s)


depth, bulge_at = solve_depth()                # overall depth behind the face, where it is widest
rot = math.radians(90.0 + tilt_deg)
up_y, up_z = math.sin(rot), math.cos(rot)


def height(y, z):
    return up_y * y + up_z * z


floor_top = min(height(y, z) for y, z in low_points) - foot_clear
desk = floor_top - wall
post_xy = [(sx * m4_square / 2, sy * m4_square / 2) for sx in (1, -1) for sy in (1, -1)]

assert front_open_r > active_d / 2 + 1.0, "lip would cover the active area"
assert thread_engage < m4_hole_depth - 0.5, "screw would bottom out in the panel"
assert m4_square / 2 - post_od_wide / 2 > pi_half_w + 2.0, "wide posts would touch the boards"


def profile(a, depth_, z0, steps=72):
    """Ellipse in (radius, depth): widest (a) at z0, closing on the axis at depth_."""
    pts = []
    for i in range(steps + 1):
        z = depth_ * i / steps
        u = (z - z0) / (depth_ - z0)
        pts.append((a * math.sqrt(max(0.0, 1 - u * u)), z))
    pts[-1] = (0.0, depth_)
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
outer_pts = profile(dome_max_r, depth, bulge_at)
outer = revolve([(0, 0)] + outer_pts).intersect(
    cq.Workplane("XY").workplane(offset=lip_t).circle(500).extrude(depth))          # body starts behind the lip
skirt_end = lip_t + bezel_skirt
outer = outer.cut(cq.Workplane("XY").workplane(offset=lip_t - 0.01)
                  .circle(500).circle(rim_r - rabbet).extrude(bezel_skirt + 0.01))  # rabbet for the bezel skirt
inner = revolve([(0, 0)] + profile(dome_max_r - wall, depth - wall, bulge_at))
inner = inner.union(cq.Workplane("XY").workplane(offset=lip_t - 1).circle(bore_r).extrude(bore_depth + 1))
body = outer.cut(inner)

narrow = (cq.Workplane("XY").workplane(offset=panel_back_z).pushPoints(post_xy)
          .circle(post_od / 2).extrude(post_step_z - panel_back_z + 0.01))
for x, y in post_xy:
    a = math.degrees(math.atan2(y, x))
    web = (cq.Workplane("XY").box(rim_r + 10 - math.hypot(x, y), web_w, post_step_z - panel_back_z,
                                  centered=(False, True, False))
           .translate((math.hypot(x, y), 0, panel_back_z)).rotate((0, 0, 0), (0, 0, 1), a))
    narrow = narrow.union(web)
wide = (cq.Workplane("XY").workplane(offset=post_step_z).pushPoints(post_xy)
        .circle(post_od_wide / 2).extrude(depth))
body = body.union(narrow.union(wide).intersect(outer).cut(
    cq.Workplane("XY").workplane(offset=lip_t - 1).circle(bore_r).extrude(panel_back_z - lip_t + 1)))
csk_depth = (csk_d - screw_clear_d) / 2
body = body.cut(cq.Workplane("XY").workplane(offset=panel_back_z - 1).pushPoints(post_xy)
                .circle(screw_clear_d / 2).extrude(csk_seat_z - panel_back_z + 1))
for x, y in post_xy:
    body = body.cut(cq.Workplane("XY").add(
        cq.Solid.makeCone(screw_clear_d / 2, csk_d / 2, csk_depth + 0.01, cq.Vector(x, y, csk_seat_z - csk_depth))))
body = body.cut(cq.Workplane("XY").workplane(offset=csk_seat_z).pushPoints(post_xy)
                .circle(well_d / 2).extrude(depth))

# flat foot: cut at the desk, close the cut with a floor
body = body.intersect(band(desk, 1000)).union(outer.intersect(band(desk, floor_top)))

body = body.cut(cq.Workplane("YZ").workplane(offset=-(dome_max_r + 3)).center(mic_y, mic_z)
                .rect(mic_port_w, mic_port_w).extrude(dome_max_r - 50 + 6).edges("|X").fillet(mic_port_r))
body = body.cut(cq.Workplane("XY").box(switch_slot_w, dome_max_r, switch_slot_h)
                .translate((switch_x, dome_max_r * 0.75, switch_z)))
h_cable = floor_top + cable_hole_d / 2 + 0.5
y_w0 = -math.sin(rot) * (depth * 0.5)
cable = (cq.Workplane("XZ").workplane(offset=-y_w0).center(cable_x, h_cable)
         .circle(cable_hole_d / 2).extrude(200))
body = body.cut(world_to_body(cable))
vent_ys = [s * (16.0 + i * vent_pitch) for s in (1, -1) for i in range(vent_rows)]
body = body.cut(cq.Workplane("XY").workplane(offset=bat_back_z - 18).pushPoints([(0, y) for y in vent_ys])
                .slot2D(vent_len, vent_w).extrude(depth))

# ============================================================
# BEZEL RING
# ============================================================
bezel = (cq.Workplane("XY").circle(rim_r).extrude(lip_t)
         .faces("<Z").edges().chamfer(front_chamfer))
bezel = bezel.union(cq.Workplane("XY").workplane(offset=lip_t)
                    .circle(rim_r).circle(rim_r - rabbet - press_fit).extrude(bezel_skirt))
bezel = bezel.cut(cq.Workplane("XY").circle(front_open_r).extrude(lip_t + 0.02).translate((0, 0, -0.01)))
bezel = bezel.cut(cq.Workplane("XY").add(cq.Solid.makeCone(front_open_r + window_chamfer + 0.01, front_open_r,
                                                            window_chamfer + 0.01, cq.Vector(0, 0, -0.01))))

# ============================================================
# FIT CHECK INTERFACE (read by fitcheck.py)
# ============================================================
FIT_PARTS = [("body", body), ("bezel", bezel)]
FIT_ENVELOPE = outer.intersect(band(desk, 1000)).union(cq.Workplane("XY").circle(rim_r).extrude(skirt_end))
FIT_PRESS_FITS = [("body", "bezel")]
FIT_BACK_HIDE = []
DESK = dict(tilt=tilt_deg, lift=-desk)

# ============================================================
# EXPORT (each part in its print orientation, sitting on Z=0)
# ============================================================
if __name__ == "__main__":
    T = dict(tolerance=0.01, angularTolerance=0.1)
    for name, part in (("body", body.translate((0, 0, -lip_t))), ("bezel", bezel)):
        cq.exporters.export(part, f"smallclock_dome_{DOME}_{name}.stl", **T)
        cq.exporters.export(part, f"smallclock_dome_{DOME}_{name}.3mf", **T)
    print(f"dome {DOME}: Ø{2 * dome_max_r:.0f} widest at {bulge_at:.1f} mm, {depth:.1f} mm deep behind the face, "
          f"rim Ø{2 * rim_r:.1f}, tilt {tilt_deg:.0f} deg")
