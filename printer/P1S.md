# Bambu Lab P1S

## Machine
- Enclosed CoreXY, build volume **256 x 256 x 256 mm**.
- AMS fitted, multi-colour via filament-slot assignment baked into the `.3mf`.
- Ships with a **hardened steel 0.4 mm nozzle** (verify if it has been swapped).

## Filament on hand
| Filament | Slot use | Notes |
|---|---|---|
| CMYK kit (cyan / magenta / yellow / black) | AMS colour work | Bambu 4-colour set |
| Black | Structural, sign bodies | |
| White | Sign faces, diffusers | |
| Purple sparkle (glitter PLA) | Feature / sculpture | See constraint below |

## Design constraints

**Glitter PLA is abrasive and detail-limited.** The flakes wash out fine
features below roughly 0.8 mm, so sparkle parts want bold, chunky geometry:
sculpture and sign bodies, not fine text, thin ribs or printed threads.
Abrasive filament also wears brass nozzles, which is why the hardened steel
nozzle matters.

**Multi-colour is geometry, not paint.** Each colour is a separate body/object
assigned to an AMS slot. A model exported as a single fused mesh loses this.
Design colour separation into the model from the start.

## Calibration
Results go here as they are run: flow ratio, temperature tower, tolerance /
fit-test coupons per filament. `CreativeToolkit-Physical` already has a
`calibration_tile` worth re-running per filament.
