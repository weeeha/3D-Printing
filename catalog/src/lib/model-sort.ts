import { totalGrams, type ModelRecord } from "@/lib/models";
import { sliceCost } from "@/lib/model-cost";

export type SortKey = "name" | "time" | "grams" | "cost";
export type SortDir = "asc" | "desc";

/** Folders with sliced files first, then by name; a folder of refusals sinks to the bottom. */
export function groupByFolder(models: ModelRecord[]): [string, ModelRecord[]][] {
  const byFolder = new Map<string, ModelRecord[]>();
  for (const m of models) byFolder.set(m.folder, [...(byFolder.get(m.folder) ?? []), m]);
  const sliced = (ms: ModelRecord[]) => ms.filter((m) => m.slice.status === "sliced").length;
  return [...byFolder.entries()].sort(([a, am], [b, bm]) => sliced(bm) - sliced(am) || a.localeCompare(b));
}

function value(m: ModelRecord, key: Exclude<SortKey, "name">): number | null {
  if (m.slice.status !== "sliced") return null;
  if (key === "time") return m.slice.seconds;
  if (key === "grams") return totalGrams(m.slice);
  return sliceCost(m.slice);
}

/** A sorted copy. Files without a slice have no time, weight or cost, so they stay last either way. */
export function sortModels(models: ModelRecord[], key: SortKey, dir: SortDir): ModelRecord[] {
  const sign = dir === "asc" ? 1 : -1;
  return [...models].sort((a, b) => {
    if (key === "name") return sign * a.name.localeCompare(b.name, undefined, { sensitivity: "base" });
    const va = value(a, key), vb = value(b, key);
    if (va === null || vb === null) return va === vb ? 0 : va === null ? 1 : -1;
    return sign * (va - vb);
  });
}
