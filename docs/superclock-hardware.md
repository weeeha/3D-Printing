# SuperClock fleet hardware

Established by read-only SSH probe, 2026-08-17. **The four clocks are not the same
hardware**, so each needs its own enclosure design.

| Clock | Pi | Panel | Interface | Resolution |
|---|---|---|---|---|
| `fastclock` | **Pi 5** Rev 1.0 | Waveshare 5inch Round LCD, 10-pt touch | HDMI + USB touch | 1080x1080 |
| `smallclock` | Pi 4B Rev 1.5 | Waveshare 3.4inch DSI LCD (C), round, Goodix GT911 | DSI | 800x800 |
| `squareclock` | Pi 4B Rev 1.5 | 7-inch class, edt-ft5506 touch | DSI + bridge | 800x480 |
| `slowclock` | unknown | unknown | | offline at probe time |

## Notes per clock

**fastclock** additionally carries a **Fusion HAT** and an **ov5647 camera**, and uses
`dtoverlay=gpio-poweroff,gpio_pin=26`. The enclosure must accommodate the HAT stack, the
camera, and a power button. Being HDMI plus USB rather than DSI, it also needs room for
two cable runs rather than one ribbon.

**smallclock** uses `dtoverlay=vc4-kms-dsi-waveshare-panel,3_4_inch`. Vendor CAD is
published for this exact panel. Per the vendor wiki, **the Pi bolts directly onto the back
of the display board** via a 4-pin header, so the assembly is a sandwich rather than two
separately mounted parts.

As of 2026-10-01 smallclock also carries a **SunFounder PiPower v2** UPS (90 x 56 mm, Pi hole
pattern) on 24.5 mm brass spacers behind the Pi, component sides facing each other, with its
**2S 7.4 V 2000 mAh pack** taped to the PiPower's back. The photos show no USB cable from the
PiPower's USB-A out to the Pi; red/black dupont leads run from its J5/J6 5V pins instead, so it
looks GPIO-powered (unconfirmed). A **USB mic** (SuziePi,
23 x 20 x 5 mm) sits in the outer port of the USB3 stack. The stack ends 64.8 mm behind the glass;
the enclosure's `fitcheck.py` models all of it.

**squareclock is not the official Raspberry Pi 7" Touch Display**, despite presenting with
that driver signature (`7inch-touchscreen-p` i2c node, `edt-ft5506` touch). Compatible
clones are built as drop-in replacements, so **software identity does not establish
mechanical identity**. Its outer dimensions must be measured with calipers.

## Reaching the clocks

Use the `~/.ssh/config` aliases, which resolve over mDNS. The Tailscale IPs recorded in the
`me:clocks` skill are stale and time out.
