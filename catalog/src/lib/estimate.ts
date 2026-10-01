import type { ModelRecord, Sliced } from "@/lib/models";

/** Lowest and highest ratios seen across this repo's own slices. */
export type Calibration = {
  gPerCm3: [number, number];
  minPerG: [number, number];
  basedOn: string[];
};

/**
 * A dropped file has a mesh but no slice, so its grams and time are a range
 * scaled from slices that print the way it would: one filament, 0.4 mm
 * nozzle, 0.20 mm layers. Multi-colour plates and fine-nozzle tests are left
 * out because prime towers and 0.08 mm layers skew both ratios.
 */
export function calibrate(models: ModelRecord[]): Calibration | null {
  const points = models.flatMap((m) => {
    const s = m.slice;
    if (s.status !== "sliced" || s.filaments.length !== 1 || m.volumeCm3 <= 0) return [];
    if (s.settings.nozzle !== 0.4 || s.settings.layer !== 0.2) return [];
    return [{ name: m.name, s, volume: m.volumeCm3 }];
  });
  if (points.length < 2) return null;
  const grams = (s: Sliced) => s.filaments[0].grams;
  const g = points.map((p) => grams(p.s) / p.volume);
  const t = points.map((p) => p.s.seconds / 60 / grams(p.s));
  return {
    gPerCm3: [Math.min(...g), Math.max(...g)],
    minPerG: [Math.min(...t), Math.max(...t)],
    basedOn: points.map((p) => p.name),
  };
}

export function estimate(volumeCm3: number, cal: Calibration) {
  const grams: [number, number] = [volumeCm3 * cal.gPerCm3[0], volumeCm3 * cal.gPerCm3[1]];
  const seconds: [number, number] = [grams[0] * cal.minPerG[0] * 60, grams[1] * cal.minPerG[1] * 60];
  return { grams, seconds };
}
