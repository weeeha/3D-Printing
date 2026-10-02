import { describe, it, expect } from "vitest";
import rawSpools from "@/data/spools.json";
import type { Spool } from "@/lib/spools";
import {
  MODELS, centredBox, clearance, formatDuration, unionBox, type ModelRecord, type Sliced,
} from "@/lib/models";
import { costCad, priceFor } from "@/lib/prices";
import { calibrate, estimate } from "@/lib/estimate";

const SPOOLS = rawSpools as Spool[];
const byId = (id: string) => MODELS.models.find((m) => m.id === id) as ModelRecord;

describe("formatDuration", () => {
  it("prints minutes under an hour and h mm above", () => {
    expect(formatDuration(2945)).toBe("49m");
    expect(formatDuration(13211)).toBe("3h 40m");
    expect(formatDuration(23410)).toBe("6h 30m");
    expect(formatDuration(3600)).toBe("1h 00m");
    expect(formatDuration(20)).toBe("1m");
  });
});

describe("bed geometry", () => {
  it("measures clearance to the nearest bed edge, prime tower included", () => {
    const kit = byId("kit-9cubes-parts").slice as Sliced;
    expect(clearance(unionBox(kit.plate))).toBeCloseTo(11.7, 1);
  });

  it("centres an unsliced part, and a 256 mm part has no clearance", () => {
    expect(centredBox([256, 200, 4])).toEqual([0, 28, 256, 228]);
    expect(clearance(centredBox([256, 200, 4]))).toBe(0);
  });
});

describe("priceFor", () => {
  it("uses the median paid for the same product line", () => {
    expect(priceFor(SPOOLS, "PLA Matte", "PLA")).toEqual({ line: "PLA Matte", perKg: 12.99, spools: 19, matched: true });
    expect(priceFor(SPOOLS, "PLA Basic", "PLA")).toEqual({ line: "PLA Basic", perKg: 25.99, spools: 8, matched: true });
  });

  it("falls back to the material median for a line never bought", () => {
    expect(priceFor(SPOOLS, "PLA Glow", "PLA")).toEqual({ line: "PLA Glow", perKg: 25.99, spools: 43, matched: false });
  });

  it("ignores spools with no recorded price and gives up on unknown materials", () => {
    const amazonOnly = SPOOLS.filter((s) => s.pricePaidCad === null);
    expect(priceFor(amazonOnly, "PLA Basic", "PLA")).toBeNull();
    expect(priceFor(SPOOLS, "TPU 95A", "TPU")).toBeNull();
  });

  it("prices grams in CAD", () => {
    expect(costCad(40.3, 25.99)).toBeCloseTo(1.047, 3);
  });
});

describe("estimate for a dropped file", () => {
  const cal = calibrate(MODELS.models);

  it("calibrates on single-colour 0.4 mm, 0.20 mm-layer slices only", () => {
    expect(cal?.basedOn).toEqual(["smallclock_cradle", "smallclock_lid", "smallclock_shell"]);
    const [lo, hi] = cal!.gPerCm3;
    expect(lo).toBeLessThan(hi);
    const cradle = byId("smallclock-cradle");
    expect(lo).toBeCloseTo((cradle.slice as Sliced).filaments[0].grams / cradle.volumeCm3, 6);
  });

  it("gives ranges that scale with volume", () => {
    const e = estimate(10, cal!);
    expect(e.grams).toEqual([10 * cal!.gPerCm3[0], 10 * cal!.gPerCm3[1]]);
    expect(e.seconds[0]).toBeCloseTo(e.grams[0] * cal!.minPerG[0] * 60, 6);
    expect(e.seconds[1]).toBeCloseTo(e.grams[1] * cal!.minPerG[1] * 60, 6);
  });

  it("refuses to calibrate on fewer than two slices", () => {
    expect(calibrate(MODELS.models.filter((m) => m.id === "smallclock-shell"))).toBeNull();
  });
});
