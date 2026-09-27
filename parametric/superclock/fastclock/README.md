# fastclock body (May 2026 draft)

Imported on 2026-09-26 from `~/Documents/Claude/Projects/Super Clock Body Design/`
(FreeCAD file dated 2026-05-07, Blender file 2026-05-06). The originals are still there.

Target panel: Waveshare 5inch Round LCD, 1080x1080, Ø150 mm (see `docs/superclock-hardware.md`).

## `ClockBody_Parametric.FCStd`

Plain CSG, no spreadsheet. Values read from the file:

| Feature | Value |
|---|---|
| Outer shell | Ø157 x 33 mm (`OuterShell` r 78.5) |
| Cavity | Ø151, starts 3 mm behind the front face (`InnerCavity` r 75.5, 31 deep) |
| Front window | Ø130 through the 3 mm front face (`FrontWindow` r 65) |
| Bosses | 4x Ø9 x 12 mm at (±37.5, ±37.5), i.e. a 75 mm square, Z 21-33 |
| Boss holes | Ø4.5 (M4 clearance), 13 deep |

`ClockBody_Parametric.stl` is the export (gitignored by the repo's `*.stl` rule; re-export from the FCStd).

## `clock_body.blend`

Earlier Blender version. `clock_body.stl` was exported in metres (about 0.2 units across), so scale x1000 before slicing.

## Not verified

Radial clearance to the panel is 0.5 mm (Ø151 cavity vs Ø150 panel) on paper. Nothing here has been
test-fitted against the real fastclock, which also carries a Fusion HAT, an ov5647 camera and a power
button (see `docs/superclock-hardware.md`). None of those have cutouts yet.
