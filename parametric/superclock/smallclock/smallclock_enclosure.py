"""
smallclock enclosure: round puck + back lid + desk cradle for the
Waveshare 3.4inch DSI LCD (C) with a Raspberry Pi 4B on its back.

Phase 3: final. Edge finishing on all parts; chamfers on every edge that
touches the bed (a fillet there would need support), fillets elsewhere.

How it holds together: the display drops into the shell from the back and
rests against the front lip. The lid's 4 posts land on the panel's back
around its M4 holes (75 mm square, VESA-75), and 4 M4x40 countersunk screws
go through lid and posts into the panel. The posts are 0.2 mm longer than
the gap, so tightening them squeezes the shell between glass and lid. The
shell has no bosses, so the Ø115 bore stays clear for assembly.

Body frame (shell + lid): Z=0 is the front face, +Z toward the back,
+Y is display "up", X left/right seen from the front.

Print orientation:
  shell  - front face down (lip first, no supports)
  lid    - outer face down (countersinks open onto the bed, posts grow up)
  cradle - flat bottom down (saddle is a trough, no supports)
"""
import math
import cadquery as cq

# ============================================================
# PARAMETERS - Edit these to customize the model
# ============================================================
# Display (source: Waveshare dimension drawing + vendor STEP
# vendor/3_4inch-DSI-LCD_C.stp; STEP glass front is at z=+3.95)
panel_d = 115.0         # mm - round glass/panel diameter
panel_t = 6.0           # mm - glass front to panel back (drawing "6.00"; STEP 3.95..-2.05)
active_d = 87.6         # mm - visible display area
m4_square = 75.0        # mm - panel M4 hole pattern (STEP: ±37.5, ±37.5)
m4_hole_depth = 3.5     # mm - blind M4 threads in the panel back (STEP)

# Stack behind the panel (STEP + RPi 4B mechanical drawing)
pi_standoff_top = 17.1  # mm - glass front to Pi PCB underside (STEP 3.95 - -13.15)
pi_height = 17.4        # mm - Pi PCB 1.4 + USB stack 16.0

# Screws
screw_len = 40.0        # mm - M4 countersunk (DIN 7991) overall length
thread_engage = 2.7     # mm - thread in the panel (leaves 0.8 before hole bottom)
csk_d = 8.4             # mm - countersink top diameter (M4 head 8.0 + clearance)
screw_clear_d = 4.5     # mm - M4 clearance through lid and posts

# Shell
wall = 2.4              # mm - side wall
lip_t = 1.6             # mm - front lip thickness
lip_overlap = 3.0       # mm - lip reach over the glass edge (bezel is 13.7 wide)
fit_clear = 0.4         # mm - radial clearance around the glass (PETG)
cable_notch_w = 7.0     # mm - power cable exit at 6 o'clock, back rim
cable_notch_h = 5.0     # mm - notch depth into the rim

# Lid
lid_t = 3.0             # mm - holds the countersink (head height 2.2)
post_od = 8.0           # mm - clears the driver board (checked against STEP)
post_preload = 0.2      # mm - posts longer than the gap, clamps the stack
plug_h = 2.5            # mm - locating ring that enters the bore
plug_t = 1.6            # mm - ring wall
vent_w = 2.5            # mm - vent slot width
vent_pitch = 5.5        # mm - slot spacing
vent_rows = 4           # slots per bank (one bank high, one low)
vent_len = 56.0         # mm - slot length

# Cradle (desk stand)
tilt_deg = 15.0         # deg - display leans back by this much
cradle_clear = 0.6      # mm - gap between puck and saddle
cradle_floor = 3.0      # mm - material under the puck's lowest point
cradle_wrap = 20.0      # mm - saddle height above the puck's lowest point
cradle_w = 100.0        # mm - footprint width
stop_t = 4.0            # mm - back stop behind the lid
tail_len = 28.0         # mm - low plate behind the stop (anti-tip)
tail_h = 5.0            # mm
cable_channel_w = 7.5   # mm - cable path through stop and tail
foot_d = 8.2            # mm - recesses for 8 mm stick-on bumpers
foot_depth = 1.0        # mm

