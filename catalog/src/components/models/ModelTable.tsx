"use client";

import { useState } from "react";
import {
  centredBox, clearance, formatDuration, formatMm, totalGrams, unionBox, type ModelRecord,
} from "@/lib/models";
import { formatCad, sliceCost } from "@/lib/model-cost";
import { groupByFolder, sortModels, type SortDir, type SortKey } from "@/lib/model-sort";

type Sort = { key: SortKey; dir: SortDir } | null;

const COLUMNS: { label: string; key?: SortKey; align?: "right" }[] = [
  { label: "Model", key: "name" },
  { label: "Print time", key: "time", align: "right" },
  { label: "Filament", key: "grams", align: "right" },
  { label: "Cost (CAD)", key: "cost", align: "right" },
  { label: "Size (mm)", align: "right" },
  { label: "Clearance", align: "right" },
  { label: "Settings" },
];

const SortArrow = ({ active, dir }: { active: boolean; dir?: SortDir }) => (
  <span aria-hidden className={`inline-block w-3 text-center ${active ? "" : "invisible"}`}>{dir === "asc" ? "↑" : "↓"}</span>
);

function clearanceOf(m: ModelRecord): number {
  if (m.slice.status === "sliced") return clearance(unionBox(m.slice.plate));
  return clearance(m.slice.footprint ?? centredBox(m.size));
}

/** All print files as a table; headers with a key sort it, and a row opens that file in the viewer. */
export function ModelTable({ models, onOpen }: { models: ModelRecord[]; onOpen: (id: string) => void }) {
  // Unsorted means the gallery's folder order, so the two overviews read the same.
  const [sort, setSort] = useState<Sort>(null);
  const rows = sort ? sortModels(models, sort.key, sort.dir) : groupByFolder(models).flatMap(([, items]) => items);
  const toggle = (key: SortKey) =>
    setSort((s) => (s?.key === key ? { key, dir: s.dir === "asc" ? "desc" : "asc" } : { key, dir: key === "name" ? "asc" : "desc" }));
  const cell = "px-3 py-2.5 border-t border-[var(--rule)]";

  return (
    <div className="overflow-x-auto border border-[var(--rule)] bg-[var(--surface)]">
      <table className="w-full min-w-[760px] border-collapse text-[12px]">
        <thead>
          <tr>
            {COLUMNS.map((c) => (
              <th
                key={c.label}
                scope="col"
                aria-sort={c.key && sort?.key === c.key ? (sort.dir === "asc" ? "ascending" : "descending") : undefined}
                className={`px-3 py-2 font-normal text-[10px] uppercase tracking-[0.14em] text-[var(--muted)] ${c.align === "right" ? "text-right" : "text-left"}`}
              >
                {c.key ? (
                  <button type="button" onClick={() => toggle(c.key!)} className="uppercase tracking-[0.14em] hover:text-[var(--ink)]">
                    {/* The arrow's space is always reserved, on the outer side, so sorting never shifts a
                        header and right-aligned headers still line up with their numbers. */}
                    {c.align === "right" && <SortArrow active={sort?.key === c.key} dir={sort?.dir} />}
                    {c.label}
                    {c.align !== "right" && <SortArrow active={sort?.key === c.key} dir={sort?.dir} />}
                  </button>
                ) : c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((m) => {
            const s = m.slice;
            const sliced = s.status === "sliced";
            const cost = sliced ? sliceCost(s) : null;
            const clear = clearanceOf(m);
            return (
              <tr key={m.id} onClick={() => onOpen(m.id)} className="cursor-pointer hover:bg-[var(--ground)]">
                <td className={cell}>
                  <button type="button" onClick={(e) => { e.stopPropagation(); onOpen(m.id); }} className="text-left [overflow-wrap:anywhere] hover:underline">
                    {m.name}
                  </button>
                  <div className="text-[10px] text-[var(--muted)]">print/{m.folder} · {m.parts} {m.parts === 1 ? "part" : "parts"}</div>
                </td>
                <td className={`${cell} text-right`}>
                  {sliced ? formatDuration(s.seconds) : <span className="text-[var(--warn)]">Not sliced<span className="block text-[10px]">{s.short}</span></span>}
                </td>
                <td className={`${cell} text-right`}>{sliced ? `${formatMm(totalGrams(s))} g` : "–"}</td>
                <td className={`${cell} text-right`}>{cost === null ? "–" : formatCad(cost)}</td>
                <td className={`${cell} text-right whitespace-nowrap`}>{m.size.map(formatMm).join(" × ")}</td>
                <td className={`${cell} text-right ${clear < 0.5 ? "text-[var(--warn)]" : ""}`}>{clear < 0.5 ? "none" : `${formatMm(clear)} mm`}</td>
                <td className={`${cell} text-[var(--muted)]`}>{m.settingsSource === "file" ? "From the file" : "P1S defaults"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
