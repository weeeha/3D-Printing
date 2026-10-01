"use client";

import { useRef } from "react";
import { VIEW_MODES, type ViewMode } from "@/lib/view-modes";

type Props = {
  mode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
  wireframe: boolean;
  onWireframeChange: (wireframe: boolean) => void;
};

const button = "px-3 py-1.5 text-[11px] uppercase tracking-[0.12em]";

/** Geometry / Surface / Realistic as a radio group (arrows move, one tab stop), plus Wireframe. */
export function ViewControls({ mode, onModeChange, wireframe, onWireframeChange }: Props) {
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  return (
    <div className="flex flex-wrap items-center gap-2">
      <div role="radiogroup" aria-label="View mode" className="flex border border-[var(--rule)]">
        {VIEW_MODES.map((m, i) => {
          const selected = m.id === mode;
          return (
            <button
              key={m.id}
              ref={(el) => { refs.current[i] = el; }}
              type="button"
              role="radio"
              aria-checked={selected}
              tabIndex={selected ? 0 : -1}
              onClick={() => onModeChange(m.id)}
              onKeyDown={(e) => {
                const step = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1
                  : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
                if (!step) return;
                e.preventDefault();
                const next = (i + step + VIEW_MODES.length) % VIEW_MODES.length;
                onModeChange(VIEW_MODES[next].id);
                refs.current[next]?.focus();
              }}
              className={`${button} ${selected
                ? "bg-[var(--ink)] text-[var(--ground)]"
                : "text-[var(--muted)] hover:text-[var(--ink)]"}`}
            >
              {m.label}
            </button>
          );
        })}
      </div>
      <button
        type="button"
        aria-pressed={wireframe}
        onClick={() => onWireframeChange(!wireframe)}
        className={`${button} border ${wireframe
          ? "border-[var(--accent)] text-[var(--accent)]"
          : "border-[var(--rule)] text-[var(--muted)] hover:text-[var(--ink)]"}`}
      >
        Wireframe
      </button>
    </div>
  );
}
