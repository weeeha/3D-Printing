"use client";

import type { ReactNode } from "react";
import { BedDiagram } from "./BedDiagram";
import type { Measure } from "./Model";
import { calibrate, estimate } from "@/lib/estimate";
import {
  MODELS, centredBox, clearance, formatDuration, formatMm, totalGrams, unionBox,
  type Box, type ModelRecord, type Sliced,
} from "@/lib/models";
import { filamentPrice, formatCad, sliceCost } from "@/lib/model-cost";
import { costCad } from "@/lib/prices";

/** A file from disk: measured once the viewer loads it, or failed with the reason. */
export type Dropped = { name: string; bytes: number; measure: Measure | null; failed: boolean };

const CALIBRATION = calibrate(MODELS.models);

function Section({ label, children }: { label?: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-2 px-4 py-3.5 border-t border-[var(--rule)] first:border-t-0">
      {label && <span className="text-[10px] uppercase tracking-[0.14em] text-[var(--muted)]">{label}</span>}
      {children}
    </div>
  );
}

const Note = ({ children, warn }: { children: ReactNode; warn?: boolean }) => (
  <p className={`m-0 text-[11px] leading-relaxed ${warn ? "text-[var(--warn)]" : "text-[var(--muted)]"}`}>{children}</p>
);

function Chip({ tone, children }: { tone?: "accent" | "warn"; children: ReactNode }) {
  const colour = tone === "accent" ? "border-[var(--accent)] text-[var(--accent)]"
    : tone === "warn" ? "border-[var(--warn)] text-[var(--warn)]"
    : "border-[var(--rule)] text-[var(--muted)]";
  return <span className={`self-start border px-1.5 py-0.5 text-[10px] uppercase tracking-[0.12em] ${colour}`}>{children}</span>;
}

function Head({ title, path, chip }: { title: string; path: string; chip: ReactNode }) {
  return (
    <Section>
      <p className="m-0 text-sm font-semibold [overflow-wrap:anywhere]">{title}</p>
      <span className="text-[11px] text-[var(--muted)] [overflow-wrap:anywhere]">{path}</span>
      {chip}
    </Section>
  );
}

function SizeAndFit({ size, footprints, tone }: { size: [number, number, number]; footprints: { box: Box; tower: boolean }[]; tone: "accent" | "warn" }) {
  const parts = footprints.filter((f) => !f.tower);
  const union = unionBox(footprints);
  const partsUnion = unionBox(parts);
  const clear = clearance(union);
  // A plate of several parts reads by its footprint; one part by its own size.
  const sizeLine = parts.length > 1
    ? `${formatMm(partsUnion[2] - partsUnion[0])} × ${formatMm(partsUnion[3] - partsUnion[1])} mm on the plate, ${formatMm(size[2])} mm tall`
    : `${size.map(formatMm).join(" × ")} mm`;
  return (
    <Section label="Size and bed fit">
      <span className="text-[12px]">{sizeLine}</span>
      <BedDiagram footprints={footprints} tone={tone} />
      {clear < 0.5
        ? <Note warn>No clearance. At {formatMm(Math.max(size[0], size[1]))} mm it fills the bed edge to edge.</Note>
        : <Note>Fits, {formatMm(clear)} mm clear of the nearest edge{size[2] > 256 ? ", but taller than the 256 mm build height" : ""}.</Note>}
    </Section>
  );
}

function Actions({ record }: { record: ModelRecord }) {
  // Bambu Studio's bambustudioopen:// link launched the app but never fetched a
  // self-hosted file (see the spec's known issues), so the download is the way in.
  return (
    <Section>
      <a
        href={`/models/${record.id}.3mf`}
        download={`${record.name}.3mf`}
        className="block text-center px-3.5 py-2.5 text-[11px] uppercase tracking-[0.12em] bg-[var(--accent)] text-[var(--surface)] hover:bg-[var(--ink)] hover:text-[var(--ground)]"
      >
        Download .3mf
      </a>
      <Note>Open the download from your browser and it opens in Bambu Studio, ready to slice and print.</Note>
    </Section>
  );
}

