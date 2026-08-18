import type { Spool } from "./spools";

export type Status = "have" | "low" | "gone";

export const STORAGE_KEY = "filament-shelf-status-v1";

const ORDER: Status[] = ["have", "low", "gone"];
const VALID = new Set<string>(ORDER);

export const STATUS_LABEL: Record<Status, string> = {
  have: "Have",
  low: "Running low",
  gone: "Gone",
};

export function nextStatus(s: Status): Status {
  return ORDER[(ORDER.indexOf(s) + 1) % ORDER.length];
}

/**
 * Pure so it can be tested without a DOM: the component layer reads
 * localStorage and passes the raw string in.
 *
 * Unknown ids are dropped and unknown values fall back to "have", so adding
 * spools to the ledger later never corrupts an existing saved count.
 */
export function loadStatus(
  raw: string | null,
  validIds: string[],
): Record<string, Status> {
  let stored: Record<string, unknown> = {};
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        stored = parsed as Record<string, unknown>;
      }
    } catch {
      stored = {};
    }
  }
  const out: Record<string, Status> = {};
  for (const id of validIds) {
    const v = stored[id];
    out[id] = typeof v === "string" && VALID.has(v) ? (v as Status) : "have";
  }
  return out;
}

export function serialiseStatus(map: Record<string, Status>): string {
  return JSON.stringify(map);
}

const cell = (v: string) => (/[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v);

export function toStockCsv(
  spools: Spool[],
  map: Record<string, Status>,
  exportedAt: string,
): string {
  const header = "id,colourName,material,source,status,exportedAt";
  const rows = spools.map((s) =>
    [s.id, s.colourName, s.material, s.source, map[s.id] ?? "have", exportedAt]
      .map((v) => cell(String(v)))
      .join(","),
  );
  return [header, ...rows].join("\n") + "\n";
}
