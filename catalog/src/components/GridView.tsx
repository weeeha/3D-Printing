"use client";

import type { Spool } from "@/lib/spools";
import type { Status } from "@/lib/status";
import { STATUS_LABEL } from "@/lib/status";
import { SpoolSvg } from "./Spool";

const STATUS_STYLE: Record<Status, string> = {
  have: "border-[var(--rule)] text-[var(--muted)]",
  low: "border-[var(--warn)] text-[var(--warn)]",
  gone: "border-[var(--muted)] text-[var(--muted)] line-through",
};

function price(p: number | null): string {
  return p === null ? "not captured" : `$${p.toFixed(2)}`;
}

import type { Section } from "./RackView";

export function GridView({
  sections, status, onToggle,
}: {
  sections: Section[];
  status: Record<string, Status>;
  onToggle: (id: string) => void;
}) {
  const total = sections.reduce((t, s) => t + s.spools.length, 0);
  if (total === 0) {
    return (
      <p className="py-16 text-center text-sm text-[var(--muted)]">
        No spools match these filters.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {sections.map((section) => (
        <div key={section.family ?? "all"} className="flex flex-col gap-2">
          {section.family && (
            <div className="flex items-baseline gap-3">
              <span className="text-[11px] uppercase tracking-[0.14em]">
                {section.family}
              </span>
              <span className="text-[10.5px] text-[var(--muted)]">
                {section.spools.length}
              </span>
            </div>
          )}
          <div className="grid gap-px bg-[var(--rule)] border border-[var(--rule)]
                          grid-cols-[repeat(auto-fill,minmax(210px,1fr))]">
            {section.spools.map((s) => {
        const st = status[s.id] ?? "have";
        return (
          <div key={s.id} className="bg-[var(--surface)] p-3 flex gap-3 items-start">
            <SpoolSvg spool={s} status={st} size={44} onClick={() => onToggle(s.id)} />
            <div className="min-w-0 flex flex-col gap-0.5">
              <span className="text-[12px] leading-tight break-words">{s.colourName}</span>
              <span className="text-[10.5px] text-[var(--muted)]">{s.productLine}</span>
              <span className="text-[10.5px] text-[var(--muted)]">
                {s.colourCode || s.brand} · {s.material} · {s.weightKg} kg
              </span>
              <span className="text-[10.5px] text-[var(--muted)]">
                {s.orderDate} · {price(s.pricePaidCad)}
              </span>
              <button
                type="button"
                onClick={() => onToggle(s.id)}
                className={`mt-1 self-start px-2 py-0.5 text-[10px] uppercase
                            tracking-[0.1em] border ${STATUS_STYLE[st]}`}
              >
                {STATUS_LABEL[st]}
              </button>
            </div>
          </div>
        );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
