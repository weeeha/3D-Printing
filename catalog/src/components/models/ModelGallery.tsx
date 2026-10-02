"use client";

import { ModelMeta } from "./ModelMeta";
import { formatMm, type ModelRecord } from "@/lib/models";
import { groupByFolder } from "@/lib/model-sort";

/**
 * Every print file as a card with Bambu Studio's plate thumbnail, grouped by
 * print/ folder. The thumbnails have transparent backgrounds, so they sit on
 * the page surface in light and dark alike.
 */
export function ModelGallery({ models, onOpen }: { models: ModelRecord[]; onOpen: (id: string) => void }) {
  return (
    <div className="flex flex-col gap-8">
      {groupByFolder(models).map(([folder, items]) => (
        <section key={folder} aria-label={`print/${folder}`} className="flex flex-col gap-2.5">
          <div className="flex items-baseline gap-2.5 text-[11px] uppercase tracking-[0.14em]">
            print/{folder} <span className="text-[10px] tracking-normal text-[var(--muted)]">{items.length}</span>
          </div>
          <div className="grid gap-3 grid-cols-2 sm:grid-cols-[repeat(auto-fill,minmax(176px,1fr))]">
            {items.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => onOpen(m.id)}
                className="flex flex-col text-left border border-[var(--rule)] bg-[var(--surface)] hover:border-[var(--muted)]"
              >
                <div className="aspect-square flex items-center justify-center p-3">
                  {m.thumbnail ? (
                    // eslint-disable-next-line @next/next/no-img-element -- static export, no image optimiser
                    <img src={`/models/${m.id}.png`} alt="" loading="lazy" className="block max-w-full max-h-full object-contain" />
                  ) : (
                    <span className="text-[11px] text-[var(--muted)]">No preview</span>
                  )}
                </div>
                <div className="flex flex-col gap-0.5 px-3 pb-3 pt-2 border-t border-[var(--rule)]">
                  <span className="text-[12px] [overflow-wrap:anywhere]">{m.name}</span>
                  <span className="text-[10px] text-[var(--muted)]"><ModelMeta m={m} /></span>
                  <span className="text-[10px] text-[var(--muted)]">{m.size.map(formatMm).join(" × ")} mm</span>
                </div>
              </button>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
