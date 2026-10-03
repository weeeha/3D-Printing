# smallclock enclosures

Bodies for `smallclock`: Waveshare 3.4inch DSI LCD (C), 800x800, with a Raspberry Pi 4B on
the back of the display board, a SunFounder PiPower v2 UPS with its 2S pack behind the Pi, and a
USB mic (see `docs/superclock-hardware.md`). **The two final ones are the pebble and the flush-face
dome.** The puck, pebble and block hold the display on posts with M4x40 countersunk screws seated
40 mm from the panel; the flush dome screws the panel to its front ring with four M4x12.

| Variant | Script | Parts | Standing size (W x D x H) | Stands on |
|---|---|---|---|---|
| **Pebble** | `smallclock_pebble.py` | body, bezel | 121 x 97 x 121 mm | its own flat foot, 15 deg |
| **Dome, flush face** | `smallclock_dome_flush.py` | body | 125 x 121 x 113 mm | its own flat foot, 41 deg |
| Puck | `smallclock_enclosure.py` | shell, lid, cradle | 121 x 104 x 138 mm | the cradle, 15 deg |
| Block | `smallclock_block.py` | shell, back | 132 x 85 x 129 mm | its flat bottom, 12 deg |

`smallclock_dome.py` is the bezel version of the dome (`DOME=egg|balanced|wide`), kept as the
exploration the flush dome came from; it takes its widest-to-face ratio from there.

Run any of them with the cad-skill venv; each writes STL + 3MF per part in its print orientation:

    ~/ClaudeCode\ Projects/cad-skill/.venv/bin/python smallclock_pebble.py
    DOME=balanced ~/ClaudeCode\ Projects/cad-skill/.venv/bin/python smallclock_dome_flush.py

Print-ready copies are in `print/smallclock/`, each final body with a `_fit_test` slice next to it.

`fitcheck.py [puck|pebble|block|dome_flush]` puts the measured hardware stack inside the parts,
prints every clash (stack vs parts and part vs part), checks that it stands, and renders
`fitcheck[_<variant>]_cutaway_preview.png` and `fitcheck[_<variant>]_assembly_preview.png`.
Nothing is weighed yet, so the standing check gives each assembly a mass range (display 60-250 g,
Pi 40-50, PiPower 10-40, 2S pack 80-110, printed parts from their volume at 60-100 % solid PETG) and
tests every edge of the foot's contact patch at its worst case.

| Last run | Clashes | Slide-in gap | Contact patch | Centre of mass, worst case |
|---|---|---|---|---|
| Pebble | none (bezel press fit, as intended) | 4.6 mm | 63 x 55 mm | 18.4 mm inside |
| Dome, flush face | none | 1.2 mm | 71 x 69 mm | 26.0 mm inside |

Status: **designed and fit-checked in CadQuery, none printed yet.** Print the fit-test slice first.

## Pebble

One-piece body, open at the front, with a domed back and a flat foot cut under it. The stack slides
in **from the front** until the panel lands on four posts that grow out of the wall; the screws go in
from the back down four wells in the dome. A bezel ring then presses over a 1.2 mm rabbet on the
front edge (0.05 mm interference, add a drop of glue) and covers the glass rim. The dome has no seam.

- Print the body front edge down with **tree supports, build plate only**: they fill the dome and sit
  under the four post seats, and come out through the open front. Brim on: the body stands on the
  1.2 mm rabbet wall. The bezel skirt hides the brim line, but scrape it clean so the 0.05 mm press
  fit seats. Bezel: front face down, no supports.
- Fit test first: `smallclock_pebble_fit_test` is the body's first 11 mm (~11 g). Drop the panel in
  (0.4 mm clearance), check the four post seats line up with its M4 holes, press the bezel on.
- 77 mm deep; dome is a superellipse (`dome_n` 3) sized to clear the battery corners by 2 mm.
- Openings: mic port at 3 o'clock, switch slot at 1 o'clock, Ø7 charge-cable hole low on the back,
  two vent banks on the dome.
- Assembly: thread the 90-degree USB-C cable out through the back hole, slide the stack in, 4 screws,
  press the bezel on, plug the mic in through its port.

## Dome, flush face

