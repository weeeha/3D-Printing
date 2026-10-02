"use client";

import { formatDuration, formatMm, totalGrams, type ModelRecord } from "@/lib/models";
import { formatCad, sliceCost } from "@/lib/model-cost";

/** Folders with sliced files first, then by name; a folder of refusals sinks to the bottom. */
function groups(models: ModelRecord[]) {
  const byFolder = new Map<string, ModelRecord[]>();
  for (const m of models) byFolder.set(m.folder, [...(byFolder.get(m.folder) ?? []), m]);
  const sliced = (ms: ModelRecord[]) => ms.filter((m) => m.slice.status === "sliced").length;
  return [...byFolder.entries()].sort(([a, am], [b, bm]) => sliced(bm) - sliced(am) || a.localeCompare(b));
}

function meta(m: ModelRecord) {
  if (m.slice.status === "failed") {
    return <><span className="text-[var(--warn)] group-aria-[current=true]:text-inherit">Not sliced</span>{` · ${m.slice.short}`}</>;
  }
  const cost = sliceCost(m.slice);
  return `${formatDuration(m.slice.seconds)} · ${formatMm(totalGrams(m.slice))} g${cost === null ? "" : ` · ${formatCad(cost)}`}`;
}

export function ModelList({ models, selected, onSelect }: { models: ModelRecord[]; selected: string | null; onSelect: (id: string) => void }) {
  return (
    <div className="flex flex-col gap-4.5">
      {groups(models).map(([folder, items]) => (
        <div key={folder} className="flex flex-col gap-1.5">
          <div className="flex items-baseline gap-2.5 text-[11px] uppercase tracking-[0.14em]">
            print/{folder} <span className="text-[10px] tracking-normal text-[var(--muted)]">{items.length}</span>
          </div>
          <div className="flex flex-col gap-px bg-[var(--rule)] border border-[var(--rule)]">
            {items.map((m) => {
              const current = m.id === selected;
              return (
                <button
                  key={m.id}
                  type="button"
                  aria-current={current}
                  onClick={() => onSelect(m.id)}
                  className={`group flex flex-col gap-0.5 w-full text-left px-3 py-2.5 ${current
                    ? "bg-[var(--ink)] text-[var(--ground)]"
                    : "bg-[var(--surface)] hover:bg-[var(--ground)]"}`}
                >
                  <span className="text-[12px] [overflow-wrap:anywhere]">{m.name}</span>
                  <span className={`text-[10px] ${current ? "opacity-75" : "text-[var(--muted)]"}`}>{meta(m)}</span>
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
