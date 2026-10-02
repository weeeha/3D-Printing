"""
smallclock block: a soft wedge with the round face in it, for the Waveshare
3.4inch DSI LCD (C), Raspberry Pi 4B, SunFounder PiPower v2 and its 2S pack.
The stack is measured in fitcheck.py; the puck version is smallclock_enclosure.py.

How it holds together: the stack drops into the shell from the back, glass
into a locating ring behind the front lip. The back panel's 4 posts land on the
panel's back around its M4 holes (75 mm square, VESA-75), and 4 M4x40
countersunk screws go down wells in the posts into the panel. The posts run
along the display axis, so they lean 12 degrees off the back panel. They are
0.2 mm longer than the gap, so tightening squeezes the shell between glass and
back panel.

It stands flat: the bottom is cut level through the face's bottom edge, so the
face leans back by tilt_deg, and the back is cut vertical 4 mm behind the
battery's top corner.

Body frame: Z=0 is the front face, +Z toward the back, +Y up (the PiPower's
charge-port edge is down), the Pi's port end at -X, which is 3 o'clock seen
from the front.

Print orientation:
  shell - front face down, no supports
  back  - outer face down, posts grow up; brim on (posts up to 75 mm)
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
bat_top_back = (16.2, 66.4)    # mm - (y, z) battery's top back edge, the part nearest the back panel
pi_half_w = 28.0        # mm - Pi and PiPower are both 56 mm wide

# Screws
screw_len = 40.0        # mm - M4 countersunk (DIN 7991)
thread_engage = 2.7     # mm
csk_d = 8.4             # mm
screw_clear_d = 4.5     # mm

# Block
half = 66.0             # mm - half the face width (face is 132 mm square)
corner_r = 24.0         # mm - face corner radius
wall = 2.4              # mm
lip_t = 1.6             # mm - front lip thickness
lip_overlap = 3.0       # mm - lip reach over the glass edge
fit_clear = 0.4         # mm - radial clearance around the glass
ring_len = 8.0          # mm - locating ring around the glass, behind the lip
tilt_deg = 12.0         # deg - face leans back by this much
back_clear = 4.0        # mm - battery top corner to the back panel
back_t = 3.0            # mm - back panel thickness

# Posts (from the back panel to the panel back)
post_od = 8.0           # mm - clears the driver board
post_od_wide = 13.0     # mm - behind the driver board, carries the screw well
post_step_z = 19.0      # mm
post_preload = 0.2      # mm - posts longer than the gap, clamps the stack
well_d = 8.8            # mm

# Openings (positions as in smallclock_enclosure.py)
mic_y, mic_z = 1.0, 31.8       # mm - mic grille centre on the 3 o'clock wall
grille_d = 2.4          # mm - grille hole
grille_pitch = 4.5      # mm
grille_n = 4            # holes per side
switch_slot_w = 14.0    # mm - pen slot over the PiPower switch, top wall
switch_slot_h = 5.0
switch_x, switch_z = -33.0, 42.8
cable_notch_w = 9.0     # mm - charge cable exit, bottom edge of the back panel
cable_notch_h = 7.0
cable_x = -10.8         # mm - under the PiPower's USB-C input
vent_w = 3.0            # mm - back panel vents
vent_len = 50.0         # mm
vent_heights = [14.0, 20.0, 26.0, 32.0, -22.0, -28.0, -34.0, -40.0]   # mm above the axis, level

# Edge finishing
face_chamfer = 1.5      # mm - face edge (bed side)
window_chamfer = 1.0    # mm - bevel around the display window

# ============================================================
# DERIVED
# ============================================================
bore_r = panel_d / 2 + fit_clear               # 57.9
front_open_r = panel_d / 2 - lip_overlap       # 54.5
panel_back_z = lip_t + panel_t                 # 7.6
screw_tip_z = panel_back_z - thread_engage     # 4.9
csk_seat_z = screw_tip_z + screw_len           # 44.9

rot = math.radians(90.0 + tilt_deg)


def height(y, z):                              # above the axis, level
    return math.sin(rot) * y + math.cos(rot) * z


def aft(y, z):                                 # behind the face's centre, level
    return -math.cos(rot) * y + math.sin(rot) * z


desk = height(-half, 0.0)                      # the bottom passes through the face's bottom edge
back_in = aft(*bat_top_back) + back_clear
back_out = back_in + back_t
post_xy = [(sx * m4_square / 2, sy * m4_square / 2) for sx in (1, -1) for sy in (1, -1)]

assert front_open_r > (active_d / 2) + 1.0, "lip would cover the active area"
assert thread_engage < m4_hole_depth - 0.5, "screw would bottom out in the panel"
assert m4_square / 2 - post_od_wide / 2 > pi_half_w + 2.0, "wide posts would touch the boards"
lowest_post = min(height(y - post_od_wide / 2, (back_in + math.cos(rot) * (y - post_od_wide / 2)) / math.sin(rot))
                  for _, y in post_xy)
assert lowest_post > desk + wall + 1.0, f"bottom posts would hit the floor ({lowest_post - desk - wall:.1f} mm)"


def world_to_body(wp):
    return wp.rotate((0, 0, 0), (1, 0, 0), -(90.0 + tilt_deg))


def level_band(h0, h1):
    """Between two heights, level, as a body-frame solid."""
    return world_to_body(cq.Workplane("XY").box(1000, 1000, h1 - h0, centered=(True, True, False))
                         .translate((0, 0, h0)))


def aft_band(d0, d1):
    """Between two distances behind the face, level, as a body-frame solid."""
    return world_to_body(cq.Workplane("XY").box(1000, d1 - d0, 1000).translate((0, -(d0 + d1) / 2, 0)))


def prism(h, r, z0=0.0):
    return (cq.Workplane("XY").workplane(offset=z0).rect(2 * h, 2 * h).extrude(400 - z0)
            .edges("|Z").fillet(r))


# ============================================================
# SHELL
# ============================================================
block = (prism(half, corner_r).faces("<Z").edges().chamfer(face_chamfer)
         .intersect(level_band(desk, 500)))
shell = block.intersect(aft_band(-500, back_in))
cavity = (prism(half - wall, corner_r - wall, lip_t)
          .intersect(level_band(desk + wall, 500)).intersect(aft_band(-500, back_in + 1)))
shell = shell.cut(cavity)
shell = shell.cut(cq.Workplane("XY").circle(front_open_r).extrude(lip_t + 0.02).translate((0, 0, -0.01)))
shell = shell.cut(cq.Workplane("XY").add(cq.Solid.makeCone(front_open_r + window_chamfer + 0.01, front_open_r,
                                                            window_chamfer + 0.01, cq.Vector(0, 0, -0.01))))
# locating ring around the glass, grows off the back of the lip
shell = shell.union(cq.Workplane("XY").workplane(offset=lip_t - 0.01)
                    .circle(bore_r + wall).circle(bore_r).extrude(ring_len))
# mic grille on the 3 o'clock wall
grid = [(mic_y + (i - (grille_n - 1) / 2) * grille_pitch, mic_z + (j - (grille_n - 1) / 2) * grille_pitch)
        for i in range(grille_n) for j in range(grille_n)]
shell = shell.cut(cq.Workplane("YZ").workplane(offset=-(half + 1)).pushPoints(grid)
                  .circle(grille_d / 2).extrude(wall + 2))
# pen slot over the PiPower switch
shell = shell.cut(cq.Workplane("XY").box(switch_slot_w, 20, switch_slot_h).translate((switch_x, half, switch_z)))

# ============================================================
# BACK PANEL  (with the posts)
# ============================================================
back = block.intersect(aft_band(back_in, back_out))
narrow = (cq.Workplane("XY").workplane(offset=panel_back_z - post_preload).pushPoints(post_xy)
          .circle(post_od / 2).extrude(post_step_z - panel_back_z + post_preload + 0.01))
wide = (cq.Workplane("XY").workplane(offset=post_step_z).pushPoints(post_xy)
        .circle(post_od_wide / 2).extrude(200))
back = back.union(narrow.union(wide).intersect(aft_band(-500, back_in + 0.5)))
csk_depth = (csk_d - screw_clear_d) / 2
back = back.cut(cq.Workplane("XY").workplane(offset=panel_back_z - 1).pushPoints(post_xy)
                .circle(screw_clear_d / 2).extrude(csk_seat_z - panel_back_z + 1))
for x, y in post_xy:
    back = back.cut(cq.Workplane("XY").add(
        cq.Solid.makeCone(screw_clear_d / 2, csk_d / 2, csk_depth + 0.01, cq.Vector(x, y, csk_seat_z - csk_depth))))
back = back.cut(cq.Workplane("XY").workplane(offset=csk_seat_z).pushPoints(post_xy)
                .circle(well_d / 2).extrude(200))
# vents, level slots through the panel
vents = (cq.Workplane("XZ").workplane(offset=back_in - 2).pushPoints([(0, h) for h in vent_heights])
         .slot2D(vent_len, vent_w).extrude(back_t + 4))
back = back.cut(world_to_body(vents))
# charge cable notch at the bottom edge, also through the shell's back edge
notch = world_to_body(cq.Workplane("XY").box(cable_notch_w, back_t + 8, cable_notch_h + 1, centered=(True, True, False))
                      .translate((cable_x, -(back_in + back_out) / 2 + 2, desk - 1)))
back, shell = back.cut(notch), shell.cut(notch)

# ============================================================
# FIT CHECK INTERFACE (read by fitcheck.py)
# ============================================================
FIT_PARTS = [("shell", shell), ("back", back)]
FIT_ENVELOPE = block.intersect(aft_band(-500, back_out))
FIT_PRESS_FITS = []
FIT_BACK_HIDE = ["back"]
DESK = dict(tilt=tilt_deg, lift=-desk)

# ============================================================
# EXPORT (each part in its print orientation, sitting on Z=0)
# ============================================================
if __name__ == "__main__":
    shell_print = shell                                         # face on the bed
    back_print = (back.rotate((0, 0, 0), (1, 0, 0), 90.0 + tilt_deg)     # stand it up
                  .rotate((0, 0, 0), (1, 0, 0), 90.0)                    # outer face down
                  .translate((0, 0, back_out)))
    T = dict(tolerance=0.01, angularTolerance=0.1)
    for name, part in (("shell", shell_print), ("back", back_print)):
        cq.exporters.export(part, f"smallclock_block_{name}.stl", **T)
        cq.exporters.export(part, f"smallclock_block_{name}.3mf", **T)
    sb, bb = shell.val().BoundingBox(), back_print.val().BoundingBox()
    print(f"shell  {2*half:.0f} x {2*half:.0f} mm face, back {back_out:.1f} mm behind the face centre, "
          f"print height {sb.zmax:.1f} mm")
    print(f"back   {bb.xlen:.1f} x {bb.ylen:.1f} mm, posts to {bb.zmax:.1f} mm, screws M4x{screw_len:.0f} CSK "
          f"seated at {csk_seat_z:.1f} mm")
