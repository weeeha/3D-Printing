# Absurd Notice Signs — 256 × 200 mm, Bambu + AMS

Deadpan bureaucratic warning plaques. Two variants of the same three jokes:

| Variant | Script | Colours | Files |
|---|---|---|---|
| **ANSI colour** (current) | `build_signs_color.py` | 4 — white / black / yellow / blue | `csign_*.3mf` |
| Monochrome municipal notice | `build_signs.py` | 2 — cream / black | `sign_*.3mf` |

| Sign | Signal word | Pictogram | Content |
|---|---|---|---|
| `csign_airgap` | CAUTION (yellow) | crossed-out Wi-Fi | Do not connect this machine to the internet |
| `csign_clankers` | CAUTION (yellow) | crossed-out robot | No clankers allowed · max occupancy 0 |
| `csign_bilingual` | AVIS / NOTICE (blue) | crossed-out document | Reading this notice is prohibited (FR then EN) |

### Why AVIS comes first

This is a **Québec** sign, not a France one and not a federal-Ontario one. Under the
Charte de la langue française, French must be predominant on Québec signage, so the AVIS
panel leads and NOTICE follows. Two related conventions are baked into the copy:

- `100 $` — sign *after* the number, with a space. Not `$100`.
- `Amende : 100 $` — space before the colon, as French typography requires.
- Register is official rather than conversational: *« la lecture du présent avis »*, not
  *« de cette affiche »*.

## Geometry

- **256 × 200 × 4 mm.** Deliberately *not* 256 × 256 — the advertised 256³ volume is not
  usable for a flat footprint. A filament-cutter exclusion zone caps real full-width
  prints near **256 × 228 mm**, so a full square plate gets rejected by the slicer.
- **Flush colour inlay, 0.6 mm deep.** The plate carries pockets; each colour part fills
  them exactly, so the top face is flat with no fragile raised ridges.
- **0.6 mm is exactly 3 layers at 0.2 mm** — the colour change lands on a layer boundary
  rather than mid-layer. Keep `INLAY` an integer multiple of your layer height.
- Rounded corners R6, 3.2 mm black keyline border, four Ø4.5 mm holes for M4 screws.

### The colour model

The plate is white, and art exists *only* where a pocket is cut. So **white costs no
filament slot** — a white symbol is the absence of coloured art, with the plate showing
through at full height. That is what keeps these inside a single 4-slot AMS.

Coloured regions must never overlap, or two parts would claim the same pocket. Separation
is therefore boolean subtraction, exactly like offset printing plates:

```
yellow band = band_rect − (triangle ∪ exclamation ∪ letters)
```

The build asserts this — any colour pair overlapping by more than 0.02 mm² is reported.

### Design rules borrowed from ANSI Z535 / ISO 7010

- The **safety-alert triangle** appears only on DANGER / WARNING / CAUTION. NOTICE never
  gets one, which is why the blue bilingual sign is triangle-free.
- All three signs are *prohibitions*, so every pictogram is an **ISO prohibition roundel**
  — ring plus 45° bar plus symbol — rather than a mandatory-action disc.
- Pictograms are built from primitives (arcs, sectors, ellipses, polygons), not traced
  artwork, so they scale with the layout.

## Printing with AMS

1. Import the `.3mf`. It contains **four objects** — `plate_white`, `art_black`,
   `art_yellow`, `art_blue` — already positioned in millimetres. The bilingual sign has
   no yellow, so it carries three.
2. Select all, assemble into a single object so they slice as one part group.
3. Assign a filament per part by name.
4. Layer height **0.2 mm** (see the inlay-depth note above).

The parts share coincident boundary surfaces with zero clearance. That is correct for
multi-material parts — do not add a gap.

### Warping

A 256 × 200 mm flat plate is close to the worst case for FDM: maximum leverage for corner
lift as the first layers cool. PLA or PETG rather than ABS/ASA, brim on, textured PEI
plate, enclosure door open for PLA.

## Editing

```bash
# 2D only + SVG previews. Seconds. Use this while iterating on copy.
SIGNS_SVG=1 /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd build_signs_color.py

# full 3D + 3MF. Minutes.
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd build_signs_color.py
```

Copy lives in `sign_airgap` / `sign_clankers` / `sign_bilingual` at the bottom of the
script. `font_scale` per body tunes density.

### How the layout works, and what it refuses to do

- Glyph widths are measured **once** at a 10 mm reference height from wire bounding boxes.
  Outline advance is linear in size, so any other size is a multiplication — no
  re-measuring, and never the expensive face-making step. This is why the dry run is
  seconds rather than minutes.
- The footer is **anchored to the bottom edge and built upward**; the body then centres
  itself in whatever space remains. Pure top-down flow either piled dead space at the
  bottom or walked text off the plate — both happened before this changed.
- Headings, bullets and emphasis all wrap, bullets with a hanging indent. An unwrapped
  bullet once pushed art 7 mm past the right edge of the plate.
- Three checks report rather than silently degrade: **per-line column overflow**,
  **content taller than its region**, and a **bounding-box test of all fused art against
  the plate** — the last one catches overflow in any direction that per-line checks miss.
- `MIN_CAP = 4.5` mm is the printable floor for a 0.4 mm nozzle. Below roughly 1.2
  extrusion widths, thin strokes print patchy. Shorten copy rather than lowering it.

### Two environment traps worth knowing

- `freecadcmd` execs a script as a module named after the file, so `__name__` is **never**
  `"__main__"`. An `if __name__ == "__main__":` guard silently skips the entire script.
- Its embedded Python reports **US-ASCII** as the preferred encoding. `open(path, "w")`
  and `print()` both raise on non-ASCII, so SVG output is written with an explicit
  `encoding="utf-8"` and diagnostics pass through `ascii_safe()`. A warning containing a
  bullet character once crashed the run instead of reporting the problem it found.
  (`Part.makeWireString` itself handles Unicode fine — accents, curly quotes, `•`, `·`.)

`make_preview.py` traces the monochrome SVGs from the saved `.FCStd`; the colour script
emits its SVGs inline. Both trace the same geometry that gets extruded, so a preview
cannot drift from the print.

## Note on the parody

Fictional issuing bodies — *Bureau of Air-Gapped Appliances*, *Office of Organic
Occupancy*, *Ministry of Self-Reporting* — and no real municipal crest or wordmark. These
read as jokes rather than as counterfeit government or regulatory notices.
