"""
smallclock pebble: one-piece domed body + front bezel ring for the Waveshare
3.4inch DSI LCD (C), Raspberry Pi 4B, SunFounder PiPower v2 and its 2S pack.
The stack is measured in fitcheck.py; the puck version is smallclock_enclosure.py.

How it holds together: the body is one piece and open at the front. The whole
stack slides in from the front until the panel's back lands on four posts that
grow out of the wall (75 mm square, VESA-75). 4 M4x40 countersunk screws go down
wells in the dome, through the posts, into the panel's blind M4 holes and pull
it onto the posts. The bezel ring presses over a rabbet on the body's front edge
and covers the glass rim. The dome has no seam.

It stands on its own: a flat foot is cut under the body so the face leans back
by tilt_deg, with a floor closing the cut 3 mm under the lowest hardware.

Body frame: Z=0 is the front face (bezel front), +Z toward the back, +Y up
(the PiPower's charge-port edge is down), the Pi's port end at -X, which is
3 o'clock seen from the front.

Print orientation:
  body  - front edge down; tree supports inside the dome only, they come out through the front
  bezel - front face down
"""
import math
import cadquery as cq

# ============================================================
# PARAMETERS - Edit these to customize the model
# ============================================================
# Display (vendor/3_4inch-DSI-LCD_C.stp, as in smallclock_enclosure.py)
panel_d = 115.0         # mm - round glass/panel diameter
panel_t = 6.0           # mm - glass front to panel back
active_d = 87.6         # mm - visible display area
m4_square = 75.0        # mm - panel M4 hole pattern
m4_hole_depth = 3.5     # mm - blind M4 threads in the panel back

# Measured stack (fitcheck.py), body frame
stack_back = 64.8       # mm - glass front to the back of the battery
bat_corner_r = 45.8     # mm - battery's farthest corner from the axis (74 x 38 pack, off-centre)
pi_half_w = 28.0        # mm - Pi and PiPower are both 56 mm wide
low_points = [(-57.5, 7.6),    # (y, z) bottom of the panel at its back face
              (-46.8, 46.6)]   # bottom of the right-angle charge plug

# Screws
screw_len = 40.0        # mm - M4 countersunk (DIN 7991)
thread_engage = 2.7     # mm - thread in the panel (leaves 0.8 before hole bottom)
csk_d = 8.4             # mm - countersink top diameter
screw_clear_d = 4.5     # mm - M4 clearance

# Body
wall = 2.4              # mm
lip_t = 1.6             # mm - bezel lip thickness, the glass sits right behind it
lip_overlap = 3.0       # mm - lip reach over the glass edge
fit_clear = 0.4         # mm - radial clearance around the glass
dome_start = 44.0       # mm - cylinder turns into the dome here
dome_n = 3.0            # superellipse exponent: 2 is an ellipse, higher is boxier
dome_clear = 2.0        # mm - inside the dome, over the battery's back corners

# Bezel ring
bezel_skirt = 4.0       # mm - skirt length over the body's front edge
rabbet = 1.2            # mm - skirt thickness; the body's outer wall steps in by this
press_fit = 0.05        # mm - skirt interference (glue it as well)

# Posts (from the wall to the panel back)
post_od = 8.0           # mm - clears the driver board (as in the puck)
post_od_wide = 13.0     # mm - behind the driver board, carries the screw well
post_step_z = 19.0      # mm - where the post widens
web_w = 4.0             # mm - web tying the narrow post to the wall
well_d = 8.8            # mm - head and screwdriver access down to the seat

# Stand
tilt_deg = 15.0         # deg - face leans back by this much
foot_clear = 3.0        # mm - floor to the lowest hardware

# Openings (positions as in smallclock_enclosure.py)
mic_port_w = 24.0       # mm - square port at 3 o'clock, the mic plugs in through it last
mic_port_r = 3.0
mic_y, mic_z = 1.0, 31.8
switch_slot_w = 14.0    # mm - pen slot for the PiPower switch, about 1 o'clock
switch_slot_h = 5.0
switch_x, switch_z = -33.0, 42.8
cable_hole_d = 7.0      # mm - charge cable exit, low on the back, just above the floor
cable_x = -8.0          # mm
vent_w = 3.0            # mm - slot width
vent_len = 40.0         # mm
vent_pitch = 6.5        # mm
vent_rows = 3           # slots per bank, one bank high on the dome, one low

