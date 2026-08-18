"use client";

import type { Material, Source } from "@/lib/spools";
import type { Status } from "@/lib/status";
import { STATUS_LABEL } from "@/lib/status";

export type FilterState = {
  materials: Material[];
  sources: Source[];
  statuses: Status[];
};

export const EMPTY_FILTERS: FilterState = { materials: [], sources: [], statuses: [] };

const MATERIALS: Material[] = ["PLA", "PETG", "PVA", "Support"];
const SOURCES: Source[] = ["bambu", "amazon"];
const STATUSES: Status[] = ["have", "low", "gone"];
const SOURCE_LABEL: Record<Source, string> = { bambu: "Bambu Lab", amazon: "Amazon" };

function toggle<T>(list: T[], v: T): T[] {
  return list.includes(v) ? list.filter((x) => x !== v) : [...list, v];
}

function Group<T extends string>({
  label, options, selected, onToggle, render,
}: {
  label: string;
  options: T[];
  selected: T[];
  onToggle: (v: T) => void;
  render: (v: T) => string;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-[10px] uppercase tracking-[0.14em] text-[var(--muted)] w-16 shrink-0">
        {label}
      </span>
      {options.map((o) => {
        const on = selected.includes(o);
        return (
          <button
            key={o}
            type="button"
            onClick={() => onToggle(o)}
            aria-pressed={on}
            className={`px-2.5 py-1 text-[11px] border transition-colors ${
              on
                ? "border-[var(--accent)] text-[var(--accent)]"
                : "border-[var(--rule)] text-[var(--muted)] hover:border-[var(--muted)]"
            }`}
          >
            {render(o)}
          </button>
        );
      })}
    </div>
  );
}

export function Filters({
  value, onChange, matchCount, total,
}: {
  value: FilterState;
  onChange: (v: FilterState) => void;
  matchCount: number;
  total: number;
}) {
  return (
    <div className="flex flex-col gap-3 border-y border-[var(--rule)] py-4">
      <Group label="Material" options={MATERIALS} selected={value.materials}
        onToggle={(m) => onChange({ ...value, materials: toggle(value.materials, m) })}
        render={(m) => m} />
      <Group label="Source" options={SOURCES} selected={value.sources}
        onToggle={(s) => onChange({ ...value, sources: toggle(value.sources, s) })}
        render={(s) => SOURCE_LABEL[s]} />
      <Group label="Status" options={STATUSES} selected={value.statuses}
        onToggle={(s) => onChange({ ...value, statuses: toggle(value.statuses, s) })}
        render={(s) => STATUS_LABEL[s]} />
      <div className="flex items-center gap-3 text-[11px] text-[var(--muted)]">
        <span>{matchCount} of {total} spools</span>
        {(value.materials.length || value.sources.length || value.statuses.length) > 0 && (
          <button type="button" onClick={() => onChange(EMPTY_FILTERS)}
            className="underline underline-offset-2 hover:text-[var(--ink)]">
            clear filters
          </button>
        )}
      </div>
    </div>
  );
}