# Edge finishing
front_chamfer = 1.0     # mm - shell front outer edge (bed side)
window_chamfer = 1.0    # mm - bevel around the display window (bed side)
back_round = 0.8        # mm - shell back outer edge
lid_chamfer = 1.0       # mm - lid outer edge (bed side, reads as the back edge)
cradle_corner_r = 4.0   # mm - cradle vertical corners
cradle_top_round = 1.5  # mm - cradle top edges
cradle_foot_chamfer = 0.6  # mm - cradle bottom edge, counters elephant's foot

# ============================================================
# DERIVED
# ============================================================
bore_r = panel_d / 2 + fit_clear               # 57.9
outer_r = bore_r + wall                        # 60.3
front_open_r = panel_d / 2 - lip_overlap       # 54.5
panel_back_z = lip_t + panel_t                 # 7.6, where the posts land
screw_tip_z = panel_back_z - thread_engage     # 4.9
lid_outer_z = screw_tip_z + screw_len          # 44.9, countersunk head flush here
body_depth = lid_outer_z - lid_t               # 41.9, shell length
post_len = body_depth - panel_back_z + post_preload
pi_back_z = lip_t + pi_standoff_top + pi_height
rear_gap = body_depth - pi_back_z

assert front_open_r > active_d / 2 + 1.0, "lip would cover the active area"
assert rear_gap >= 3.0, f"only {rear_gap:.1f} mm behind the Pi ports"
assert thread_engage < m4_hole_depth - 0.5, "screw would bottom out in the panel"
post_xy = [(sx * m4_square / 2, sy * m4_square / 2) for sx in (1, -1) for sy in (1, -1)]

# ============================================================
# SHELL
# ============================================================
# finish the outer edges while the body is still a plain cylinder
shell = (cq.Workplane("XY").circle(outer_r).extrude(body_depth)
         .faces("<Z").edges().chamfer(front_chamfer)
         .faces(">Z").edges().fillet(back_round))
shell = shell.cut(
    cq.Workplane("XY").circle(front_open_r).extrude(lip_t + 0.02).translate((0, 0, -0.01)))
# 45 degree bevel around the window, cut as a cone (edge selection is
# ambiguous here: every front circle is centred on the axis)
bevel = cq.Solid.makeCone(front_open_r + window_chamfer + 0.01, front_open_r,
                          window_chamfer + 0.01, cq.Vector(0, 0, -0.01))
shell = shell.cut(cq.Workplane("XY").add(bevel))
shell = shell.cut(
    cq.Workplane("XY").workplane(offset=lip_t).circle(bore_r).extrude(body_depth))
# power cable exit at 6 o'clock on the back rim
shell = shell.cut(
    cq.Workplane("XY")
    .box(cable_notch_w, wall * 3, cable_notch_h + 0.01, centered=(True, True, False))
    .translate((0, -outer_r, body_depth - cable_notch_h)))

# ============================================================
# LID  (modelled in body coords, Z from body_depth to lid_outer_z)
# ============================================================
lid = (cq.Workplane("XY").workplane(offset=body_depth)
       .circle(outer_r).extrude(lid_t)
       .faces(">Z").edges().chamfer(lid_chamfer))
# locating ring into the bore, with a gap for the cable at 6 o'clock
plug_or = bore_r - 0.3
plug = (cq.Workplane("XY").workplane(offset=body_depth - plug_h)
        .circle(plug_or).circle(plug_or - plug_t).extrude(plug_h))
plug = plug.cut(cq.Workplane("XY").box(cable_notch_w + 2, 20, 50)
                .translate((0, -plug_or, body_depth)))
lid = lid.union(plug)
# posts from the lid inner face down to the panel back
posts = (cq.Workplane("XY").workplane(offset=body_depth - post_len)
         .pushPoints(post_xy).circle(post_od / 2).extrude(post_len + 0.01))
lid = lid.union(posts)
# M4 clearance through posts + lid, countersink flush with the outer face
lid = lid.cut(cq.Workplane("XY").workplane(offset=body_depth - post_len - 1)
              .pushPoints(post_xy).circle(screw_clear_d / 2).extrude(post_len + lid_t + 2))
csk_depth = (csk_d - screw_clear_d) / 2         # 90 degree countersink
for (x, y) in post_xy:
    cone = cq.Solid.makeCone(screw_clear_d / 2, csk_d / 2, csk_depth + 0.01,
                             cq.Vector(x, y, lid_outer_z - csk_depth))
    lid = lid.cut(cq.Workplane("XY").add(cone))