# Edge finishing
front_chamfer = 1.0     # mm - bezel front edge (bed side)
window_chamfer = 1.0    # mm - bevel around the display window

# ============================================================
# DERIVED
# ============================================================
bore_r = panel_d / 2 + fit_clear               # 57.9
outer_r = bore_r + wall                        # 60.3
front_open_r = panel_d / 2 - lip_overlap       # 54.5
panel_back_z = lip_t + panel_t                 # 7.6, post seats
screw_tip_z = panel_back_z - thread_engage     # 4.9
csk_seat_z = screw_tip_z + screw_len           # 44.9, head flush here, inside the post
bat_back_z = lip_t + stack_back                # 66.4

k = (1 - (bat_corner_r / bore_r) ** dome_n) ** (1 / dome_n)
dome_b_in = (bat_back_z + dome_clear - dome_start) / k
dome_b_out = dome_b_in + wall
depth = dome_start + dome_b_out                # overall, bezel front to dome top

rot = math.radians(90.0 + tilt_deg)
up_y, up_z = math.sin(rot), math.cos(rot)      # world "up", in body coordinates


def height(y, z):
    return up_y * y + up_z * z


floor_top = min(height(y, z) for y, z in low_points) - foot_clear
desk = floor_top - wall                        # the foot, in height units
post_xy = [(sx * m4_square / 2, sy * m4_square / 2) for sx in (1, -1) for sy in (1, -1)]

assert front_open_r > active_d / 2 + 1.0, "lip would cover the active area"
assert thread_engage < m4_hole_depth - 0.5, "screw would bottom out in the panel"
assert csk_seat_z < dome_start + dome_b_in * 0.5, "screw seat would sit in the dome wall"
assert m4_square / 2 - post_od_wide / 2 > pi_half_w + 2.0, "wide posts would touch the boards"


def superellipse(a, b, z0, steps=60):
    pts = []
    for i in range(1, steps + 1):
        t = i / steps * math.pi / 2
        pts.append((a * math.cos(t) ** (2 / dome_n), z0 + b * math.sin(t) ** (2 / dome_n)))
    pts[-1] = (0.0, pts[-2][1])     # end on a tiny flat: a point right on the axis meshes with a crack at the tip
    return pts


def revolve(pts):
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))


def band(h0, h1):
    """Everything between two heights above the desk, as a body-frame solid."""
    return (cq.Workplane("XY").box(1000, 1000, h1 - h0, centered=(True, True, False))
            .translate((0, 0, h0)).rotate((0, 0, 0), (1, 0, 0), -(90.0 + tilt_deg)))


def world_to_body(wp):
    return wp.rotate((0, 0, 0), (1, 0, 0), -(90.0 + tilt_deg))


# ============================================================
# BODY
# ============================================================
skirt_end = lip_t + bezel_skirt
outer = revolve([(0, lip_t), (outer_r - rabbet, lip_t), (outer_r - rabbet, skirt_end),
                 (outer_r, skirt_end), (outer_r, dome_start)]
                + superellipse(outer_r, dome_b_out, dome_start))
inner = revolve([(0, lip_t - 1), (bore_r, lip_t - 1), (bore_r, dome_start)]
                + superellipse(bore_r, dome_b_in, dome_start))
body = outer.cut(inner)

# posts: narrow past the driver board and webbed to the wall, wide behind it
narrow = (cq.Workplane("XY").workplane(offset=panel_back_z).pushPoints(post_xy)
          .circle(post_od / 2).extrude(post_step_z - panel_back_z + 0.01))
for x, y in post_xy:
    a = math.degrees(math.atan2(y, x))
    web = (cq.Workplane("XY").box(outer_r - math.hypot(x, y), web_w, post_step_z - panel_back_z,
                                  centered=(False, True, False))
           .translate((math.hypot(x, y), 0, panel_back_z)).rotate((0, 0, 0), (0, 0, 1), a))
    narrow = narrow.union(web)
wide = (cq.Workplane("XY").workplane(offset=post_step_z).pushPoints(post_xy)
        .circle(post_od_wide / 2).extrude(depth))
