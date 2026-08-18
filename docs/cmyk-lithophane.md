# CMYK lithophane printing

Source: [Bambu Lab wiki](https://wiki.bambulab.com/en/knowledge-sharing/cmyk-color-lithophane-printing-instructions).
The page returns HTTP 402 to plain fetchers; read it in a browser.

## Two routes

**Make My Lithophane** (Bambu's own web app, also in Bambu Handy under MakerLab) is the
short path. Pick *Colorful Litho with Fixed Frame* for CMYK or *Mono Litho with Fixed
Frame* for white-only. It exports a 3MF with the frame and light guide plate already
included and configured, ready to print.

**Manual route** via Lithophane Maker: generates **five STLs** from a JPG. Load all five
into Bambu Studio as one object with multiple parts, then assign colours by filename.

## Settings

| Setting | Value |
|---|---|
| Nozzle | **0.2mm** recommended |
| First layer height | 0.15mm |
| Top / bottom shell layers | 3 |
| Infill | 100% rectilinear |
| Canvas size | 144mm W x 108mm H (fits Bambu frame + LED backlight board) |
| Bed | 45-55degC for PLA Basic |

## The four filaments

Cyan `#0086D6`, Magenta `#EC008C`, Yellow `#F4EE2A`, **White `#FFFFFF`**.

Despite the "CMYK" name, the fourth slot is **white, not black**.

## Failure mode to watch

**AMS slot order must match the colour order set in Bambu Studio.** If it doesn't, the
print completes and the colours are simply wrong. Verify before every run.

## Frame and light guide plate

| Part | Filament | Walls | Top / bottom | Infill | Time | Usage |
|---|---|---|---|---|---|---|
| Frame | any PLA, dark preferred | 5 | 5 / 3 | 50%, tree support auto | 5h35m | 240g |
| Light guide plate | PLA Basic Jade White | 5 | 5 / 5 | | 35m | 30g |

## Gap in our setup

The P1S has a **0.4mm** hardened steel nozzle. Lithophanes at the recommended quality
want **0.2mm**, so this needs a nozzle purchase before attempting a good one.
