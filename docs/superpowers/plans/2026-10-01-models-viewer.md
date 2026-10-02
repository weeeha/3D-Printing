# Models viewer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A `/models` page in `catalog/` that shows every `print/**/*.3mf` in a 3D viewer with print time, filament, cost, bed fit and the slicer settings used, plus "Open in Bambu Studio".

**Architecture:** A Mac-only script slices each print file with Bambu Studio's CLI and commits `src/data/models.json` plus copies under `public/models/`. The static-export page reads that JSON, prices filament from `spools.json`, and renders a react-three-fiber viewer (copied from `../3D Models`) with a new 3MF reader that follows Bambu's component files.

**Tech Stack:** Next 15 static export, React 19, Tailwind 4, three 0.184, @react-three/fiber 9, @react-three/drei 10, three-stdlib 2, fflate 0.8, Vitest 2 (Node env).

**Spec:** `docs/superpowers/specs/2026-10-01-models-viewer-design.md`

## Global Constraints

- Vercel builds from `catalog/` alone: nothing at build or runtime reads `../print` or `../printer`. Only `npm run slice` and tests do.
- `npm run slice` needs `/Applications/BambuStudio.app`; it is never part of `npm run build`.
- P1S: bed 256 × 256 × 256 mm, no-go corner `0x0,18x0,18x28,0x28` (front-left), defaults `Bambu Lab P1S 0.4 nozzle` / `0.20mm Standard @BBL X1C` / `Bambu PLA Basic @BBL X1C`.
- Styling only from `globals.css` tokens (`--ground --surface --ink --muted --rule --rail --accent`, plus new `--warn --viewport --bed --bed-line`), system monospace, square corners, hairlines. No new fonts, no gradients, no emoji.
- Copy: verb + object labels, no exclamation marks, no em dashes.
- Money is CAD, two decimals. Durations `49m`, `6h 30m`.
- Plan deviation (noted for Nick): code is written once during execution, test first, rather than duplicated into this plan.

## File map

| File | Responsibility |
|---|---|
| `scripts/slice-lib.mjs` | Pure helpers for slicing: profile flattening, `--info` / `slice_info` / `plate_1.json` / settings parsing, bed offset, item placement, failure reason, slug, product line |
| `scripts/slice-models.mjs` | Mac runner: walk `print/`, slice, write `models.json` and `public/models/*.3mf` |
| `src/data/models.json` | Generated, committed |
| `public/models/<id>.3mf` | Generated, committed (LFS) |
| `src/lib/models.ts` | Types, formatting, plate union, clearance, centred footprint |
| `src/lib/prices.ts` | Median CAD/kg by product line with material fallback |
| `src/lib/estimate.ts` | Calibrate on records, estimate ranges |
| `src/lib/read3mf.ts` | DOM-free 3MF reader following `p:path` components |
| `src/lib/bambu.ts` | `bambustudioopen://` link |
| `src/lib/view-modes.ts` | View mode ids and labels |
| `src/components/models/ThreeMfLoader.ts` | three `Loader` around `read3mf` |
| `src/components/models/Model.tsx` | Playground `Model.tsx`, narrowed to 3MF/STL, reports size + volume |
| `src/components/models/Plate.tsx` | P1S plate, grid, no-go corner |
| `src/components/models/ModelCanvas.tsx` | Canvas, lights, controls, Bounds, error boundary (dynamic import) |
| `src/components/models/ViewControls.tsx` | Mode radiogroup + Wireframe |
| `src/components/models/ModelList.tsx` | Grouped file list |
| `src/components/models/BedDiagram.tsx` | SVG footprint on the bed |
| `src/components/models/PrintPanel.tsx` | Sliced / failed / estimate panels |
| `src/components/models/DropZone.tsx` | STL/3MF from disk |
| `src/components/models/ModelsWorkbench.tsx` | Client state and layout |
| `src/components/SiteNav.tsx` | Filament Shelf / Models nav |
| `src/app/models/page.tsx` | Route + metadata |
| `src/app/page.tsx` | Add `SiteNav` only |

## Interfaces

