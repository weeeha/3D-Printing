# Models viewer — design

Date: 2026-10-01
Status: approved (draft reviewed, "build"), ready for implementation planning
Draft: https://claude.ai/artifact/HRuRfdx7CwV381NPmd89TQ

## Purpose

A `/models` page in the `catalog/` site that shows every print-ready file in
`print/` in a 3D viewer, with what it takes to print it on the P1S: print
time, filament per colour, cost at the prices actually paid, size and bed
fit, and the slicer settings the numbers came from. A download hands the
file to Bambu Studio.

The viewer is the one from `3d-models-playground` (`../3D Models`), copied
and narrowed to print formats. The filament shelf stays at `/`.

## Scope

In scope:

- The 12 `.3mf` files under `print/`. STL copies are not listed.
- Geometry, Surface and Realistic view modes plus Wireframe, on a 256 mm P1S
  plate drawn where the slicer placed the parts.
- A print panel: time, filament and cost, size and bed fit, settings used,
  "Download .3mf".
- Dropping an STL or 3MF from disk for a rough estimate (a range).
- A two-link site nav, Filament Shelf and Models, on both pages.

Not in scope:

- Sending jobs to the printer. The download stops at opening the file.
- The Realistic room, lighting presets and SuperClock screen faces from the
  playground viewer. Realistic here is plastic on the plate.
- Per-object colours in Realistic for multi-colour files.
- Fixing the sign files (see Known issues).

## Data

### Source of truth

`print/**/*.3mf` stay the deliverables and are never written by the app.
Prices come from `catalog/src/data/spools.json`, already built from the
order ledgers.

### Slicing step (Mac only)

`catalog/scripts/slice-models.mjs`, run as `npm run slice`. It needs Bambu
Studio at `/Applications/BambuStudio.app` and is never run on Vercel.

For each `print/**/*.3mf`:

1. **Settings.** A file with `Metadata/project_settings.config` is a Bambu
   Studio project and slices with its own settings. Any other file is a bare
   mesh and slices with the P1S defaults: `Bambu Lab P1S 0.4 nozzle`,
   `0.20mm Standard @BBL X1C`, `Bambu PLA Basic @BBL X1C`.
2. **Flatten the default profiles.** Bambu's system profiles inherit through
   a chain (`PLA Basic @BBL X1C` → `@base` → `fdm_filament_pla` → ...). The
   CLI does not follow `inherits`, so unflattened profiles silently fall back
   to built-in values (20% infill instead of 15%, density 0, so 0 g). The
   script merges each chain, parent first, into one JSON before slicing.
3. **Place bare meshes on the bed.** Bare meshes come from CadQuery and
   FreeCAD in their own coordinates. Auto-arrange splits multi-part signs
   apart, and no arrange leaves origin-centred parts off the bed. The script
   copies the file, moves every build item by one shared offset so the union
   is centred on (128, 128) with its lowest point at Z = 0, and slices with
   `--arrange 0`.
4. **Slice** with `--slice 0 --export-3mf`, then read from the output:
   `Metadata/slice_info.config` (time, per-filament type, colour, grams),
   `Metadata/plate_1.json` (each object's footprint on the bed, including the
   prime tower), `Metadata/project_settings.config` (settings used).
5. **Measure** with `--info`: overall size, parts, triangles, volume.

Output, both committed (Vercel builds from `catalog/` alone, the same rule as
`spools.json`):

- `catalog/src/data/models.json`: one record per file, below.
- `catalog/public/models/<id>.3mf`: a copy of each file. These go through Git
  LFS by the existing `*.3mf` rule; LFS stores by content hash, so the copy
  adds no LFS storage.

A slice that fails is recorded, not dropped, with a reason a person can act
on. A part at or over 255.9 mm on X or Y gets "fills the bed"; anything else
carries Bambu Studio's own message.

### Record

