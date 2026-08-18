"use client";

import type { Spool } from "@/lib/spools";
import type { Status } from "@/lib/status";
import { SpoolSvg } from "./Spool";

/**
 * The wall rack. Spools sit edge-on along horizontal rails, twelve to a row at
 * desktop width, fewer as the viewport narrows. Gone spools keep their slot so
 * the shelf shows the gap rather than silently reflowing.
 */
export function RackView({
  spools, status, onToggle,
}: {
  spools: Spool[];
  status: Record<string, Status>;
  onToggle: (id: string) => void;
}) {
  const rows: Spool[][] = [];
  for (let i = 0; i < spools.length; i += 12) rows.push(spools.slice(i, i + 12));

  if (spools.length === 0) {
    return (
      <p className="py-16 text-center text-sm text-[var(--muted)]">
        No spools match these filters.
      </p>
    );
  }

  return (
    <div className="flex flex-col">
      {rows.map((row, i) => (
        <div key={i} className="relative">
          <div className="grid gap-x-2 gap-y-1 justify-items-center items-end px-3 pb-2
                          grid-cols-[repeat(auto-fill,minmax(58px,1fr))]">
            {row.map((s) => (
              <SpoolSvg
                key={s.id}
                spool={s}
                status={status[s.id] ?? "have"}
                size={58}
                onClick={() => onToggle(s.id)}
              />
            ))}
          </div>
          {/* The rail the spools rest on */}
          <div className="h-2 w-full bg-[var(--rail)] rounded-[1px]" />
          <div className="h-6" />
        </div>
      ))}
    </div>
  );
}
