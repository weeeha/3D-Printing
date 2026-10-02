"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";
import { DropZone } from "./DropZone";
import { ModelList } from "./ModelList";
import { PrintPanel, type Dropped } from "./PrintPanel";
import { ViewControls } from "./ViewControls";
import type { Measure, PrintFormat } from "./Model";
import { BED, MODELS, formatMm, unionBox } from "@/lib/models";
import type { ViewMode } from "@/lib/view-modes";

// three.js only runs in the browser; the static export never renders it.
const ModelCanvas = dynamic(() => import("./ModelCanvas"), { ssr: false });


type LocalFile = { name: string; bytes: number; url: string; format: PrintFormat };
type ViewState = { status: "loading" } | { status: "ready"; measure: Measure } | { status: "error"; message: string };

/** The viewer: file list, 3D canvas and print panel. ModelsPage owns which model is selected. */
export function ModelsWorkbench({ selected, onSelect }: { selected: string | null; onSelect: (id: string) => void }) {
  const [local, setLocal] = useState<LocalFile | null>(null);
  const [mode, setMode] = useState<ViewMode>("geometry");
  const [wireframe, setWireframe] = useState(false);
  const [view, setView] = useState<ViewState>({ status: "loading" });

  const record = useMemo(() => MODELS.models.find((m) => m.id === selected) ?? null, [selected]);
  const source = local
    ? { url: local.url, format: local.format, key: local.url }
    : record ? { url: `/models/${record.id}.3mf`, format: "3mf" as const, key: record.id } : null;

  useEffect(() => setView({ status: "loading" }), [source?.key]);
  useEffect(() => () => { if (local) URL.revokeObjectURL(local.url); }, [local]);

  const select = (id: string) => {
    setLocal(null);
    onSelect(id);
  };
  const onMeasure = useCallback((measure: Measure) => setView({ status: "ready", measure }), []);
  const onError = useCallback((message: string) => setView({ status: "error", message }), []);

  // Put the plate where the slicer put the parts: bed X/Y map to scene X/-Z around the model's centre.
  const plateOffset = useMemo<[number, number]>(() => {
    if (local || record?.slice.status !== "sliced") return [0, 0];
    const parts = record.slice.plate.filter((p) => !p.tower);
    if (!parts.length) return [0, 0];
    const [x0, y0, x1, y1] = unionBox(parts);
    return [BED / 2 - (x0 + x1) / 2, (y0 + y1) / 2 - BED / 2];
  }, [local, record]);

  const colour = !local && record?.slice.status === "sliced" && record.slice.filaments.length === 1
    ? record.slice.filaments[0].hex
    : null;
  const dropped: Dropped | null = local
    ? { name: local.name, bytes: local.bytes, measure: view.status === "ready" ? view.measure : null, failed: view.status === "error" }
    : null;
  const readout = view.status === "ready" ? `${view.measure.size.map(formatMm).join(" × ")} mm` : "";
  const fileName = local ? local.name : record ? `${record.name}.3mf` : "";

  return (
      <div className="grid gap-5 items-start grid-cols-1 [grid-template-areas:'viewer''panel''files']
                      min-[760px]:grid-cols-[minmax(0,1fr)_300px] min-[760px]:[grid-template-areas:'viewer_panel''files_panel']
                      min-[1140px]:grid-cols-[236px_minmax(0,1fr)_300px] min-[1140px]:[grid-template-areas:'files_viewer_panel']">
        <section aria-label="Print files" className="[grid-area:files] min-w-0 flex flex-col gap-4.5">
          <ModelList models={MODELS.models} selected={local ? null : selected} onSelect={select} />
          <DropZone onFile={(file, format) => setLocal({ name: file.name, bytes: file.size, url: URL.createObjectURL(file), format })} />
        </section>

        <section aria-label="Model viewer" className="[grid-area:viewer] min-w-0 flex flex-col gap-2.5">
          <div className="flex flex-wrap items-center gap-2">
            <ViewControls mode={mode} onModeChange={setMode} wireframe={wireframe} onWireframeChange={setWireframe} />
            <span className="ml-auto text-[12px] text-[var(--muted)]">{readout}</span>
          </div>
          <div className="relative aspect-[4/3] max-w-full overflow-hidden border border-[var(--rule)] bg-[var(--viewport)]">
            {source && (
              <div className="absolute inset-0 touch-none">
                <ModelCanvas
                  key={source.key}
                  url={source.url}
                  format={source.format}
                  mode={mode}
                  wireframe={wireframe}
                  colour={colour}
                  plateOffset={plateOffset}
                  onMeasure={onMeasure}
                  onError={onError}
                />
              </div>
            )}
            {view.status !== "ready" && (
              <div className="absolute inset-0 flex items-center justify-center p-6 text-center text-[12px] leading-relaxed text-[var(--muted)] pointer-events-none">
                {view.status === "loading" ? `Loading ${fileName}` : `Couldn't show ${fileName} in the browser. ${view.message}`}
              </div>
            )}
          </div>
          <p className="m-0 text-[10px] leading-relaxed text-[var(--muted)]">
            Drag to orbit, scroll or pinch to zoom. The plate is the P1S bed, 256 mm square, with the parts where the slicer placed them.
          </p>
        </section>

        <div className="[grid-area:panel] min-w-0">
          <PrintPanel record={local ? null : record} dropped={dropped} />
        </div>
      </div>
  );
}
