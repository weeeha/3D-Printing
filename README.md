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
sculpture/    Blender / Substance sources, one folder per project
print/        final .3mf (or STL when that is all that exists), per project
scans/        photogrammetry / LiDAR captures (Scaniverse, face scans, point clouds)
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
- MacBook `~/Project/2022`, `~/Project`, `~/3D Projects`, `~/Downloads` -> 2022–2023
  archive below (2026-09-28)

## 2022–2023 archive (from the MacBook)

Only the newest source per project was kept; `.blend1` backups, autosaves,
OBJ/FBX/USD exports and duplicate `(1)`/` 2` copies stayed local.
Authorship was checked from the absolute paths saved inside each `.blend`
(`/Users/NickVyhouski/...` = made on this Mac).

| Project | Sources (`sculpture/`) | Print (`print/`) |
|---|---|---|
| Pigeon "Big Tail" (Apr–May 2023) | `pigeon-bigtail/` modeled → prefinal → purple simplified | `pigeon-bigtail/` head, hair, body STL (colour print) |
| Hand (Jan 2023) | `hand/Hand_finalized.blend` | — (gcode only) |
| Ice sculpture room (Nov 2022) | `ice-sculpture/` | — |
| Mirror man sculpture (2023) | `mirror-man/sculpture.blend` ¹ | — |
| VR GoPro holder (Feb–Mar 2023) | `vr-gopro-holder/` | `vr-gopro-holder/` final 3 STL iterations |
| Stereophone (Mar–Apr 2023) | `stereophone/` | `stereophone/` a + b halves |
| Leshka micro mount (Mar 2023) | `leshka-mount/` | `leshka-mount/` |
| Camera holder (2023) | `camera-holder/` | `camera-holder/` + 3rd-person holder |
| Room (Oct 2022) | `room-2022/room.blend` | — |
| Boob (May 2023) | `boob/` | `boob/Boob.3mf` |
| Food experiment, old man hand, coin design, monument (2022) | one folder each | — |
| Hydrant texturing (Jun 2022) | `hydrant-texturing/hydrant.spp` (Substance Painter) | — |
| ZBrush bird / mushroom / flower / pig (Sep–Oct 2023) | ZBrush sources not found | `zbrush-bird/`, `mushroom/`, `flower/`, `pig/` .3mf |
| Bike mount, basket fix, side/middle parts, size tests (2023) | — | one folder each |

Scans: `scans/scaniverse/` (10 captures, Jul–Oct 2022), `scans/face/`
(NickEblet + facescan, Nov 2023), `scans/misc/` (point clouds, glasses, camera).

¹ Built around a third-party figure scan (`fig0038`); the raw scan itself is not included.

### Left out on purpose

- **Third-party downloads:** APACHE AH-64D, `fig00xx` figure scans, CGTrader
  pigeon (`uploads-files-3526806`), Rick & Morty (Thingiverse, CC-NC-ND),
  Knight with Flag, Warhammer-style minis (`Sup/`, `Unsupported/`), Bambu
  scraper/spool, iPhone model, Sketchfab/Poly Haven assets, Blender demo files.
- **Saved on someone else's PC** (possibly commissioned or collaborators' work,
  not yet confirmed): BigTail/Pistol2/Meat cube versions from `C:\Users\user`;
  Helicopter, EGGS, гриб, untitled4, Menu, REREHEPF and `Nastia Models` from
  `C:\Users\User`; Deus Ex leg, МОНЕТЫ, knife, old tank, Blender 2, ASiO, plants on table, shelf.
- **Course material:** `b30beginnersFiles`, `cube_diorama`, week-005 Unity class assets.
- **Too big / export-only:** raw ZBrush STL exports (Bird/Pig head/Hair, 100–485 MB each).