```ts
// src/lib/models.ts
export const BED = 256;
export const NO_GO: Box = [0, 0, 18, 28];
export type Box = [number, number, number, number];           // x0 y0 x1 y1, bed mm
export type Filament = { slot: number; type: string; line: string; hex: string | null; grams: number };
export type PlateObject = { name: string; box: Box; tower: boolean };
export type SliceSettings = { printer: string; process: string; layer: number; infill: string; walls: number; supports: boolean; nozzle: number };
export type Sliced = { status: "sliced"; seconds: number; filaments: Filament[]; plate: PlateObject[]; settings: SliceSettings };
export type Failed = { status: "failed"; reason: string; slicerMessage: string };
export type ModelRecord = { id: string; name: string; folder: string; file: string; sha256: string; parts: number;
  triangles: number; volumeCm3: number; size: [number, number, number]; settingsSource: "file" | "defaults"; slice: Sliced | Failed };
export type ModelsData = { slicedAt: string; slicer: string; models: ModelRecord[] };
export function formatDuration(seconds: number): string;      // 2946 -> "49m", 23400 -> "6h 30m"
export function formatMm(v: number): string;                  // 120.6 -> "120.6"
export function unionBox(boxes: { box: Box }[]): Box;
export function clearance(box: Box): number;                  // min distance to a bed edge, mm
export function centredBox(size: [number, number, number]): Box;
export function totalGrams(s: Sliced): number;

// src/lib/prices.ts
export type Price = { line: string; perKg: number; orders: number; matched: boolean };
export function priceFor(spools: Spool[], line: string, material: string): Price | null;
export function costCad(grams: number, perKg: number): number;

// src/lib/estimate.ts
export type Calibration = { gPerCm3: [number, number]; minPerG: [number, number]; basedOn: string[] };
export function calibrate(models: ModelRecord[]): Calibration | null;
export function estimate(volumeCm3: number, cal: Calibration): { grams: [number, number]; seconds: [number, number] };

// src/lib/read3mf.ts
export type MeshPart = { positions: Float32Array; indices: Uint32Array; matrix: number[] }; // matrix: column-major 4x4
export function read3mf(bytes: Uint8Array): MeshPart[];
export function parse3mfDocs(docs: Record<string, string>): MeshPart[];          // keys like "/3D/3dmodel.model"

// src/lib/bambu.ts
export function bambuStudioLink(fileUrl: string): string;    // "bambustudioopen://" + encodeURIComponent(fileUrl)

// scripts/slice-lib.mjs
export function flattenProfile(kind, name, readProfile);     // readProfile(kind, name) -> object; merges inherits chain
export function parseInfo(text);    // -> { size:[x,y,z], min:[x,y,z], max:[x,y,z], parts, triangles, volumeCm3 }
export function bedOffset(info);    // -> [tx, ty, tz] centring the union on (128,128), lowest point to Z=0
export function placeItems(modelXml, offset);   // every <item> gets "1 0 0 0 1 0 0 0 1 tx ty tz" composed with its own translation
export function parseSliceInfo(xml);            // -> { seconds, filaments:[{slot,type,hex,grams}], message? }
export function parsePlate(json);               // -> PlateObject[] (tower: /wipe|prime/i)
export function parseSettings(json);            // -> SliceSettings + filamentPresets[]
export function productLine(preset);            // "Bambu PLA Matte @BBL P1S 0.4 nozzle" -> "PLA Matte"; fallback "PLA Basic"
export function failureReason(size, slicerMessage); // fills-the-bed sentence when max(x,y) >= 255.9
export function slug(name);                     // "TEST-PLATE_tile+conflict" -> "test-plate-tile-conflict"
```

---

### Task 1: Slice helpers (`scripts/slice-lib.mjs`)

**Files:** Create `scripts/slice-lib.mjs`, `tests/slice-lib.test.ts`.