const printerName = (s: string) => s.replace(/^Bambu Lab /, "").replace(/ (\d\.\d) nozzle$/, " · $1 mm nozzle");
const processName = (s: string) => s.replace(/ @BBL.*$/, "");

function SlicedPanel({ record, slice }: { record: ModelRecord; slice: Sliced }) {
  const fromFile = record.settingsSource === "file";
  const cost = sliceCost(slice);
  const lines = [...new Map(slice.filaments.map((f) => [f.line, f])).values()];
  return (
    <>
      <Head
        title={`${record.name}.3mf`}
        path={`${record.file} · ${record.parts} ${record.parts === 1 ? "part" : "parts"}`}
        chip={<Chip tone={fromFile ? "accent" : undefined}>{fromFile ? "Settings from the file" : "P1S defaults"}</Chip>}
      />
      <Section label="Print time">
        <span className="text-2xl font-semibold tracking-tight">{formatDuration(slice.seconds)}</span>
        <Note>Bambu Studio&apos;s estimate for the P1S{slice.filaments.length > 1 ? ", including colour changes" : ""}.</Note>
      </Section>
      <Section label="Filament and cost (CAD)">
        <div className="grid grid-cols-[12px_minmax(0,1fr)_auto_auto] items-center gap-x-2.5 gap-y-1.5 text-[12px]">
          {slice.filaments.map((f) => {
            const price = filamentPrice(f);
            return (
              <div key={f.slot} className="contents">
                <span
                  aria-hidden
                  className={`w-3 h-3 border ${f.hex ? "border-[var(--rule)]" : "border-dashed border-[var(--muted)]"}`}
                  style={f.hex ? { background: f.hex } : undefined}
                />
                <span>{f.line}{!f.hex && <span className="text-[var(--muted)]"> · no colour in file</span>}</span>
                <span className="text-right">{formatMm(f.grams)} g</span>
                <span className="text-right">{price ? formatCad(costCad(f.grams, price.perKg)) : "–"}</span>
              </div>
            );
          })}
          <span className="pt-1.5 border-t border-[var(--rule)]" />
          <span className="pt-1.5 border-t border-[var(--rule)] font-semibold">Total</span>
          <span className="pt-1.5 border-t border-[var(--rule)] font-semibold text-right">{formatMm(totalGrams(slice))} g</span>
          <span className="pt-1.5 border-t border-[var(--rule)] font-semibold text-right">{cost === null ? "–" : formatCad(cost)}</span>
        </div>
        {lines.map((f) => {
          const price = filamentPrice(f);
          if (!price) return <Note key={f.line}>No price recorded for {f.line} or any {f.type}.</Note>;
          return price.matched
            ? <Note key={f.line}>{f.line} at {formatCad(price.perKg)}/kg, the median of {price.spools} spools bought from Bambu.</Note>
            : <Note key={f.line}>No {f.line} bought yet, so the {f.type} median stands in: {formatCad(price.perKg)}/kg over {price.spools} spools.</Note>;
        })}
      </Section>
      <SizeAndFit size={record.size} footprints={slice.plate} tone="accent" />
      <Section label="Sliced with">
        <dl className="m-0 grid grid-cols-[auto_minmax(0,1fr)] gap-x-3 gap-y-1 text-[12px]">
          {[
            ["Printer", printerName(slice.settings.printer)],
            ["Process", processName(slice.settings.process)],
            ["Layer", `${slice.settings.layer.toFixed(2)} mm`],
            ["Infill", slice.settings.infill],
            ["Walls", String(slice.settings.walls)],
            ["Supports", slice.settings.supports ? "On" : "None"],
          ].map(([k, v]) => (
            <div key={k} className="contents">
              <dt className="text-[var(--muted)]">{k}</dt>
              <dd className="m-0 [overflow-wrap:anywhere]">{v}</dd>
            </div>
          ))}
        </dl>
        {!fromFile && (
          <Note>This file has no slicer settings, so it was sliced with the P1S defaults and PLA Basic. Your real print may use other settings.</Note>
        )}
      </Section>
      <Actions record={record} />
    </>
  );
}