The old fixed-body dome resized to the bare glass: no bezel. The display panel is the front, and the
body starts right behind it, its outer edge flush with the 115 mm glass. The dome keeps the bezel
version's widest-to-face ratio (Ø126 over a 115 face), runs 88.7 mm deep from the glass, and stands
on a flat foot with the face leaned back 41 degrees.

- **How it holds:** behind the panel there is a free ring between the display board (r 50.3) and the
  glass edge (r 57.5). The body's front ring seats there, opening Ø109 so the Pi's ports (r 53.5) slide
  through. Four M4x12 button-head screws go through bosses in the ring at 45 degrees, behind the
  display board, into the panel's own M4 holes (75 mm square, 3.5 mm deep). Each screw reaches its
  boss down an Ø8.4 guide tube: the top two tubes open in the back of the dome, the bottom two run out
  through the underside of the foot.
- **Print** front ring down: the ring is flat and sits on the bed. **Tree supports, build plate
  only**, for the dome cap and the four boss undersides (3.4 mm up, hanging 7 mm into the opening);
  they come out through the front. **Inner brim only**, so the visible outer edge stays clean; its
  0.4 mm chamfer takes up elephant's foot. The outer wall leans out at most 24 degrees, so the
  outside needs nothing.
- **Fit test first:** `smallclock_dome_flush_balanced_fit_test` is the ring and bosses only (11 mm,
  ~24 g). Screw it to the real panel: the outer edges should line up with the glass and the four
  screws should pull it down without bottoming out.
- Openings as on the pebble: mic port at 3 o'clock, switch slot at 1 o'clock, Ø7 charge-cable hole
  low on the back, two vent banks.

