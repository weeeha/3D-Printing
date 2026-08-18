import { describe, it, expect } from "vitest";
import { COLOURS, lookupColour } from "@/lib/colours.mjs";

describe("colours", () => {
  it("resolves a Bambu colour code to a hex and finish", () => {
    expect(lookupColour("11101")).toEqual({ hex: "#1A1A1A", finish: "matte" });
  });

  it("resolves a third-party key by brand, line and colour name", () => {
    expect(lookupColour("creality:hyper pla:grey")).toEqual({
      hex: "#8A8F92",
      finish: "basic",
    });
  });

  it("gives dual-colour swatches a second stop", () => {
    const s = lookupColour("gilded rose");
    expect(s?.finish).toBe("dual");
    expect(s?.hex2).toBeTruthy();
  });

  it("returns undefined for an unknown key", () => {
    expect(lookupColour("nope")).toBeUndefined();
  });

  it("gives every entry a valid hex and finish", () => {
    const finishes = new Set([
      "basic", "matte", "silk", "sparkle", "translucent",
      "dual", "rainbow", "glow", "marble",
    ]);
    for (const [key, s] of Object.entries(COLOURS)) {
      expect(s.hex, key).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(finishes.has(s.finish), `${key} finish ${s.finish}`).toBe(true);
      if (s.finish === "dual") expect(s.hex2, key).toMatch(/^#[0-9A-Fa-f]{6}$/);
    }
  });

  it("keys are all lowercase so lookup is case-insensitive", () => {
    for (const key of Object.keys(COLOURS)) {
      expect(key).toBe(key.toLowerCase());
    }
  });
});