function FailedPanel({ record, reason }: { record: ModelRecord; reason: string }) {
  return (
    <>
      <Head title={`${record.name}.3mf`} path={`${record.file} · ${record.parts} parts`} chip={<Chip tone="warn">Not sliced</Chip>} />
      <Section label="Print time">
        <span className="text-2xl font-semibold tracking-tight text-[var(--warn)]">No estimate</span>
        <Note>{reason}</Note>
      </Section>
      <Section label="Filament and cost (CAD)">
        <Note>Weight and cost appear once the file slices.</Note>
      </Section>
      <SizeAndFit size={record.size} footprints={[{ box: centredBox(record.size), tower: false }]} tone="warn" />
      <Actions record={record} />
    </>
  );
}

function EstimatePanel({ dropped }: { dropped: Dropped }) {
  const m = dropped.measure;
  const basic = filamentPrice({ line: "PLA Basic", type: "PLA" });
  const range = m && CALIBRATION ? estimate(m.volumeCm3, CALIBRATION) : null;
  return (
    <>
      <Head title={dropped.name} path={`From your computer · ${Math.max(1, Math.round(dropped.bytes / 1024))} KB`} chip={<Chip>Estimate</Chip>} />
      {!m ? (
        <Section label="Print time">
          <Note>{dropped.failed ? "No estimate, because the file could not be read. The viewer says why." : "Measuring the mesh."}</Note>
        </Section>
      ) : (
        <>
          <Section label="Print time">
            {range
              ? <span className="text-2xl font-semibold tracking-tight">{formatDuration(range.seconds[0])} to {formatDuration(range.seconds[1])}</span>
              : <span className="text-2xl font-semibold tracking-tight">No estimate</span>}
            <Note>
              A range from the mesh volume ({formatMm(m.volumeCm3)} cm³)
              {range && CALIBRATION ? `, scaled by how this repo's ${CALIBRATION.basedOn.length} single-colour, 0.4 mm prints sliced` : ""}.
              Slice it in Bambu Studio for a real number.
            </Note>
          </Section>
          {range && (
            <Section label="Filament and cost (CAD)">
              <div className="grid grid-cols-[12px_minmax(0,1fr)_auto_auto] items-center gap-x-2.5 text-[12px]">
                <span aria-hidden className="w-3 h-3 border border-dashed border-[var(--muted)]" />
                <span>PLA Basic</span>
                <span className="text-right">{Math.round(range.grams[0])} to {Math.round(range.grams[1])} g</span>
                <span className="text-right">
                  {basic ? `${formatCad(costCad(range.grams[0], basic.perKg))} to ${formatCad(costCad(range.grams[1], basic.perKg))}` : "–"}
                </span>
              </div>
            </Section>
          )}
          <SizeAndFit size={m.size} footprints={[{ box: centredBox(m.size), tower: false }]} tone={Math.max(m.size[0], m.size[1]) >= 255.9 ? "warn" : "accent"} />
        </>
      )}
      <Section label="Open it">
        <Note>This file is on your computer, so open it in Bambu Studio from there.</Note>
      </Section>
    </>
  );
}

export function PrintPanel({ record, dropped }: { record: ModelRecord | null; dropped: Dropped | null }) {
  return (
    <aside aria-live="polite" className="border border-[var(--rule)] bg-[var(--surface)] min-w-0">
      {dropped ? <EstimatePanel dropped={dropped} />
        : record?.slice.status === "sliced" ? <SlicedPanel record={record} slice={record.slice} />
        : record?.slice.status === "failed" ? <FailedPanel record={record} reason={record.slice.reason} />
        : null}
    </aside>
  );
}