**Hardware:** 4x M4x12 button head (ISO 7380, 2.5 mm hex). Not longer: the ring is 9 mm thick under
the head, so 12 mm leaves 3.0 mm in the 3.5 mm blind holes, and a 14 bottoms out against the glass
side. A 2.5 mm hex key with at least 50 mm of reach: each screw head sits 46.5 mm down its tube
(a standard L-key's long arm is 56 mm; ball-end makes it easier).

**Assembly:**
1. Trim the 5V dupont leads, as for the puck.
2. Plug the 90-degree USB-C cable into the PiPower's charge port and thread it out through the
   cable hole from the inside.
3. Unplug the mic. Slide the stack in through the front, Pi's port end toward the mic port, until
   the panel's back sits on the ring.
4. Lay it face down on a cloth so the tubes stand vertical. Drop a screw down each tube and drive
   it with the key: snug, not tight (PETG ring, 3 mm of thread in the panel).
5. Plug the mic in through its port.

The glass edge is exposed on this one: nothing in front of it, so don't lift the clock by the panel.

## Block

The round face sits in a 132 mm soft square; the bottom is level through the face's bottom edge, so
the face leans back 12 degrees, and the back is cut vertical 4 mm behind the battery. The stack drops
in from the back, glass into a locating ring behind the lip. The back panel carries the posts, which
run along the display axis and so lean 12 degrees off the panel.

- Shell: face down, no supports. Back panel: outer face down, brim on (posts up to 77 mm).
- The mic sits 6 mm from the wall here, so it gets a 16-hole grille and stays plugged in.
- Switch slot in the top wall (34 mm reach for a pen), cable notch at the back panel's bottom edge,
  two vent banks on the back panel.

## Puck

The rest of this README covers the puck, except the measured stack and the print settings, which
apply to every variant. Its 13 mm lid posts stop 0.4 mm short of the bore so the lid
slides in; on that side each screw well opens into a channel that the shell wall closes.

## Measured stack (depth behind the glass front)

| Layer | mm | Source |
|---|---|---|
| Pi board | 17.1 | vendor STEP (exact) |
| Pi ports top | 34.9 | Raspberry Pi STEP |
| PiPower board | 43.2-44.8 | 24.5 mm spacers, measured off a side photo |
| 5V header + dupont leads | 60.8 | photo |
| Battery back | 64.8 | 74 x 38 mm off a back photo, 19.5 thick (2x18650) |

The photo numbers are about ±1 mm. Worth one caliper check before printing: glass front to the
back of the battery should read about 65 mm. If it differs, change `stack_back` and rerun both scripts.

## Print settings (Bambu P1S, 0.4 mm nozzle)

| Part | Orientation | Settings |
|---|---|---|
| Pebble body | front edge down | PETG, 0.2 mm, 3 walls, 15% gyroid, tree supports (build plate only), brim on |
| Pebble bezel | front face down | PETG, 0.2 mm, 3 walls, no supports |
| Dome flush body | front ring down | PETG, 0.2 mm, 3 walls, 15% gyroid, tree supports (build plate only), inner brim only |
| Fit tests (both) | as their body | the body's settings; the dome's needs supports under the bosses only |
| Puck shell | front face down | PETG, 0.2 mm, 3 walls, 15% gyroid, no supports |
| Puck lid | outer face down | PETG, 0.2 mm, 4 walls (the posts are mostly wall), 15% gyroid, no supports, brim on (64 mm posts) |
| Puck cradle | flat bottom down | PETG, 0.2 mm, 3 walls, 15% gyroid, no supports |

PETG because a Pi 4 behind a screen runs warm and PLA softens from about 55 C.

Supports, measured off the print meshes (faces steeper than 45 degrees, above the bed): the pebble
body needs them under the post seats (6 mm up) and the dome cap (from 60 mm); the flush dome under
the boss undersides (3.4 mm up) and the dome cap (from 60 mm). All of it sits inside the front
opening, so the supports stand on the plate and come out through the front. The bezel and the
puck parts have no overhangs past 45 degrees. Bridges: the mic port top (18 mm), the switch slot
top (14 mm) and, on the puck, the four 8 mm bumper recess ceilings under the cradle.

Rough weights, solid: pebble body 116 g + bezel 6 g, flush dome body 111 g; at 3 walls and 15%
infill expect a bit less, plus the supports.

## Key parameters

| Parameter | Value |
|---|---|
| Outer diameter | 120.6 mm |
| Shell depth | 71.4 mm (+ 3 mm lid) |
| Room behind the battery | 5.0 mm |
| Wall | 2.4 mm |
| Glass clearance | 0.4 mm radial |
| Front lip overlap | 3.0 mm (window Ø109, bevel to Ø111; active area Ø87.6) |
| Lid posts | Ø13 (Ø8 past the driver board), 64 mm, screw seated 29.5 mm down a Ø8.8 well |
| Mic port | 24 x 24 mm at 3 o'clock |
| Switch slot | 14 x 5 mm, about 1 o'clock |
| Tilt | 15 degrees |
| Cradle footprint | 100 x 104 mm |
| Post preload | 0.2 mm |

## Hardware
- 4x M4x40 countersunk (DIN 7991), the same as before: each head now seats at the bottom of a well
  in its post, still 40 mm from the panel. Length matters: the panel's M4 holes are blind, 3.5 mm
  deep, and a longer screw bottoms out against the glass side. Use a screwdriver with a shaft of at least 35 mm.
- 4x 8 mm stick-on bumpers for the cradle.
- A 90-degree USB-C cable for charging. The PiPower's USB-C input sits 28 mm inside the wall, too deep for a straight plug.

## Assembly
1. Trim the red/black 5V dupont leads (PiPower J5/J6 to the Pi's GPIO) so they don't loop past the battery.
2. Plug the 90-degree USB-C cable into the PiPower's charge port (bottom edge).
3. Unplug the USB mic. Drop the whole stack (display, Pi, PiPower, battery) into the shell from the back,
   glass against the front lip, Pi's port end toward the mic port at 3 o'clock.
4. Route the charge cable along the bottom to the notch at 6 o'clock on the back rim.
5. Lid on, posts onto the panel's M4 holes, 4 screws down the wells. The posts are 0.2 mm long on purpose: tightening clamps the stack.
6. Plug the mic back in through the mic port.
7. Set the puck in the cradle; the cable runs out through the channel at the back.

The PiPower switch is about 18 mm in from the slot at 1 o'clock; push it with a pen tip.
The charge-port edge is the bottom of the enclosure. If the picture comes out upside down, flip the
`wlr-randr` rotation in the labwc autostart (currently 180 degrees).

After the first assembly, run the clock with the lid on for an hour and check `vcgencmd measure_temp`:
the battery sits 5 mm in front of the lid vents and partly shades them.

`vendor/` holds Waveshare's STEP model and dimension drawing. The Raspberry Pi STEP stays outside the
repo (licence); `fitcheck.py` reads it from `PI_STEP` and falls back to its envelope when it is missing.
