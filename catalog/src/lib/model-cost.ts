import rawSpools from "@/data/spools.json";
import type { Spool } from "@/lib/spools";
import type { Filament, Sliced } from "@/lib/models";
import { costCad, priceFor, type Price } from "@/lib/prices";

const SPOOLS = rawSpools as Spool[];

export const filamentPrice = (f: Pick<Filament, "line" | "type">): Price | null => priceFor(SPOOLS, f.line, f.type);

/** Total CAD for a slice, or null when any filament has no price to go on. */
export function sliceCost(s: Sliced): number | null {
  let total = 0;
  for (const f of s.filaments) {
    const price = filamentPrice(f);
    if (!price) return null;
    total += costCad(f.grams, price.perKg);
  }
  return total;
}

export const formatCad = (v: number) => `$${v.toFixed(2)}`;