body = body.union(narrow.union(wide).intersect(outer))
# M4 clearance up to the seat, 90 degree countersink, then the well out through the dome
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

# mic port at 3 o'clock, square so its top prints as a short flat bridge
body = body.cut(cq.Workplane("YZ").workplane(offset=-(outer_r + 2)).center(mic_y, mic_z)
                .rect(mic_port_w, mic_port_w).extrude(wall + 6).edges("|X").fillet(mic_port_r))
# PiPower switch slot through the top of the wall
body = body.cut(cq.Workplane("XY").box(switch_slot_w, outer_r, switch_slot_h)
                .translate((switch_x, outer_r * 0.75, switch_z)))
# charge cable exit: straight back out of the dome, just above the floor
h_cable = floor_top + cable_hole_d / 2 + 0.5
y_w0 = -math.sin(rot) * dome_start             # world y of the dome start, on the axis
cable = (cq.Workplane("XZ").workplane(offset=-y_w0).center(cable_x, h_cable)
         .circle(cable_hole_d / 2).extrude(80))     # "XZ" extrudes toward -Y, the back
body = body.cut(world_to_body(cable))
# vents through the dome: one bank high (exhaust), one low (intake)
vent_ys = [s * (16.0 + i * vent_pitch) for s in (1, -1) for i in range(vent_rows)]
body = body.cut(cq.Workplane("XY").workplane(offset=dome_start + 4).pushPoints([(0, y) for y in vent_ys])
                .slot2D(vent_len, vent_w).extrude(depth))

# ============================================================
# BEZEL RING
# ============================================================
bezel = (cq.Workplane("XY").circle(outer_r).extrude(lip_t)
         .faces("<Z").edges().chamfer(front_chamfer))
bezel = bezel.union(cq.Workplane("XY").workplane(offset=lip_t)
                    .circle(outer_r).circle(outer_r - rabbet - press_fit).extrude(bezel_skirt))
bezel = bezel.cut(cq.Workplane("XY").circle(front_open_r).extrude(lip_t + 0.02).translate((0, 0, -0.01)))
bezel = bezel.cut(cq.Workplane("XY").add(cq.Solid.makeCone(front_open_r + window_chamfer + 0.01, front_open_r,
                                                            window_chamfer + 0.01, cq.Vector(0, 0, -0.01))))

# ============================================================
# FIT CHECK INTERFACE (read by fitcheck.py)
# ============================================================
FIT_PARTS = [("body", body), ("bezel", bezel)]
FIT_ENVELOPE = outer.intersect(band(desk, 1000)).union(cq.Workplane("XY").circle(outer_r).extrude(skirt_end))
FIT_PRESS_FITS = [("body", "bezel")]
FIT_BACK_HIDE = []
DESK = dict(tilt=tilt_deg, lift=-desk)

# ============================================================
# EXPORT (each part in its print orientation, sitting on Z=0)
# ============================================================
if __name__ == "__main__":
    body_print = body.translate((0, 0, -lip_t))     # front edge on the bed
    bezel_print = bezel                             # front face on the bed
    # fit test: the body's first 11 mm (rabbet, bore, post seats), to try the panel and the bezel on
    fit_test = body_print.intersect(cq.Workplane("XY").circle(200).extrude(11.0))
    T = dict(tolerance=0.01, angularTolerance=0.1)
    for name, part in (("body", body_print), ("bezel", bezel_print), ("fit_test", fit_test)):
        cq.exporters.export(part, f"smallclock_pebble_{name}.stl", **T)
        cq.exporters.export(part, f"smallclock_pebble_{name}.3mf", **T)
    bb = body.val().BoundingBox()
    print(f"body   Ø{2*outer_r:.1f} x {depth:.1f} mm deep, foot {abs(desk - height(-outer_r, 0)):.1f} mm under the rim, "
          f"tilt {tilt_deg:.0f} deg, print height {bb.zmax - lip_t:.1f} mm")
    print(f"bezel  Ø{2*outer_r:.1f} x {lip_t + bezel_skirt:.1f} mm, screws M4x{screw_len:.0f} CSK "
          f"seated at {csk_seat_z:.1f} mm")
