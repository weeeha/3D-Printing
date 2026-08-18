import type { Spool } from "./spools";

/**
 * Ordering spools the way you would arrange a physical shelf: by colour.
 *
 * Everything here derives from the spool's hex, converted to HSL once.
 * Extreme lightness is tested before saturation, because a near-white
 * translucent spool has enough residual saturation to land in a hue bucket
 * otherwise, and "clear PETG filed under green" is nonsense on a shelf.
 */

export type ColourFamily =
  | "Red" | "Orange" | "Yellow" | "Green" | "Cyan" | "Blue" | "Purple"
  | "Pink" | "White" | "Neutral" | "Black" | "Multi";

/** Display order: the spectrum, then neutrals, then the multi-colour rolls. */
export const FAMILY_ORDER: ColourFamily[] = [
  "Red", "Orange", "Yellow", "Green", "Cyan", "Blue", "Purple", "Pink",
  "White", "Neutral", "Black", "Multi",
];

export type Hsl = { h: number; s: number; l: number };

export function hexToHsl(hex: string): Hsl {
  const n = parseInt(hex.slice(1), 16);
  const r = ((n >> 16) & 255) / 255;
  const g = ((n >> 8) & 255) / 255;
  const b = (n & 255) / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const d = max - min;
  const l = (max + min) / 2;
  let s = 0;
  let h = 0;
  if (d !== 0) {
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) * 60;
    else if (max === g) h = ((b - r) / d + 2) * 60;
    else h = ((r - g) / d + 4) * 60;
  }
  return { h, s, l };
}

const HUE_BANDS: [number, number, ColourFamily][] = [
  [15, 45, "Orange"],
  [45, 70, "Yellow"],
  [70, 160, "Green"],
  [160, 200, "Cyan"],
  [200, 255, "Blue"],
  [255, 290, "Purple"],
  [290, 345, "Pink"],
];

export function colourFamily(spool: Spool): ColourFamily {
  // Rolls with no single hue: rainbow, and the two-tone dual-colour rolls.
  if (spool.finish === "rainbow" || spool.finish === "dual") return "Multi";

  const { h, s, l } = hexToHsl(spool.hex);
  if (l > 0.92) return "White";
  if (l < 0.15) return "Black";
  if (s < 0.15) return "Neutral";
  for (const [lo, hi, family] of HUE_BANDS) {
    if (h >= lo && h < hi) return family;
  }
  return "Red";
}

export type SortKey = "date" | "colour" | "material" | "status";

export const SORT_LABEL: Record<SortKey, string> = {
  date: "Purchase date",
  colour: "Colour",
  material: "Material",
  status: "Status",
};

const STATUS_RANK = { have: 0, low: 1, gone: 2 } as const;

export function sortSpools(
  spools: Spool[],
  key: SortKey,
  status: Record<string, "have" | "low" | "gone">,
): Spool[] {
  const decorated = spools.map((s, i) => ({ s, i }));

  const compare: Record<SortKey, (a: Spool, b: Spool) => number> = {
    date: (a, b) => a.orderDate.localeCompare(b.orderDate),
    material: (a, b) =>
      a.material.localeCompare(b.material) ||
      a.productLine.localeCompare(b.productLine),
    status: (a, b) =>
      STATUS_RANK[status[a.id] ?? "have"] - STATUS_RANK[status[b.id] ?? "have"],
    colour: (a, b) => {
      const fa = FAMILY_ORDER.indexOf(colourFamily(a));
      const fb = FAMILY_ORDER.indexOf(colourFamily(b));
      if (fa !== fb) return fa - fb;
      const ha = hexToHsl(a.hex);
      const hb = hexToHsl(b.hex);
      return ha.h - hb.h || ha.l - hb.l;
    },
  };

  // Index tiebreak keeps the sort stable and predictable across re-renders.
  return decorated
    .sort((x, y) => compare[key](x.s, y.s) || x.i - y.i)
    .map((d) => d.s);
}

export type Group = { family: ColourFamily; spools: Spool[] };

export function groupByColour(spools: Spool[]): Group[] {
  const buckets = new Map<ColourFamily, Spool[]>();
  for (const s of spools) {
    const f = colourFamily(s);
    const list = buckets.get(f);
    if (list) list.push(s);
    else buckets.set(f, [s]);
  }
  return FAMILY_ORDER.filter((f) => buckets.has(f)).map((family) => ({
    family,
    spools: buckets.get(family)!,
  }));
}
