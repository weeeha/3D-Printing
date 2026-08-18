"use client";

import type { PrinterState } from "@/lib/printer";
import { LOW_THRESHOLD } from "@/lib/printer";

function ago(iso: string): string {
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs} h ago`;
  return `${Math.round(hrs / 24)} d ago`;
}

export function AmsStrip({
  state, onApply, applied,
}: {
  state: PrinterState;
  onApply: () => void;
  applied: boolean;
}) {
  return (
    <section className="flex flex-col gap-3 border border-[var(--rule)] p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <div className="flex flex-wrap items-baseline gap-3">
          <h2 className="text-[11px] uppercase tracking-[0.14em]">Loaded in the AMS</h2>
          <span className="text-[10.5px] text-[var(--muted)]">
            read {ago(state.readAt)}
            {state.ams.map((u) => ` · AMS ${"AB"[u.unit]} ${u.humidityRh}% RH`).join("")}
          </span>
        </div>
        <button
          type="button"
          onClick={onApply}
          disabled={applied}
          className="px-3 py-1.5 text-[11px] uppercase tracking-[0.12em] border
                     border-[var(--rule)] text-[var(--muted)] enabled:hover:text-[var(--ink)]
                     enabled:hover:border-[var(--muted)] disabled:opacity-45"
        >
          {applied ? "Reading applied" : "Apply printer reading"}
        </button>
      </div>

      {state.printing && (
        <p className="text-[11px] text-[var(--muted)]">
          Printing <span className="text-[var(--ink)]">{state.printing}</span>
          {state.percent !== null ? ` · ${state.percent}%` : ""}
        </p>
      )}

      <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(104px,1fr))]">
        {state.slots.map((s) => {
          const low = s.remain !== null && s.remain < LOW_THRESHOLD;
          return (
            <div key={s.slot} className="flex flex-col gap-1.5">
              <div className="flex items-center gap-2">
                <span
                  className="h-3.5 w-3.5 rounded-[2px] border border-[var(--rule)]"
                  style={{ background: s.hex ?? "transparent" }}
                />
                <span className="text-[11px]">{s.slot}</span>
                <span
                  className={`ml-auto text-[11px] ${low ? "text-[var(--warn)]" : "text-[var(--muted)]"}`}
                >
                  {s.remain === null ? "no tag" : `${s.remain}%`}
                </span>
              </div>
              {/* Remaining filament as a bar, the thing you actually scan for */}
              <div className="h-1 w-full bg-[var(--rule)]">
                <div
                  className={low ? "h-1 bg-[var(--warn)]" : "h-1 bg-[var(--accent)]"}
                  style={{ width: `${s.remain ?? 0}%` }}
                />
              </div>
              <span className="text-[10px] text-[var(--muted)] leading-tight">
                {s.productLine}
              </span>
            </div>
          );
        })}
      </div>

      <p className="text-[10.5px] text-[var(--muted)] leading-relaxed max-w-[70ch]">
        Percentages come from the printer&apos;s own RFID estimate and only exist for
        Bambu spools currently in the AMS. The other {70} spools on the shelf are a
        manual count. Applying the reading marks anything under {LOW_THRESHOLD}% as
        running low; you can still override any spool by clicking it.
      </p>
    </section>
  );
}
