import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { buildSpools } from "../scripts/build-spools.mjs";
import committed from "@/data/spools.json";

/**
 * spools.json is committed so that Vercel can build from catalog/ alone,
 * without reaching up into printer/. That means it can drift from the CSVs.
 * This test is the alarm: edit a ledger without running `npm run build:data`
 * and it fails.
 */
describe("committed spools.json", () => {
  it("matches a fresh build from the CSV ledgers", () => {
    const fresh = buildSpools(
      readFileSync(resolve(__dirname, "../../printer/orders.csv"), "utf8"),
      readFileSync(resolve(__dirname, "../../printer/orders-amazon.csv"), "utf8"),
    );
    expect(committed).toEqual(fresh);
  });
});