# vent banks: one low (intake), one high (exhaust), clear of the posts
vent_ys = []
for bank in (1, -1):
    for i in range(vent_rows):
        vent_ys.append(bank * (14.0 + i * vent_pitch))
vents = (cq.Workplane("XY").workplane(offset=body_depth - 1)
         .pushPoints([(0, y) for y in vent_ys])
         .slot2D(vent_len, vent_w).extrude(lid_t + 2))
lid = lid.cut(vents)

# ============================================================
# CRADLE  (built in world coords: desk at Z=0, back of the clock toward -Y)
# ============================================================
# body -> world: rotate 90 deg about X (body Y->world Z, body Z->world -Y),
# then tilt the front up by tilt_deg.
rot = 90.0 + tilt_deg
ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))


def to_world(p):
    x, y, z = p
    return (x, y * ca - z * sa, y * sa + z * ca)


# lowest point of the puck is the back-bottom edge of the lid
low = to_world((0, -outer_r, lid_outer_z))
lift = cradle_floor - low[2]
front_bottom = to_world((0, -outer_r, 0))


def place(wp):
    return wp.rotate((0, 0, 0), (1, 0, 0), rot).translate((0, 0, lift))


y_front = front_bottom[1]
y_stop = low[1] - stop_t
y_tail = y_stop - tail_len
top_z = cradle_floor + cradle_wrap

# one L-shaped side profile (tall block + low tail), extruded across X,
# so the edges can be finished before any cut
profile = [(y_tail, 0), (y_front, 0), (y_front, top_z), (y_stop, top_z),
           (y_stop, tail_h), (y_tail, tail_h)]
cradle = (cq.Workplane("YZ").polyline(profile).close()
          .extrude(cradle_w / 2, both=True)
          .edges("|Z").fillet(cradle_corner_r)
          .faces(">Z").edges().fillet(cradle_top_round)
          .faces("<Z").edges().chamfer(cradle_foot_chamfer))

# saddle: the puck envelope (shell + lid) with clearance
envelope = cq.Workplane("XY").circle(outer_r + cradle_clear).extrude(lid_outer_z + cradle_clear)
cradle = cradle.cut(place(envelope))
# nothing in front of the display face
front_half = cq.Workplane("XY").box(400, 400, 400).translate((0, 0, -200))
cradle = cradle.cut(place(front_half))
# cable channel through the back stop and tail
cradle = cradle.cut(cq.Workplane("XY")
                    .box(cable_channel_w, 200, 100, centered=(True, True, False))
                    .translate((0, y_stop - 100 + 30, cradle_floor - 1.5)))
# bumper recesses on the underside
inset = 9.0
feet = [(sx * (cradle_w / 2 - inset), y) for sx in (1, -1)
        for y in (y_front - inset, y_tail + inset)]
cradle = cradle.cut(cq.Workplane("XY").pushPoints(feet)
                    .circle(foot_d / 2).extrude(foot_depth))

# ============================================================
# EXPORT (each part in its print orientation, sitting on Z=0)
# ============================================================
shell_print = shell
lid_print = lid.rotate((0, 0, 0), (0, 1, 0), 180).translate((0, 0, lid_outer_z))  # outer face on the bed
cradle_print = cradle

T = dict(tolerance=0.01, angularTolerance=0.1)
cq.exporters.export(shell_print, "smallclock_shell.stl", **T)
cq.exporters.export(lid_print, "smallclock_lid.stl", **T)
cq.exporters.export(cradle_print, "smallclock_cradle.stl", **T)
# 3MF via CadQuery's native writer (keeps cavities intact, unlike STL->3MF conversion)
for name, part in (("shell", shell_print), ("lid", lid_print), ("cradle", cradle_print)):
    cq.exporters.export(part, f"smallclock_{name}.3mf", **T)

cbb = cradle.val().BoundingBox()
print(f"shell  Ø{2*outer_r:.1f} x {body_depth:.1f} mm, rear gap behind Pi {rear_gap:.1f} mm")
print(f"lid    Ø{2*outer_r:.1f} x {lid_t:.1f} mm, 4 posts Ø{post_od:.0f} x {post_len:.1f} mm, "
      f"screws M4x{screw_len:.0f} CSK")
print(f"cradle {cbb.xlen:.1f} x {cbb.ylen:.1f} x {cbb.zlen:.1f} mm")
