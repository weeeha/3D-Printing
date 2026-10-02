import type { Spool } from "@/lib/spools";

export type Price = {
  line: string;
  /** CAD per kg. */
  perKg: number;
  /** How many priced spools the median came from. */
  spools: number;
  /** False when no spool of this line was bought and the material median stands in. */
  matched: boolean;
};

/**
 * What a kilo of this filament cost you: the median paid per kg over spools
 * of the same Bambu product line, else over the same material. Amazon spools
 * have no recorded price and never count.
 */
export function priceFor(spools: Spool[], line: string, material: string): Price | null {
  const priced = spools.filter((s) => s.pricePaidCad !== null && s.weightKg > 0);
  const own = priced.filter((s) => s.productLine === line);
  const pool = own.length ? own : priced.filter((s) => s.material === material);
  if (!pool.length) return null;
  const perKg = median(pool.map((s) => (s.pricePaidCad as number) / s.weightKg));
  return { line, perKg: Math.round(perKg * 100) / 100, spools: pool.length, matched: own.length > 0 };
}

export const costCad = (grams: number, perKg: number) => (grams / 1000) * perKg;

function median(values: number[]): number {
  const v = [...values].sort((a, b) => a - b);
  const mid = v.length >> 1;
  return v.length % 2 ? v[mid] : (v[mid - 1] + v[mid]) / 2;
}
