"use client";

import type { Spool } from "@/lib/spools";
import type { Status } from "@/lib/status";
import { SpoolSvg } from "./Spool";

/**
 * The wall rack. Spools sit edge-on along horizontal rails, twelve to a row at
 * desktop width, fewer as the viewport narrows. Gone spools keep their slot so
 * the shelf shows the gap rather than silently reflowing.
 */
export type Section = { family: string | null; spools: Spool[] };

function Shelf({ spools, status, onToggle }: {
  spools: Spool[];
  status: Record<string, Status>;
  onToggle: (id: string) => void;
}) {
  const rows: Spool[][] = [];
  for (let i = 0; i < spools.length; i += 12) rows.push(spools.slice(i, i + 12));
  return (
    <>
      {rows.map((row, i) => (
        <div key={i} className="relative">
          <div className="grid gap-x-2 gap-y-1 justify-items-center items-end px-3 pb-2
                          grid-cols-[repeat(auto-fill,minmax(58px,1fr))]">
            {row.map((s) => (
              <SpoolSvg key={s.id} spool={s} status={status[s.id] ?? "have"}
                size={58} onClick={() => onToggle(s.id)} />
            ))}
          </div>
          <div className="h-2 w-full bg-[var(--rail)] rounded-[1px]" />
          <div className="h-6" />
        </div>
      ))}
    </>
  );
}

export function RackView({
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
    <div className="flex flex-col">
      {sections.map((section) => (
        <div key={section.family ?? "all"} className="flex flex-col">
          {section.family && (
            <div className="flex items-baseline gap-3 pb-2">
              <span className="text-[11px] uppercase tracking-[0.14em]">
                {section.family}
              </span>
              <span className="text-[10.5px] text-[var(--muted)]">
                {section.spools.length}
              </span>
            </div>
          )}
          <Shelf spools={section.spools} status={status} onToggle={onToggle} />
        </div>
      ))}
    </div>
  );
}