- [ ] Write failing tests:
  - `flattenProfile` merges a three-level fake chain parent-first; child keys win; `inherits` removed.
  - `parseInfo` on two-object `--info` text returns the union size and summed parts/triangles/volume.
  - `bedOffset` for min (-60.3,-60.3,-20.95) max (60.3,60.3,20.95) → [128, 128, 20.95].
  - `placeItems` rewrites both an `<item objectid="1" />` and an identity-transform item, keeping objectids.
  - `parseSliceInfo` on the real KIT snippet → seconds 23397, two filaments (#FFFFFF 132.16 g slot 1, #EC008C 39.81 g slot 2).
  - `parsePlate` marks `wipe_tower` as tower.
  - `productLine`, `slug`, `failureReason` (256 wide → contains "256.0 mm wide"; 120 wide → slicer message).
- [ ] Run `npx vitest run tests/slice-lib.test.ts`, expect FAIL (module missing).
- [ ] Implement `slice-lib.mjs`.
- [ ] Run, expect PASS. Commit "slice-lib: parse and place for Bambu CLI slicing".

### Task 2: Runner, data, freshness

**Files:** Create `scripts/slice-models.mjs`, `tests/models-freshness.test.ts`; modify `package.json` (`"slice": "node scripts/slice-models.mjs"`); generate `src/data/models.json`, `public/models/*.3mf`.

- [ ] Write `tests/models-freshness.test.ts`: every `../print/**/*.3mf` has a record with matching sha256; `public/models/<id>.3mf` bytes equal the source; no extra records.
- [ ] Run, expect FAIL (no models.json).
- [ ] Implement the runner (temp dir under `os.tmpdir()`, flattened defaults written once per run, `--info`, placement for bare meshes, slice, read outputs via `unzip -p`, failure records from `result.json`).
- [ ] Run `npm run slice`; expect 6 sliced + 6 failed; numbers match the spike (shell 49 min / 40.3 g, KIT PARTS 6h 30m / 172 g).
- [ ] Run freshness test, expect PASS. Commit "Slice print files into models.json".

### Task 3: 3MF reader

**Files:** Create `src/lib/read3mf.ts`, `tests/read3mf.test.ts`; add `fflate` dependency.

- [ ] Failing tests with 3MFs built via `zipSync`: single cube (8 vertices, 12 triangles, identity matrix); root object with two `p:path` components into `3D/Objects/object_1.model` with a translate transform (matrix carries tx); build item transform composes with component transform; missing root throws "No 3D/3dmodel.model".
- [ ] Run, FAIL. Implement with regex parsing (attributes in any order). Run, PASS. Commit.

### Task 4: Page libraries

**Files:** Create `src/lib/models.ts`, `src/lib/prices.ts`, `src/lib/estimate.ts`, `src/lib/bambu.ts`, `src/lib/view-modes.ts`, `tests/models-lib.test.ts`.

- [ ] Failing tests: `formatDuration` (2946 → "49m", 23400 → "6h 30m", 13211 → "3h 40m"); `clearance` of KIT plate union; `centredBox([256,200,4])` → [0,28,256,228] and clearance 0; `priceFor` PLA Matte → 12.99 (19 orders), unknown line "PLA Glow" falls back to PLA median, Amazon unpriced spools ignored; `costCad(40.3, 25.99)` → 1.05 (rounded at display); `calibrate` on committed models.json uses the three smallclock records; `estimate` scales linearly; `bambuStudioLink` encodes `https://x/models/a b.3mf`.
- [ ] Run, FAIL. Implement. Run, PASS. Commit.

### Task 5: Viewer

**Files:** Create `ThreeMfLoader.ts`, `Model.tsx`, `Plate.tsx`, `ModelCanvas.tsx`, `ViewControls.tsx`; add deps `three @react-three/fiber @react-three/drei three-stdlib @types/three`; add tokens `--warn --viewport --bed --bed-line` to `globals.css`.

- [ ] Copy `Model.tsx` from `../3D Models/components/scene/Model.tsx`; drop GLTF/OBJ sources and screen children; 3MF via `useLoader(ThreeMfLoader, url)`; add `onMeasure({ size, volumeCm3 })`; Realistic colour prop.
- [ ] `Plate.tsx`: 256 plane, 32 mm grid, no-go corner, offset prop; colours from CSS tokens, re-read on theme change.
- [ ] `ModelCanvas.tsx`: Canvas with shadows, hemisphere + directional light, `<Bounds fit clip observe margin={1.2}>` around the model only, OrbitControls, error boundary reporting `onError(message)`.
- [ ] `ViewControls.tsx`: radiogroup with arrow keys (from playground), Wireframe toggle, catalog styling.
- [ ] `npx tsc --noEmit` clean. Commit.

### Task 6: Page

**Files:** Create `ModelList.tsx`, `BedDiagram.tsx`, `PrintPanel.tsx`, `DropZone.tsx`, `ModelsWorkbench.tsx`, `SiteNav.tsx`, `src/app/models/page.tsx`; modify `src/app/page.tsx` (insert `<SiteNav current="shelf" />` as first child of `<main>`).

- [ ] Build the workbench per the spec layout and the approved draft; hash selection; dynamic import of `ModelCanvas` with `ssr: false`; loading / error overlay; panels for sliced, failed, estimate; action buttons (`<a href={bambuStudioLink(abs)}>`, `<a href="/models/<id>.3mf" download>`).
- [ ] `npm test` all green; `npm run build` succeeds and `out/models.html` exists. Commit.

### Task 7: Verify and ship

- [ ] `npm run dev`; in the browser pane at 1400 px and 375 px, light and dark: every family loads, modes switch, dropped STL gives a range, no horizontal scroll.
- [ ] Safari: same page, one family per type (or report unverified).
- [ ] Bambu link against the dev server opens the file in Bambu Studio (Bambu Studio not running beforehand).
- [ ] Run `me:unslop` Phase 2 on changed UI files; fix findings.
- [ ] Ship with `me:ship`: push branch, PR, Vercel preview link.
