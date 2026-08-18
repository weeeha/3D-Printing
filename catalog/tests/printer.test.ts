import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  statusFromRemain, matchSlots, derivedStatuses, LOW_THRESHOLD,
  type PrinterState, type PrinterSlot,
} from "@/lib/printer";
import type { Spool } from "@/lib/spools";
import { toPrinterState } from "../scripts/read-printer.mjs";

const sp = (id: string, productLine: string, hex: string): Spool =>
  ({
    id, source: "bambu", brand: "Bambu Lab", material: "PLA", productLine,
    colourName: "X", colourCode: "", hex, finish: "basic", weightKg: 1,
    isRefill: false, orderId: "o", orderDate: "2024-01-01", pricePaidCad: 1,
  }) as Spool;

const slot = (o: Partial<PrinterSlot>): PrinterSlot =>
  ({ slot: "A1", uuid: "u", sku: "", productLine: "PLA Matte", material: "PLA",
     hex: "#000000", remain: 50, ...o });

describe("statusFromRemain", () => {
  it("maps zero to gone, low values to low, healthy values to have", () => {
    expect(statusFromRemain(0)).toBe("gone");
    expect(statusFromRemain(LOW_THRESHOLD - 1)).toBe("low");
    expect(statusFromRemain(LOW_THRESHOLD)).toBe("have");
    expect(statusFromRemain(100)).toBe("have");
  });

  it("returns null when there is no RFID reading, rather than guessing", () => {
    expect(statusFromRemain(null)).toBeNull();
  });
});

describe("matchSlots", () => {
  it("never assigns the same spool to two slots", () => {
    const spools = [sp("a", "PLA Matte", "#FFFFFF"), sp("b", "PLA Matte", "#FFFFFF")];
    const m = matchSlots(
      [slot({ slot: "A2", hex: "#FFFFFF" }), slot({ slot: "B4", hex: "#FFFFFF" })],
      spools,
    );
    expect(new Set(Object.values(m)).size).toBe(2);
    expect(m.A2).not.toBe(m.B4);
  });

  it("prefers a product-line match over colour alone", () => {
    const spools = [sp("petg", "PETG Basic", "#0086D6"), sp("pla", "PLA Basic", "#0086D6")];
    const m = matchSlots([slot({ productLine: "PLA Basic", hex: "#0086D6" })], spools);
    expect(m.A1).toBe("pla");
  });

  it("falls back to colour when the product line does not line up", () => {
    const spools = [sp("only", "PLA CMYK Lithophane Bundle", "#0086D6")];
    const m = matchSlots([slot({ productLine: "PLA Basic", hex: "#0086D6" })], spools);
    expect(m.A1).toBe("only");
  });

  it("skips a slot with no colour rather than mis-assigning", () => {
    expect(matchSlots([slot({ hex: null })], [sp("a", "PLA Matte", "#000000")])).toEqual({});
  });

  it("leaves slots unmatched when nothing in the ledger fits", () => {
    expect(matchSlots([slot({ hex: "#123456" })], [sp("a", "PLA Matte", "#000000")])).toEqual({});
  });
});

describe("against the real printer reading", () => {
  const state = JSON.parse(
    readFileSync(resolve(__dirname, "../src/data/printer-state.json"), "utf8"),
  ) as PrinterState;
  const spools = JSON.parse(
    readFileSync(resolve(__dirname, "../src/data/spools.json"), "utf8"),
  ) as Spool[];

  it("reads 8 AMS slots", () => {
    expect(state.slots).toHaveLength(8);
  });

  it("matches every slot to a distinct ledger spool", () => {
    const m = matchSlots(state.slots, spools);
    expect(Object.keys(m)).toHaveLength(8);
    expect(new Set(Object.values(m)).size).toBe(8);
  });

  it("derives low only below the threshold, so 29% and 26% flip but 34% does not", () => {
    const d = derivedStatuses(state, spools);
    expect(Object.values(d).filter((s) => s === "low")).toHaveLength(2);
    expect(Object.values(d).filter((s) => s === "have")).toHaveLength(6);
  });
});

describe("toPrinterState", () => {
  it("treats remain of -1 as no reading rather than zero", () => {
    const out = toPrinterState(
      { print: { ams: { ams: [{ id: "0", tray: [{ id: "0", remain: -1, tray_color: "FFFFFFFF" }] }] } } },
      "2026-08-17T00:00:00Z",
    );
    expect(out.slots[0].remain).toBeNull();
  });

  it("rejects a malformed colour instead of emitting a broken hex", () => {
    const out = toPrinterState(
      { print: { ams: { ams: [{ id: "0", tray: [{ id: "0", tray_color: "" }] }] } } },
      "2026-08-17T00:00:00Z",
    );
    expect(out.slots[0].hex).toBeNull();
  });
});
