# Virtual filament shelf — design

Date: 2026-08-17
Status: approved, ready for implementation planning

## Purpose

A web page that shows the filament collection as a shelf you can look at,
and doubles as the tool for counting what is actually left. Two view modes:
a realistic wall rack and a dense grid. Deployed to Vercel.

The audit documents (`printer/inventory.md`, `printer/orders.csv`,
`printer/orders-amazon.csv`) answer *what was bought*. This app answers
*what is on the shelf right now*, which no document can, because only a
human looking at the shelf knows.

## Scope

In scope:

- Render all 78 purchased spools, each with its own colour and finish.
- Two view modes, rack and grid, with a toggle that preserves filter state.
- Per-spool status: Have, Running low, Gone. Set by clicking.
- Filters by material, source and status.
- Export the current status as `stock.csv`.
- Deploy to Vercel from `catalog/`.

Not in scope:

- Editing purchase data through the UI. The CSVs are edited by hand.
- Gram-level remaining-weight tracking. Three coarse states only.
- Accounts, sync, or any server-side state.
- The drawer view or AMS slot-card view. Rack and grid only.

## Data model

### Source of truth

`printer/orders.csv` and `printer/orders-amazon.csv` remain the ledgers and
are never written by the app.

### Build step

`catalog/scripts/build-spools.mjs` reads both CSVs and writes
`catalog/src/data/spools.json`.

**Only filament rows become spools.** From `orders.csv` that means the
`filament` and `support` categories; `printer`, `hardware`, `ams`, `hotend`,
`accessory` and `spare` rows are skipped. From `orders-amazon.csv` every row
becomes a spool except the Bed Weld adhesive glue. Hardware and accessories
belong to `printer/inventory.md`, not to the shelf.

Its other job is to explode line items into one record per physical spool:

- `PETG Basic White ×2` becomes 2 records.
- `PLA Matte Refill Pack 10 Rolls` becomes 10 records, 5 Ivory White and
  5 Charcoal, per the documented 5/5 assumption.
- `PLA CMYK Lithophane Bundle` becomes 4 records, one per process colour.
- `TRONXY PLA Glow bundle, 250 g ×4` becomes 1 record of 1 kg, because it
  ships as one bundle and is stored as one unit.

Spool record:

```
{
  id: string            // stable slug, e.g. "bambu-pla-matte-11101-3"
  source: "bambu" | "amazon"
  brand: string
  material: "PLA" | "PETG" | "PVA" | "Support"
  productLine: string   // "PLA Matte", "Hyper PLA", "Silk PLA"
  colourName: string
  colourCode: string    // Bambu code where known, else ""
  hex: string
  finish: Finish
  weightKg: number
  isRefill: boolean
  orderId: string
  orderDate: string     // ISO
  pricePaidCad: number | null   // null for every Amazon spool
}
```

`pricePaidCad` is nullable because the Amazon screenshots carried no prices.
The UI must render a null price as "not captured", never as $0.

### Colour and finish

`catalog/src/lib/colours.ts` maps Bambu colour code, or third-party
brand plus colour name, to `{ hex, finish }`.

```
type Finish =
  | "basic" | "matte" | "silk" | "sparkle" | "translucent"
  | "dual" | "rainbow" | "glow" | "marble"
```

Finish drives rendering, not just labelling:

- `silk` gets a specular sheen across the coil.
- `sparkle` and `marble` get a fine speckle overlay.
- `translucent` renders at partial alpha over the rack behind it.
- `dual` and `rainbow` use multi-stop gradients along the winding.
- `glow` gets a soft outer bloom.

Hex values are a best reading of Bambu's published colour codes, not
sampled from physical spools. They are expected to need correction once
compared against the real shelf. This is why the mapping is one isolated
file with no other responsibility.

## Status layer

`catalog/src/lib/status.ts` owns all status state.

- Shape: `Record<spoolId, "have" | "low" | "gone">`.
- Default for every spool: `have`. Nick's stated position is that the
  collection is broadly intact, so marking exceptions is less work than
  confirming 78 items.
- Persisted to `localStorage` under one key. Never written into
  `spools.json`, so a mis-click cannot corrupt the purchase ledger.
- Clicking a spool cycles `have → low → gone → have`.
- Export writes `stock.csv` with columns
  `id,colourName,material,source,status,exportedAt`.
- Unknown ids in stored state are ignored on load, so adding spools to
  the ledger later does not break an existing saved count.

## Views

### Rack (default)

Modelled on the black wall rack reference. Spools are seen edge-on: an
outer flange ring, the wound coil in the filament colour with fine
concentric winding texture, and a hub hole. Ranked across horizontal
rails, roughly twelve per shelf, wrapping responsively.

Gone spools stay in position, dimmed to an empty rail slot outline rather
than being removed, so the shelf shows the hole where something used to be.

### Grid

Dense sortable swatch grid. Each cell shows the colour, name, code,
material, source and status. Sortable by colour family, material,
purchase date and status.

### Toggle

A single control switches modes. Active filters and scroll position
survive the switch.

## Filters

- Material: PLA, PETG, PVA, Support.
- Source: Bambu Lab, Amazon.
- Status: Have, Running low, Gone.

Filters combine as AND across categories and OR within a category. A
running count shows how many of 78 spools match.

## Modules

| File | Responsibility |
|---|---|
| `scripts/build-spools.mjs` | CSV to `spools.json`. Build time only. |
| `src/lib/colours.ts` | Colour code to hex and finish. Pure data. |
| `src/lib/spools.ts` | Types, loader, filter and sort helpers. |
| `src/lib/status.ts` | Status state, persistence, CSV export. |
| `src/components/Spool.tsx` | One spool as SVG. Finish-aware. |
| `src/components/RackView.tsx` | Shelf rails and spool placement. |
| `src/components/GridView.tsx` | Grid cells. |
| `src/components/Filters.tsx` | Filter and sort controls. |
| `src/app/page.tsx` | Composition, view toggle, state wiring. |

Each is independently testable. `Spool.tsx` takes a spool and a status and
knows nothing about filtering or persistence.

## Testing

The build script holds the only non-trivial logic, so it carries the tests:

- Total spool count is exactly 78.
- Bambu spools 59, Amazon spools 19.
- Bambu weight totals 57 kg, Amazon 19 kg.
- Every spool has a non-empty `hex` and a valid `finish`.
- Every `id` is unique.
- Bundle expansion is correct: the 10-pack yields 10, CMYK yields 4, the
  TRONXY glow bundle yields 1.

Status layer tests: cycle order is correct, export produces one row per
spool, unknown ids in stored state are dropped on load.

A failing count test is the intended alarm if a CSV edit changes the data.

## Deployment

- Next.js App Router, static export, Tailwind. No component library.
- Vercel project root directory: `catalog/`.
- Branch `filament-shelf`, preview deployment first. Not promoted to
  production without an explicit go.

## Known limitations, stated on the page

- Colour hexes are indicative, not sampled.
- Amazon prices were never captured, so spend figures are Bambu only.
- The 10-roll matte pack's 5/5 colour split is an assumption.
- Two identical DURAMIC PLA+ Purple spools ordered the same day are
  counted as two; may be one duplicated order-history row.
- Status is a human count, not measured weight, and is only as fresh as
  the last time someone clicked through the shelf.
