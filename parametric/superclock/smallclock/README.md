# smallclock enclosure

Round puck + back lid + desk cradle for `smallclock`: Waveshare 3.4inch DSI LCD (C), 800x800,
with a Raspberry Pi 4B on the back of the display board (see `docs/superclock-hardware.md`).

Source of truth: `smallclock_enclosure.py` (CadQuery). Run it with the cad-skill venv:

    ~/ClaudeCode\ Projects/cad-skill/.venv/bin/python smallclock_enclosure.py

It writes `smallclock_shell.stl`, `smallclock_lid.stl`, `smallclock_cradle.stl`, each in its print orientation.

Status: **Phase 2 (features), not printed yet.**

## Hardware
- 4x M4x40 countersunk (DIN 7991). Length matters: the panel's M4 holes are blind, 3.5 mm deep, and a longer screw bottoms out against the glass side.
- 4x 8 mm stick-on bumpers for the cradle.
- A 90-degree USB-C cable. A straight plug needs about 25 mm and there is 16-21 mm between the ports and the wall.

## Assembly
1. Display (with the Pi already on its back) drops into the shell from the back, glass against the front lip.
2. Route the power cable to the notch at 6 o'clock on the back rim.
3. Lid on, posts onto the panel's M4 holes, 4 screws. The posts are 0.2 mm long on purpose: tightening clamps the stack.
4. Set the puck in the cradle; the cable runs out through the channel at the back.

`vendor/` holds Waveshare's STEP model and dimension drawing, used for every measurement in the script.
