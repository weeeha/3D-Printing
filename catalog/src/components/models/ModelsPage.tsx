"use client";

import { useCallback, useEffect, useState } from "react";
import { SiteNav } from "@/components/SiteNav";
import { ModelGallery } from "./ModelGallery";
import { ModelTable } from "./ModelTable";
import { ModelsWorkbench } from "./ModelsWorkbench";
import { MODELS } from "@/lib/models";

type View = "gallery" | "list" | "viewer";
type Route = { view: View; id: string | null };

const VIEWS: { id: View; label: string }[] = [
  { id: "gallery", label: "Gallery" },
  { id: "list", label: "List" },
  { id: "viewer", label: "Viewer" },
];
const DEFAULT_ID = MODELS.models.find((m) => m.slice.status === "sliced")?.id ?? MODELS.models[0]?.id ?? null;

/** #gallery, #list, or a model id (opens the viewer). Anything else is the gallery. */
function parse(hash: string): Route {
  const h = hash.replace(/^#/, "");
  if (h === "list") return { view: "list", id: null };
  if (MODELS.models.some((m) => m.id === h)) return { view: "viewer", id: h };
  return { view: "gallery", id: null };
}

export function ModelsPage() {
  const [route, setRoute] = useState<Route>({ view: "gallery", id: null });
  // The last model opened, so switching back to Viewer returns to it.
  const [lastId, setLastId] = useState<string | null>(DEFAULT_ID);

  useEffect(() => {
    const sync = () => {
      const next = parse(window.location.hash);
      setRoute(next);
      if (next.id) setLastId(next.id);
    };
    sync();
    window.addEventListener("hashchange", sync);
    return () => window.removeEventListener("hashchange", sync);
  }, []);

  /** Switching views and opening a model are history steps, so Back returns to the overview. */
  const go = (hash: string) => { window.location.hash = hash; };
  /** Picking another model inside the viewer replaces the entry instead of stacking them. */
  const selectInViewer = useCallback((id: string) => {
    try { history.replaceState(null, "", `#${id}`); } catch {}
    setRoute({ view: "viewer", id });
    setLastId(id);
  }, []);

  return (
    <main className="mx-auto max-w-[1320px] px-4 py-8 sm:px-8 sm:py-12 flex flex-col gap-8">
      <SiteNav current="models" />
      <header className="flex flex-col gap-4">
        <p className="text-[11px] uppercase tracking-[0.16em] text-[var(--muted)]">
          print/ · {MODELS.models.length} files · sliced {MODELS.slicedAt} with {MODELS.slicer}
        </p>
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight">Models</h1>
        <p className="max-w-[62ch] text-sm leading-relaxed text-[var(--muted)]">
          Every print-ready file in <code className="text-[var(--accent)]">print/</code>, sliced for the P1S.
          Print time and filament come from Bambu Studio. Cost is the filament weight times what you paid
          per kilo for that line.
        </p>
      </header>

      <div className="flex border border-[var(--rule)] w-max max-w-full">
        {VIEWS.map((v) => (
          <button
            key={v.id}
            type="button"
            aria-pressed={route.view === v.id}
            onClick={() => go(v.id === "viewer" ? (lastId ?? "") : v.id)}
            className={`px-4 py-1.5 text-[11px] uppercase tracking-[0.12em] ${route.view === v.id
              ? "bg-[var(--ink)] text-[var(--ground)]"
              : "text-[var(--muted)] hover:text-[var(--ink)]"}`}
          >
            {v.label}
          </button>
        ))}
      </div>

      {route.view === "gallery" && <ModelGallery models={MODELS.models} onOpen={go} />}
      {route.view === "list" && <ModelTable models={MODELS.models} onOpen={go} />}
      {route.view === "viewer" && <ModelsWorkbench selected={route.id ?? lastId} onSelect={selectInViewer} />}
    </main>
  );
}
