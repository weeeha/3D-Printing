import { describe, it, expect } from "vitest";
import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import committed from "@/data/models.json";

/**
 * models.json and public/models/ are committed so Vercel can build from
 * catalog/ alone, and they come from `npm run slice`, which needs Bambu
 * Studio on the Mac. This test is the alarm: change a print file without
 * re-slicing and it fails.
 */
const REPO = resolve(__dirname, "../..");
const sha256 = (path: string) => createHash("sha256").update(readFileSync(path)).digest("hex");

function printFiles(dir = join(REPO, "print")): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? printFiles(join(dir, e.name)) : e.name.endsWith(".3mf") ? [join(dir, e.name)] : [],
  );
}

describe("committed models.json", () => {
  const files = printFiles().map((p) => relative(REPO, p)).sort();

  it("has one record per print file", () => {
    expect(committed.models.map((m) => m.file).sort()).toEqual(files);
  });

  it("was sliced from the current version of each file", () => {
    for (const m of committed.models) {
      expect(m.sha256, `${m.file} changed since the last npm run slice`).toBe(sha256(join(REPO, m.file)));
    }
  });

  it("ships a byte copy of each file in public/models", () => {
    for (const m of committed.models) {
      expect(sha256(join(REPO, "catalog/public/models", `${m.id}.3mf`)), m.id).toBe(m.sha256);
    }
    expect(readdirSync(join(REPO, "catalog/public/models")).sort())
      .toEqual(committed.models.map((m) => `${m.id}.3mf`).sort());
  });
});
