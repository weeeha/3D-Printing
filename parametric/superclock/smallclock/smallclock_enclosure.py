"""
smallclock enclosure: round puck + back lid + desk cradle for the
Waveshare 3.4inch DSI LCD (C) with a Raspberry Pi 4B on its back, and a
SunFounder PiPower v2 UPS with its 2S pack behind the Pi.

Phase 3: final. Edge finishing on all parts; chamfers on every edge that
touches the bed (a fillet there would need support), fillets elsewhere.

How it holds together: the display drops into the shell from the back and
rests against the front lip. The lid's 4 posts land on the panel's back
around its M4 holes (75 mm square, VESA-75), and 4 M4x40 countersunk screws
go down wells in the posts into the panel; each head seats at the bottom of
its well, 40 mm from the panel. The posts are 0.2 mm longer than the gap, so
tightening them squeezes the shell between glass and lid. The shell has no
bosses, so the Ø115 bore stays clear for assembly.

The shell depth comes from the measured stack (fitcheck.py), not from the
screw length: display, Pi, PiPower on 24.5 mm spacers, battery at 64.8 mm.

Body frame (shell + lid): Z=0 is the front face, +Z toward the back,
+Y is display "up" (the PiPower's charge-port edge is down), and the Pi's
port end is at -X, which is 3 o'clock seen from the front.

Print orientation:
  shell  - front face down (lip first, no supports)
  lid    - outer face down (screw wells open onto the bed, posts grow up)
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
pi_half_w = 28.0        # mm - Pi and PiPower are both 56 mm wide, centred on the M4 square

# Power stack behind the Pi (measured 2026-10-01, see fitcheck.py): PiPower v2
# on 24.5 mm spacers (photo, Ethernet jack as ruler), 2S pack taped to its back
stack_back = 64.8       # mm - glass front to the back of the battery
rear_clear = 5.0        # mm - room behind the battery for the 5V dupont leads

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

# USB mic (SuziePi B0CYM618H7, 23 x 20 x 5 mm) in the outer port of the
# USB3 stack. Its tip ends 0.6 mm inside the bore, so the port goes all the
# way through and the mic plugs in last, through it.
mic_port_w = 24.0       # mm - square port, head Ø20 + clearance
mic_port_r = 3.0        # mm - port corner radius
mic_y = 1.0             # mm - port centre, height (vendor STEP + Pi STEP)
mic_z = 31.8            # mm - port centre, behind the front face

# PiPower ON/OFF slide switch, on the board's top edge, 18 mm inside the
# wall: a pen tip through this slot pushes it either way
switch_slot_w = 14.0    # mm - along the switch travel
switch_slot_h = 5.0     # mm
switch_x = -33.0        # mm - switch centre (SunFounder drawing)
switch_z = 42.8         # mm - behind the front face

# Lid
lid_t = 3.0             # mm - lid plate
post_od = 8.0           # mm - clears the driver board (checked against STEP)
post_od_wide = 13.0     # mm - behind the driver board, carries the screw well
post_step_z = 19.0      # mm - where the post widens (driver board ends at 18.2)
well_d = 8.8            # mm - head and screwdriver access down to the seat
post_wall_gap = 0.4     # mm - wide posts stop this short of the bore so the lid slides in
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
csk_seat_z = screw_tip_z + screw_len           # 44.9, countersunk head flush here, inside the post
body_depth = lip_t + stack_back + rear_clear   # 71.4, shell length
lid_outer_z = body_depth + lid_t               # 74.4
post_len = body_depth - panel_back_z + post_preload
pi_back_z = lip_t + pi_standoff_top + pi_height
rear_gap = body_depth - (lip_t + stack_back)   # behind the battery

assert front_open_r > active_d / 2 + 1.0, "lip would cover the active area"
assert rear_gap >= 3.0, f"only {rear_gap:.1f} mm behind the battery"
assert thread_engage < m4_hole_depth - 0.5, "screw would bottom out in the panel"
assert csk_seat_z < body_depth - 5.0, "screw seat would sit in the lid plate"
assert m4_square / 2 - post_od_wide / 2 > pi_half_w + 2.0, "wide posts would touch the boards"
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
# mic port at 3 o'clock, square so its top edge prints as a short flat bridge
mic_port = (cq.Workplane("YZ").workplane(offset=-(outer_r + 2))
            .center(mic_y, mic_z).rect(mic_port_w, mic_port_w).extrude(wall + 6)
            .edges("|X").fillet(mic_port_r))
shell = shell.cut(mic_port)
# PiPower switch slot, through the top of the wall
shell = shell.cut(
    cq.Workplane("XY")
    .box(switch_slot_w, outer_r, switch_slot_h)
    .translate((switch_x, outer_r * 0.75, switch_z)))

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
# posts from the lid inner face down to the panel back: narrow where they
# pass the driver board, wide behind it to carry the screw well
post_tip_z = body_depth - post_len
narrow = (cq.Workplane("XY").workplane(offset=post_tip_z)
          .pushPoints(post_xy).circle(post_od / 2).extrude(post_step_z - post_tip_z + 0.01))
wide = (cq.Workplane("XY").workplane(offset=post_step_z)
        .pushPoints(post_xy).circle(post_od_wide / 2).extrude(body_depth - post_step_z + 0.01)
        .intersect(cq.Workplane("XY").circle(bore_r - post_wall_gap).extrude(lid_outer_z)))
lid = lid.union(narrow).union(wide)
# M4 clearance from the post tip to the seat, 90 degree countersink at the
# seat, then the well up through the lid for the head and the screwdriver
csk_depth = (csk_d - screw_clear_d) / 2
lid = lid.cut(cq.Workplane("XY").workplane(offset=post_tip_z - 1)
              .pushPoints(post_xy).circle(screw_clear_d / 2).extrude(csk_seat_z - post_tip_z + 1))
for (x, y) in post_xy:
    cone = cq.Solid.makeCone(screw_clear_d / 2, csk_d / 2, csk_depth + 0.01,
                             cq.Vector(x, y, csk_seat_z - csk_depth))
    lid = lid.cut(cq.Workplane("XY").add(cone))
lid = lid.cut(cq.Workplane("XY").workplane(offset=csk_seat_z)
              .pushPoints(post_xy).circle(well_d / 2).extrude(lid_outer_z - csk_seat_z + 1))
# the well leaves a hairline on the bore side; open it into a channel up to the
# plug ring (the shell wall closes it once the lid is in)
for (x, y) in post_xy:
    chan = (cq.Workplane("XY")
            .box(10, well_d * 0.8, body_depth - plug_h - csk_seat_z, centered=(False, True, False))
            .translate((math.hypot(x, y), 0, csk_seat_z))
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(math.atan2(y, x))))
    lid = lid.cut(chan)
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
print(f"shell  Ø{2*outer_r:.1f} x {body_depth:.1f} mm, rear gap behind battery {rear_gap:.1f} mm")
print(f"lid    Ø{2*outer_r:.1f} x {lid_t:.1f} mm, 4 posts Ø{post_od_wide:.0f}/{post_od:.0f} x {post_len:.1f} mm, "
      f"screws M4x{screw_len:.0f} CSK seated {lid_outer_z - csk_seat_z:.1f} mm down the wells")
print(f"cradle {cbb.xlen:.1f} x {cbb.ylen:.1f} x {cbb.zlen:.1f} mm")

# ============================================================
# FIT CHECK INTERFACE (read by fitcheck.py)
# ============================================================
FIT_PARTS = [("shell", shell), ("lid", lid)]
FIT_ENVELOPE = cq.Workplane("XY").circle(outer_r).extrude(lid_outer_z)
FIT_PRESS_FITS = []
FIT_BACK_HIDE = ["lid"]
FIT_WORLD_EXTRA = [("cradle", cradle)]
DESK = dict(tilt=tilt_deg, lift=lift)
