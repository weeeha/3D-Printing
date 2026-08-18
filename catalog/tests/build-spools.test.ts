import { describe, it, expect, beforeAll } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { buildSpools } from "../scripts/build-spools.mjs";

const FINISHES = new Set([
  "basic", "matte", "silk", "sparkle", "translucent",
  "dual", "rainbow", "glow", "marble",
]);

let spools: any[];

beforeAll(() => {
  spools = buildSpools(
    readFileSync(resolve(__dirname, "../../printer/orders.csv"), "utf8"),
    readFileSync(resolve(__dirname, "../../printer/orders-amazon.csv"), "utf8"),
  );
});

describe("buildSpools", () => {
  it("yields exactly 78 spools", () => {
    expect(spools).toHaveLength(78);
  });

  it("splits 59 Bambu and 19 Amazon", () => {
    expect(spools.filter((s) => s.source === "bambu")).toHaveLength(59);
    expect(spools.filter((s) => s.source === "amazon")).toHaveLength(19);
  });

  it("totals 57 kg Bambu and 19 kg Amazon", () => {
    const kg = (src: string) =>
      spools.filter((s) => s.source === src).reduce((t, s) => t + s.weightKg, 0);
    expect(kg("bambu")).toBeCloseTo(57, 5);
    expect(kg("amazon")).toBeCloseTo(19, 5);
  });

  it("expands the 10-roll matte pack into 10 spools, 5 and 5", () => {
    const pack = spools.filter(
      (s) => s.orderId === "ca644191913257447425" && s.productLine === "PLA Matte",
    );
    expect(pack).toHaveLength(10);
    expect(pack.filter((s) => s.colourCode === "11100")).toHaveLength(5);
    expect(pack.filter((s) => s.colourCode === "11101")).toHaveLength(5);
  });

  it("expands the CMYK bundle into 4 spools", () => {
    expect(
      spools.filter((s) => s.productLine === "PLA CMYK Lithophane Bundle"),
    ).toHaveLength(4);
  });

  it("keeps the TRONXY glow bundle as one 1 kg spool", () => {
    const t = spools.filter((s) => s.brand === "TRONXY");
    expect(t).toHaveLength(1);
    expect(t[0].weightKg).toBe(1);
  });

  it("excludes hardware, hotends, accessories and the glue", () => {
    const names = spools.map((s) => s.productLine.toLowerCase()).join("|");
    expect(names).not.toContain("hotend");
    expect(names).not.toContain("scraper");
    expect(names).not.toContain("adhesive");
    expect(names).not.toContain("enclosure");
    expect(names).not.toContain("desiccant");
  });

  it("gives every spool a unique id, a hex and a valid finish", () => {
    expect(new Set(spools.map((s) => s.id)).size).toBe(78);
    for (const s of spools) {
      expect(s.hex, s.id).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(FINISHES.has(s.finish), `${s.id} ${s.finish}`).toBe(true);
    }
  });

  it("leaves every Amazon price null and every Bambu price a number", () => {
    for (const s of spools) {
      if (s.source === "amazon") expect(s.pricePaidCad, s.id).toBeNull();
      else expect(typeof s.pricePaidCad, s.id).toBe("number");
    }
  });

  it("counts 4 half-kilo support spools on the Bambu side", () => {
    const half = spools.filter((s) => s.weightKg === 0.5);
    expect(half).toHaveLength(4);
    expect(half.every((s) => s.source === "bambu")).toBe(true);
  });
});
