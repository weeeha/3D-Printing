"use client";

import { useEffect, useMemo, useState } from "react";
import rawSpools from "@/data/spools.json";
import type { Spool } from "@/lib/spools";
import {
  STORAGE_KEY, loadStatus, serialiseStatus, nextStatus, toStockCsv,
  type Status,
} from "@/lib/status";
import { Filters, EMPTY_FILTERS, type FilterState } from "@/components/Filters";
import { RackView, type Section } from "@/components/RackView";
import { GridView } from "@/components/GridView";
import { sortSpools, groupByColour, type SortKey } from "@/lib/colour-sort";
import { ThemeToggle } from "@/components/ThemeToggle";

const SPOOLS = rawSpools as Spool[];
const IDS = SPOOLS.map((s) => s.id);

const TOTAL_KG = SPOOLS.reduce((t, s) => t + s.weightKg, 0);
const BAMBU = SPOOLS.filter((s) => s.source === "bambu").length;
const AMAZON = SPOOLS.length - BAMBU;

export default function Home() {
  const [view, setView] = useState<"rack" | "grid">("rack");
  const [filters, setFilters] = useState<FilterState>(EMPTY_FILTERS);
  // Each view remembers its own ordering. A rack is a physical shelf, so it
  // defaults to colour; the grid is a ledger, so it defaults to purchase date.
  const [sortByView, setSortByView] = useState<Record<"rack" | "grid", SortKey>>({
    rack: "colour",
    grid: "date",
  });
  const [grouped, setGrouped] = useState(false);
  const sort = sortByView[view];
  const [status, setStatus] = useState<Record<string, Status>>(() =>
    loadStatus(null, IDS),
  );

  // Read persisted state after mount so the static export hydrates cleanly.
  useEffect(() => {
    setStatus(loadStatus(window.localStorage.getItem(STORAGE_KEY), IDS));
  }, []);

  const toggle = (id: string) => {
    setStatus((prev) => {
      const next = { ...prev, [id]: nextStatus(prev[id] ?? "have") };
      window.localStorage.setItem(STORAGE_KEY, serialiseStatus(next));
      return next;
    });
  };

  const visible = useMemo(
    () =>
      SPOOLS.filter((s) => {
        const { materials, sources, statuses } = filters;
        if (materials.length && !materials.includes(s.material)) return false;
        if (sources.length && !sources.includes(s.source)) return false;
        if (statuses.length && !statuses.includes(status[s.id] ?? "have")) return false;
        return true;
      }),
    [filters, status],
  );

  const sections: Section[] = useMemo(() => {
    const ordered = sortSpools(visible, sort, status);
    if (!grouped) return [{ family: null, spools: ordered }];
    return groupByColour(ordered).map((g) => ({
      family: g.family,
      spools: g.spools,
    }));
  }, [visible, sort, grouped, status]);

  const counts = useMemo(() => {
    let have = 0, low = 0, gone = 0;
    for (const id of IDS) {
      const s = status[id] ?? "have";
      if (s === "have") have++;
      else if (s === "low") low++;
      else gone++;
    }
    return { have, low, gone };
  }, [status]);

  const exportCsv = () => {
    const csv = toStockCsv(SPOOLS, status, new Date().toISOString().slice(0, 10));
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = "stock.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="mx-auto max-w-[1100px] px-4 py-8 sm:px-8 sm:py-12 flex flex-col gap-8">
      <header className="flex flex-col gap-4">
        <div className="flex items-start justify-between gap-4">
          <p className="text-[11px] uppercase tracking-[0.16em] text-[var(--muted)]">
            Bambu Lab and Amazon · Dec 2022 to Dec 2025
          </p>
          <ThemeToggle />
        </div>
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight">
          Filament Shelf
        </h1>
        <p className="max-w-[62ch] text-sm leading-relaxed text-[var(--muted)]">
          Every spool ever bought, drawn from the two ledgers in{" "}
          <code className="text-[var(--accent)]">printer/</code>. Click a spool to
          cycle it through Have, Running low and Gone. Your count is saved in this
          browser and exports to CSV.
        </p>

        <div className="grid gap-px bg-[var(--rule)] border border-[var(--rule)]
                        grid-cols-2 sm:grid-cols-4">
          {[
            { n: String(SPOOLS.length), l: "Spools bought" },
            { n: `${TOTAL_KG} kg`, l: "Filament" },
            { n: `${BAMBU} / ${AMAZON}`, l: "Bambu / Amazon" },
            { n: `${counts.have}`, l: "Marked have" },
          ].map((f) => (
            <div key={f.l} className="bg-[var(--surface)] px-4 py-3 flex flex-col gap-1">
              <span className="text-2xl font-semibold tracking-tight">{f.n}</span>
              <span className="text-[10px] uppercase tracking-[0.14em] text-[var(--muted)]">
                {f.l}
              </span>
            </div>
          ))}
        </div>
      </header>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex border border-[var(--rule)]">
          {(["rack", "grid"] as const).map((v) => (
            <button
              key={v}
              type="button"
              onClick={() => setView(v)}
              aria-pressed={view === v}
              className={`px-4 py-1.5 text-[11px] uppercase tracking-[0.12em] ${
                view === v
                  ? "bg-[var(--ink)] text-[var(--ground)]"
                  : "text-[var(--muted)] hover:text-[var(--ink)]"
              }`}
            >
              {v === "rack" ? "Rack" : "Grid"}
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={exportCsv}
          className="px-3 py-1.5 text-[11px] uppercase tracking-[0.12em]
                     border border-[var(--rule)] text-[var(--muted)]
                     hover:text-[var(--ink)] hover:border-[var(--muted)]"
        >
          Export stock.csv
        </button>
        <span className="text-[11px] text-[var(--muted)]">
          {counts.low} low · {counts.gone} gone
        </span>
      </div>

      <Filters
        value={filters}
        onChange={setFilters}
        matchCount={visible.length}
        total={SPOOLS.length}
        sort={sort}
        onSortChange={(k) => setSortByView((prev) => ({ ...prev, [view]: k }))}
        grouped={grouped}
        onGroupedChange={setGrouped}
      />

      {view === "rack" ? (
        <RackView sections={sections} status={status} onToggle={toggle} />
      ) : (
        <GridView sections={sections} status={status} onToggle={toggle} />
      )}

      <footer className="border-t border-[var(--rule)] pt-6 flex flex-col gap-3
                         text-[12px] leading-relaxed text-[var(--muted)] max-w-[68ch]">
        <p className="uppercase tracking-[0.14em] text-[10px]">Known limitations</p>
        <p>
          Colours are a best reading of Bambu&apos;s published codes and of product
          photos, not sampled from the physical spools. Expect some to be visibly
          off, and tell me which so the mapping can be corrected.
        </p>
        <p>
          Amazon prices were never captured, so the Amazon spools show{" "}
          <em>not captured</em> rather than a figure. The ten-roll matte pack is
          split five Ivory White and five Charcoal by assumption, since the order
          email gives no per-colour count. Two identical DURAMIC PLA+ Purple spools
          ordered the same day are counted as two.
        </p>
        <p>
          Status is a human count, not measured weight, and is only as fresh as the
          last time someone clicked through the shelf.
        </p>
      </footer>
    </main>
  );
}