```ts
type ModelRecord = {
  id: string;              // slug of the file name, used in /models#<id>
  name: string;            // file name without .3mf
  folder: string;          // print/<folder>
  file: string;            // repo path
  sha256: string;          // of the print/ file, for the freshness test
  parts: number;
  triangles: number;
  volumeCm3: number;
  size: [number, number, number];  // mm, X × Y × Z
  settingsSource: "file" | "defaults";
  slice:
    | { status: "sliced"; seconds: number; filaments: Filament[];
        plate: PlateObject[]; settings: SliceSettings }
    | { status: "failed"; reason: string; slicerMessage: string };
};
type Filament = { slot: number; type: string; line: string;
                  hex: string | null; grams: number };
type PlateObject = { name: string; box: [number, number, number, number];
                     tower: boolean };   // bed mm, x0 y0 x1 y1
```

`line` is the Bambu product line taken from the slot's filament preset
("PLA Matte", "PLA Basic"). `hex` is null for bare meshes, which carry no
colour.

### Freshness

`tests/models-freshness.test.ts`: every `print/**/*.3mf` has a record, every
record's `sha256` matches its file, and every `public/models/<id>.3mf` is a
byte copy. Edit a print file without running `npm run slice` and it fails.

## Cost

Price per kg is the median of `pricePaidCad / weightKg` over priced spools of
the same product line. With no priced spool of that line, the median of the
same material. Amazon spools have no recorded price and never count. Today:
PLA Basic CAD 25.99 (8 spools), PLA Matte 12.99 (19). The panel names the
line, the price and how many orders it came from.

## Estimate for dropped files

The viewer measures the mesh volume (signed tetrahedra) and size. Grams and
minutes are shown as a range, calibrated at runtime on this repo's own
records: sliced, single filament, 0.4 mm nozzle, 0.20 mm layers. Grams =
volume × the lowest and highest g/cm³ seen; minutes = grams × the lowest and
highest min/g seen. Fewer than two calibration records: show volume and size
only. The panel says it is an estimate and to slice for a real number.

## Page

`catalog/src/app/models/page.tsx` (server component, metadata) renders
`ModelsPage` (client): header, a Gallery / List / Viewer switch styled like
the shelf's Rack / Grid toggle, and the selected view. The 3D canvas loads
with `next/dynamic`, `ssr: false`, so the static export never renders
three.js on the server.

Layout follows the approved draft and the shelf's system: tokens from
`globals.css`, system monospace, hairline rules, square corners.

The view lives in the hash: none or `#gallery` is the gallery, `#list` the
list, `#<model id>` the viewer on that model. Opening a model from an
overview is a history step, so Back returns to it; picking another model
inside the viewer replaces the entry.

### Gallery and list (added 2026-10-02)

- **Gallery** (default): cards grouped by `print/` folder, each with Bambu
  Studio's plate thumbnail (`public/models/<id>.png`, transparent, so it sits
  on light and dark), name, time · grams · cost or "Not sliced · reason",
  and size. Two columns on phones.
- **List**: one row per file with print time, filament, cost, size, bed
  clearance and settings source. Model, time, filament and cost sort; files
  without a slice stay last either way. Unsorted, it follows the gallery's
  folder order.

Thumbnails come from `npm run slice`: `--export-png 0` renders the plate
without slicing, so refused files get one too. Bare meshes render in the
viewer's Geometry grey instead of Bambu's default green.

### Viewer layout

- ≥1140 px: list 236 px | viewer | panel 300 px.
- 760–1139 px: viewer | panel, list under the viewer.
- Narrower: viewer, panel, list.

### Viewer

Copied from the playground: `Model.tsx` (per-mesh flat, creased-smooth and
edge variants, Z-up grounding), the mode switch as a keyboard radiogroup, and
the Wireframe toggle. Changes:

