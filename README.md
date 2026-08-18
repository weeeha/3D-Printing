# 3D Printing

Models, sources and print-ready files for the Bambu Lab P1S.

Three tracks:

| Track | What | Toolchain |
|---|---|---|
| **Products** | Things that must fit real hardware. SuperClock bodies. | FreeCAD / OpenSCAD (parametric) |
| **Sculpture** | Art objects, judged by eye. | Blender (mesh) |
| **Signs** | Fake city construction / street signage. | FreeCAD scripted + SVG artwork |

## Layout

```
printer/      P1S profile, filament inventory, calibration results
parametric/   code-defined models
  signs/      FreeCAD pipeline (build_signs.py -> FCStd -> 3mf)
  superclock/ clock enclosures
  toolkit/    OpenSCAD story cubes, dice
sculpture/    Blender sources
print/        final .3mf, print-ready with AMS slots assigned
catalog/      static gallery site
docs/         notes, hardware measurements
```

## Rules of the repo

- **`.3mf` is the deliverable.** It carries AMS filament-slot assignments and
  per-object print settings. STL is a lossy export, not an archive.
- **Generated meshes are not committed.** `.stl` / `.step` regenerate from the
  parametric sources. Only `print/` holds kept binaries, via Git LFS.
- **Third-party models stay out.** Downloaded models carry their own licences
  and are not redistributed here.

## Source folders consolidated

Copied (originals left untouched) from:
- `3d Model Building/signs` -> `parametric/signs`, `print/signs`
- `3d Model Building/*.blend` -> `sculpture`
- `CreativeToolkit-Physical/scad` -> `parametric/toolkit`
- `CreativeToolkit-Physical/stl/*.3mf` -> `print/toolkit`
