# Bambu Lab purchase audit

Two sources, kept in separate files because they carry different confidence.

- **Bambu Lab store** — reconstructed from the 13 order-confirmation emails from
  `noreply@bambulab.com` in mvyhouski@gmail.com, 20 Jun 2023 → 30 Dec 2025.
  Every line reconciles to the subtotal its email states.
  Ledger: [`orders.csv`](orders.csv).
- **Amazon, third-party brands** — transcribed from order-history screenshots,
  17 Dec 2022 → 7 Oct 2025. Items and dates only; **no prices were visible**, so
  none of this is in the spend figure.
  Ledger: [`orders-amazon.csv`](orders-amazon.csv).

> **This is what was bought, not what is on the shelf.** Filament is a
> consumable. Three years of printing has eaten an unknown share of the 76 kg
> below. Treat the filament tables as the purchase baseline and do one physical
> count against them (see [Counting stock](#counting-stock)).

## Totals

| | |
|---|---|
| Bambu orders | 13 |
| Bambu line items | 70 |
| Goods (subtotal) | $4,129.76 |
| Shipping | $126.00 |
| Taxes | $618.54 |
| **Bambu total spend** | **$4,874.30 CAD** |
| Discounts captured | $357.50 |
| Amazon filament spools | 19 (prices not captured) |
| **All filament, both sources** | **78 spools · 76 kg** |

## Hardware — durable, should all still exist

| Item | Qty | Bought | Paid |
|---|---|---|---|
| Bambu Lab P1P 3D Printer | 1 | 2023-06-20 | $899.00 |
| P1P Enclosure Kit | 1 | 2024-03-31 | $253.00 |
| AMS (Automatic Material System) | 2 | 2023-08-05, 2024-05-01 | $898.00 |
| AMS Hub | 1 | 2024-05-01 | $59.99 |
| Bambu Textured PEI Plate | 1 | 2023-07-24 | $48.99 |

**P1P + Enclosure Kit = the P1S the repo README refers to.** There is no P1S
order in the mail; the enclosure kit is the field conversion. Worth keeping
straight when buying parts — some listings are P1S-only SKUs.

Two AMS units + hub means 8 filament slots.

## Hotends and nozzles

| Spec | Form | Qty | Bought |
|---|---|---|---|
| 0.2 mm Stainless Steel | Complete hotend | 1 | 2023-07-24 |
| 0.4 mm Hardened Steel | Complete hotend | 1 | 2025-09-15 |
| 0.4 mm Hardened Steel | Hotend only | 2 | 2025-12-30 |
| 0.8 mm Hardened Steel | Complete hotend | 1 | 2025-12-30 |

5 hotends bought, $166.45. One is installed; the 2025-12 batch of three was
bought on the EOY bulk sale and is likely still sealed. **This is the highest-
value thing to physically confirm** — three spare hardened hotends cover a lot
of abrasive printing.

## Filament purchased — 55 rolls (1 kg) + 4 support spools (0.5 kg) = 57 kg

| Type | Rolls | Paid |
|---|---|---|
| PLA Matte | 19 | $365.81 |
| PETG Basic | 10 | $281.90 |
| PLA Basic | 8 | $211.92 |
| PLA Silk | 4 | $155.96 |
| PLA CMYK Lithophane Bundle | 4 | $89.99 |
| PLA Sparkle | 3 | $116.97 |
| PLA Silk Dual Color | 2 | $70.98 |
| PLA Tough | 2 | $73.98 |
| PETG Translucent | 2 | $51.98 |
| PLA Galaxy | 1 | $31.99 |
| **PLA + PETG subtotal** | **55** | **$1,451.48** |
| Support for PLA (0.5 kg) | 1 | $44.99 |
| Support for PA/PET (0.5 kg) | 1 | $50.99 |
| Support for PLA/PETG (0.5 kg) | 1 | $44.99 |
| PVA, water-soluble (0.5 kg) | 1 | $50.99 |
| **Support subtotal** | **4** | **$191.96** |

The 19 PLA Matte includes the 10-roll Ivory White / Charcoal refill pack from
Sep 2025 — bought at $12.99/roll, roughly half the per-roll price of every
other purchase in this list. Colour-by-colour breakdown is in `orders.csv`.

## Accessories, spares, consumables

| Item | Qty | Notes |
|---|---|---|
| Bambu Scraper (3 pcs) | 2 packs | 2024-09, 2025-12 |
| Desiccant for AMS (6 pack) | 2 packs | consumable — check saturation |
| PTFE tube 4000 mm | 2 | grey + white |
| PTFE tube connector | 1 | |
| Bambu 4-in-1 PTFE adapter | 1 | |
| Bambu Bus Cable, 6 pin 1500 mm | 1 | hub-to-AMS |
| AMS feeding funnel | 1 | |
| Anti-vibration feet | 1 set | |
| Hardened Steel Extruder Gear Assembly | 1 | spare, likely uninstalled |
| Nozzle wiper | 1 | wear part |
| Silicone sock for hotend | 1 | wear part |
| Replacement filament cutter | 1 | wear part |
| Bambu Filament Swatches | 1 | |
| Lithophane LED Backlight Board Kit | 1 kit (4 pcs) | 192×144 mm, KC010 |

## Third-party filament from Amazon — 19 spools, 19 kg

All 1.75 mm, all on non-Bambu spools with no RFID tag, so none of it
auto-identifies in the AMS and each spool needs its slot set by hand.

| Date | Brand | Item | Colour |
|---|---|---|---|
| 2022-12-17 | OVERTURE | PLA+ | Digital Blue |
| 2023-04-20 | DURAMIC 3D | PETG | Purple |
| 2023-04-23 | DURAMIC 3D | PETG | Yellow |
| 2023-04-23 | DURAMIC 3D | PETG | Pink |
| 2023-04-27 | DURAMIC 3D | PLA+ | Purple |
| 2023-04-27 | DURAMIC 3D | PLA+ | Purple |
| 2023-04-27 | DURAMIC 3D | PLA+ | White |
| 2023-07-22 | Creality | Hyper PLA | Black |
| 2023-07-22 | Creality | Hyper PLA | Grey |
| 2023-07-22 | GIANTARM | PLA Glow in the Dark | Rainbow |
| 2023-07-22 | TRONXY | PLA Glow bundle, 250 g ×4 | Green / Purple / Orange-red |
| 2023-07-24 | ANYCUBIC | Silk PLA | Silk Light Gold |
| 2023-07-24 | DURAMIC 3D | PETG | Translucent Green |
| 2023-09-07 | GIANTARM | PETG | Clear |
| 2023-10-18 | CC3D | Temp Colour Change PLA | Green to Yellow |
| 2024-08-23 | unbranded | PLA+ Colour Change | Rainbow |
| 2024-09-08 | CC3D | Silk PLA | Purple |
| 2025-09-14 | GIANTARM | PETG | Metal Green |
| 2025-10-07 | CC3D | Marble PETG | Stone Rock |

Plus one non-filament item: Bed Weld adhesive glue, 118 ml, Apr 2023.

**Seven of these predate the P1P.** The OVERTURE spool and all six April 2023
DURAMIC spools were bought before the printer arrived on 20 Jun 2023, so they
belong to an earlier printer. If those spools are still around they are three
years old and worth drying before trusting them on a long print.

**Two identical PLA+ Purple spools were ordered on the same day** (27 Apr 2023)
under two different order numbers. Either genuinely two spools or a duplicate in
the order history. Counted as two here; worth confirming on the shelf.

## Counting stock

`orders.csv` and `orders-amazon.csv` are the purchase ledgers and should stay immutable — it is the
audit trail. To get real stock, count once against it and keep the count in a
separate file, so a miscount never corrupts the source of truth.

The one decision worth making up front is how you track filament after the
first count. See [Open question](#open-question).

## Caveats

- **Amazon prices are not captured.** The order-history screenshots show items
  and dates but no amounts, so the $4,874.30 figure is Bambu Lab only. True
  total spend is higher by whatever the 19 third-party spools cost.
- **Other sellers may still be missing.** Anything bought from a reseller other
  than Amazon, or under a different email or Amazon account, is not here.
- **No cancellations or returns checked.** Every confirmed order is assumed
  fulfilled; delivery emails exist for the 2023–2024 orders but were not
  reconciled line-by-line.
- **One discount allocation is an assumption.** Order ca256246412 carried an
  `ACCESSORIES -$5.00 X1` discount that the email does not attach to a specific
  line; it is applied to the AMS Hub ($64.99 → $59.99). Order total is
  unaffected either way.
- **The 10-roll matte pack is split 5/5 by assumption.** The order line reads
  "Matte Ivory White and Charcoal" with no per-colour count. The 19-roll PLA
  Matte total is correct regardless; only the split between those two colours
  is a guess.
- **Order ca255613812** (P1P Enclosure Kit) was billed to Alena Vyhouskaya,
  shipped to the Montréal address. Included as it is the same printer.
