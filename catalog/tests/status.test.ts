import { describe, it, expect } from "vitest";
import { nextStatus, loadStatus, serialiseStatus, toStockCsv } from "@/lib/status";
import type { Spool } from "@/lib/spools";

const spool = (id: string, over: Partial<Spool> = {}): Spool =>
  ({
    id, source: "bambu", brand: "Bambu Lab", material: "PLA",
    productLine: "PLA Basic", colourName: "Red", colourCode: "10200",
    hex: "#C00D1E", finish: "basic", weightKg: 1, isRefill: false,
    orderId: "ca1", orderDate: "2024-01-01", pricePaidCad: 25.99, ...over,
  }) as Spool;

describe("status", () => {
  it("cycles have to low to gone and back", () => {
    expect(nextStatus("have")).toBe("low");
    expect(nextStatus("low")).toBe("gone");
    expect(nextStatus("gone")).toBe("have");
  });

  it("defaults every known spool to have when nothing is stored", () => {
    expect(loadStatus(null, ["a", "b"])).toEqual({ a: "have", b: "have" });
  });

  it("drops stored ids that no longer exist", () => {
    const raw = JSON.stringify({ a: "gone", removed: "low" });
    expect(loadStatus(raw, ["a", "b"])).toEqual({ a: "gone", b: "have" });
  });

  it("falls back to all-have on corrupt stored data", () => {
    expect(loadStatus("{not json", ["a"])).toEqual({ a: "have" });
  });

  it("ignores invalid status values in stored data", () => {
    expect(loadStatus(JSON.stringify({ a: "melted" }), ["a"])).toEqual({ a: "have" });
  });

  it("round-trips through serialise", () => {
    const m = { a: "gone" as const, b: "have" as const };
    expect(loadStatus(serialiseStatus(m), ["a", "b"])).toEqual(m);
  });

  it("exports one CSV row per spool plus a header", () => {
    const spools = [spool("a"), spool("b", { colourName: "Blue" })];
    const csv = toStockCsv(spools, { a: "gone", b: "have" }, "2026-08-17");
    const lines = csv.trim().split("\n");
    expect(lines[0]).toBe("id,colourName,material,source,status,exportedAt");
    expect(lines).toHaveLength(3);
    expect(lines[1]).toBe("a,Red,PLA,bambu,gone,2026-08-17");
  });

  it("quotes CSV fields containing a comma", () => {
    const csv = toStockCsv([spool("a", { colourName: "Green, Purple" })], { a: "have" }, "d");
    expect(csv.split("\n")[1]).toBe('a,"Green, Purple",PLA,bambu,have,d');
  });
});
