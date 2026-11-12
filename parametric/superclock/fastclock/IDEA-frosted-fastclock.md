# Idea: frosted Fastclock with buttons

Saved 2026-11-11. A design idea for the SuperClock Fast body, explored as a Blender model and
renders. Nothing here has been test-fitted against the real hardware.

## The idea

- **Body:** the existing flat-base shell (`clock_body_fixed.stl`), in frosted clear plastic, so
  the electronics show as soft shapes. References: a frosted TourBox and a clear keyboard.
- **Display:** the real Waveshare 5-inch round panel, a 150 mm glass disc that caps the shell's
  149.6 mm rim edge to edge.
- **Buttons:** four round caps in an arc along the top, just behind the display, standing 5 mm
  proud. Left to right from the front: record (orange), play (wide white pill), plus and minus
  (black). The symbols are cut 1 mm into the caps, not printed.
- **Port door:** the window on the right side is the Raspberry Pi port opening. It is closed with
  a clear door so the Pi's USB and Ethernet sockets read through it.
- **Vent:** a speaker grille cut into the back. Five patterns exist: `dial` (a clock face of
  minute ticks, the current pick), `sunflower`, `waves`, `slots`, `burst`.
- **Cable exit:** an arch 13 mm wide and 10 mm tall at the bottom back.
- **Colours tried:** frosted (current), black, white.
- **Matte black version:** rendered full-size on 2026-11-11 with a black cable and the same buttons,
  vent and layout (`renders/product/fastclock_*_black_face-complications_dial.*`). The shell is
  opaque, so the port door is a plain flush panel and nothing inside shows. Build it by passing
  `black` in place of `frosted`.

## Inside the shell

| Part | Model used | Position |
|---|---|---|
| Display driver board | vendor CAD | behind the glass |
| Raspberry Pi 5 | official STEP from raspberrypi.com (MIT), converted and coloured by part type | centred behind the display, port end toward the door |
| Battery board | UPS HAT CAD | behind the Pi, placed by hand in Blender |
| Speaker | 100 mm speaker CAD scaled to 56.5% (about 58 mm wide) | upper back, tilted 24 degrees, placed by hand in Blender |

The hand-placed positions are in `fastclock_layout.json` and override the script's own placement.

## Files

- `product_render.py`: builds the whole scene and renders it. Usage and options are in its header.
- `fastclock_layout.json`: speaker and battery board positions from Blender.
- `fastclock_assembly_latest.blend`: plain colour-coded model with a see-through shell.
- `fastclock_assembly_check.blend`: the scene the parts were moved in by hand.
- `fastclock_body_grille_cable.stl`: the shell with an earlier vent and the cable exit, for printing tests.
- `renders/product/`: full-size renders. `renders/product/previews/`: low-res sheets of each step.
- `tools/step2obj.py`, `tools/pi5_to_glb.py`: the Pi 5 STEP conversion.
- Pi 5 source: `~/Product Design/SuperClock/Component CAD models/CAD RaspberryPi5/`.

Rebuild the current version (model view):

    Blender -b --python product_render.py -- model ports,rear,side <screen.png> <out_dir> frosted grille=dial grille_elev=24 grille_o=0.0007,0.0433,0.0724

Use `final` in place of `model` for full-size renders, and `hero,back,ports,keys` for the views.

## Known problems

- **Battery board:** 20 of 640 sampled points are outside the shell at its lower back corner.
- **Speaker:** 4 of 617 sampled points touch the Pi's box. The full-size 100 mm speaker does not fit
  anywhere at the back without hitting the Pi or the battery board, which is why it was scaled down.
- **Real hardware differs:** the Fast carries a SunFounder Fusion HAT (battery, mic, speaker), an
  OV5647 camera and an A121 range sensor. None of those are modelled. The UPS HAT and speaker here
  come from the early Pi 4 parts set.
- **Pi 5 colours:** assigned by shape, since the official STEP has no colours. Most small parts are
  a neutral grey, so the USB 3 sockets are not blue.
- **Buttons:** no switches or stems are modelled under the caps, and from straight in front the caps
  barely show above the glass.
- **Vent and cable exit:** drawn for the render, not positioned against a real speaker or socket.
- **Play mark:** faint on the white cap in previews.

## Where this was heading

The renders were meant for the SuperClock portfolio page hero and for a desk-style product video
(Seedance, from stills). Neither has been made from this version yet.
