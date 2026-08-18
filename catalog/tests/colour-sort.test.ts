import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  hexToHsl, colourFamily, sortSpools, groupByColour, FAMILY_ORDER,
} from "@/lib/colour-sort";
import type { Spool } from "@/lib/spools";
import { buildSpools } from "../scripts/build-spools.mjs";

const sp = (over: Partial<Spool>): Spool =>
  ({
    id: over.hex ?? "x", source: "bambu", brand: "Bambu Lab", material: "PLA",
    productLine: "PLA Basic", colourName: "X", colourCode: "", hex: "#000000",
    finish: "basic", weightKg: 1, isRefill: false, orderId: "o",
    orderDate: "2024-01-01", pricePaidCad: 1, ...over,
  }) as Spool;

describe("hexToHsl", () => {
  it("reads pure red, green and blue", () => {
    expect(Math.round(hexToHsl("#FF0000").h)).toBe(0);
    expect(Math.round(hexToHsl("#00FF00").h)).toBe(120);
    expect(Math.round(hexToHsl("#0000FF").h)).toBe(240);
  });

  it("gives greys zero saturation", () => {
    expect(hexToHsl("#808080").s).toBe(0);
  });
});

describe("colourFamily", () => {
  const cases: [string, string][] = [
    ["#C00D1E", "Red"], ["#FF6A13", "Orange"], ["#F4EE2A", "Yellow"],
    ["#3F8E43", "Green"], ["#0086D6", "Blue"], ["#8E4EC6", "Purple"],
    ["#EC008C", "Pink"], ["#FFFFFF", "White"], ["#1A1A1A", "Black"],
    ["#8A8F92", "Neutral"],
  ];
  for (const [hex, family] of cases) {
    it(`puts ${hex} in ${family}`, () => {
      expect(colourFamily(sp({ hex }))).toBe(family);
    });
  }

  it("files a near-white translucent spool under White, not a hue", () => {
    expect(colourFamily(sp({ hex: "#EBF0EE", finish: "translucent" }))).toBe("White");
  });

  it("files rainbow and dual-colour rolls under Multi", () => {
    expect(colourFamily(sp({ hex: "#E24B4B", finish: "rainbow" }))).toBe("Multi");
    expect(colourFamily(sp({ hex: "#2E7BD6", hex2: "#D42E9E", finish: "dual" }))).toBe("Multi");
  });
});

describe("sortSpools", () => {
  it("orders by colour family, spectrum first", () => {
    const spools = [sp({ hex: "#0086D6" }), sp({ hex: "#C00D1E" }), sp({ hex: "#F4EE2A" })];
    const out = sortSpools(spools, "colour", {});
    expect(out.map((s) => colourFamily(s))).toEqual(["Red", "Yellow", "Blue"]);
  });

  it("is stable for spools of equal rank", () => {
    const a = sp({ hex: "#C00D1E", id: "a" });
    const b = sp({ hex: "#C00D1E", id: "b" });
    expect(sortSpools([a, b], "colour", {}).map((s) => s.id)).toEqual(["a", "b"]);
    expect(sortSpools([b, a], "colour", {}).map((s) => s.id)).toEqual(["b", "a"]);
  });

  it("orders by status have, low, then gone", () => {
    const a = sp({ id: "a" }), b = sp({ id: "b" }), c = sp({ id: "c" });
    const out = sortSpools([c, b, a], "status", { a: "have", b: "low", c: "gone" });
    expect(out.map((s) => s.id)).toEqual(["a", "b", "c"]);
  });

  it("does not mutate the input array", () => {
    const spools = [sp({ hex: "#0086D6", id: "a" }), sp({ hex: "#C00D1E", id: "b" })];
    const before = spools.map((s) => s.id);
    sortSpools(spools, "colour", {});
    expect(spools.map((s) => s.id)).toEqual(before);
  });
});

describe("groupByColour", () => {
  it("returns groups in spectrum order and drops empty families", () => {
    const spools = [sp({ hex: "#0086D6" }), sp({ hex: "#C00D1E" })];
    expect(groupByColour(spools).map((g) => g.family)).toEqual(["Red", "Blue"]);
  });

  it("accounts for every real spool exactly once", () => {
    const all = buildSpools(
      readFileSync(resolve(__dirname, "../../printer/orders.csv"), "utf8"),
      readFileSync(resolve(__dirname, "../../printer/orders-amazon.csv"), "utf8"),
    ) as Spool[];
    const groups = groupByColour(all);
    expect(groups.reduce((t, g) => t + g.spools.length, 0)).toBe(78);
    for (const g of groups) expect(FAMILY_ORDER).toContain(g.family);
  });
});
