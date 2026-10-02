"use client";

import { ModelMeta } from "./ModelMeta";
import type { ModelRecord } from "@/lib/models";
import { groupByFolder } from "@/lib/model-sort";

/** The viewer's compact file list, grouped by print/ folder. */
export function ModelList({ models, selected, onSelect }: { models: ModelRecord[]; selected: string | null; onSelect: (id: string) => void }) {
  return (
    <div className="flex flex-col gap-4.5">
      {groupByFolder(models).map(([folder, items]) => (
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
                  className={`flex flex-col gap-0.5 w-full text-left px-3 py-2.5 ${current
                    ? "bg-[var(--ink)] text-[var(--ground)]"
                    : "bg-[var(--surface)] hover:bg-[var(--ground)]"}`}
                >
                  <span className="text-[12px] [overflow-wrap:anywhere]">{m.name}</span>
                  <span className={`text-[10px] ${current ? "opacity-75" : "text-[var(--muted)]"}`}>
                    <ModelMeta m={m} onInk={current} />
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