- **3MF reader.** three's bundled `ThreeMFLoader` cannot open Bambu Studio
  projects: they keep each part in `3D/Objects/object_N.model` and reference
  it with `p:path`, which it does not follow. `src/lib/read3mf.ts` unzips with
  fflate and parses with regular expressions into plain meshes and matrices,
  following components across files. It has no DOM dependency, so it is unit
  tested in Node. A three `Loader` wraps it for `useLoader`.
- **Plate, not grid.** A 256 mm plate with a 32 mm grid and the 18 × 28 mm
  front-left no-go corner from the P1S profile (`bed_exclude_area`). For a
  sliced record the plate is offset so the parts sit where `plate_1.json`
  puts them.
- **Realistic** is a plastic material in the file's colour when there is
  exactly one filament with a colour, otherwise neutral, with soft shadows on
  the plate.

States: loading, loaded, couldn't load (with the reason), and the panel's
own states below.

### Print panel

- Head: file name, path, part count, a chip: "Settings from the file", "P1S
  defaults", "Not sliced", or "Estimate".
- Print time, large.
- Filament and cost (CAD): swatch, line, grams, cost per slot, total, and
  one price line per product line.
- Size and bed fit: size (a multi-part plate shows its footprint and
  height), a bed diagram with parts, prime tower and no-go corner, and the
  clearance to the nearest edge or "No clearance".
- Sliced with: printer, process, layer, infill, walls, supports. For
  defaults, a sentence that the real print may use other settings.
- Action: "Download .3mf".

### Open in Bambu Studio (dropped during build)

Bambu Studio 2.07 on macOS registers `bambustudioopen://`. Tested on
2026-10-01 against a local server that logged every request, three link
forms (`bambustudioopen://<encoded url>`, `bambustudioopen://open?file=...`,
and the raw URL) all launched Bambu Studio, and none made it request the
file. It likely accepts only MakerWorld links or a logged-in Bambu account;
its logs are encrypted, so which one is unconfirmed.

So the panel's action is "Download .3mf". Bambu Studio registers `.3mf`, so
opening the download from the browser opens it there. The download also
works behind Vercel Authentication, which protects every deployment of the
catalog project including production
(`ssoProtection: all_except_custom_domains`); a link Bambu Studio fetches
itself could not have passed that anyway.

## Testing

Vitest, Node environment, as now:

- `read3mf`: a single-mesh 3MF and a components-across-files 3MF built in the
  test with fflate; transforms applied; a missing root model throws.
- Slice parsing: `slice_info.config`, `plate_1.json` and profile-chain
  flattening against fixture text and a fake profile directory.
- Bed placement from real vertices (`boundsOf`), stepping clear of the no-go corner.
- Prices, cost, duration format, bed clearance, estimate range.
- Freshness, as above.

Manual: `npm run build` (static export), then the page in Chrome and Safari
at desktop and 375 px, light and dark, every file family, a dropped STL, and
the Bambu Studio link against the dev server.

## Known issues found while designing

- **Bambu's `--info` centres every object on itself.** Its min/max say
  nothing about where a file puts its parts, so placement and size come from
  the vertices (`boundsOf` over `read3mf`), and `--info` only supplies
  counts and volume.
- **The six signs do not slice: G-code conflict.** Their text parts are
  separate objects overlapping the sign body. Corrected on 2026-10-02: an
  earlier note blamed the 256.0 mm width. The body alone, 256 mm wide,
  slices (3h 34m, 141 g) once placed clear of the no-go corner; centred, it
  touches that corner and Bambu reports an object conflict instead, which
  is why placement now steps back from it.
- The README says `print/` files have AMS slots assigned. Only the three
  toolkit files do; signs and smallclock are bare meshes.
- The playground viewer (`3d-models-playground`, three-stdlib 2.36.1
  `ThreeMFLoader`) opens bare meshes but fails on Bambu Studio projects with
  "Cannot read properties of undefined (reading 'mesh')". Confirmed
  2026-10-02 in headless Chrome.
