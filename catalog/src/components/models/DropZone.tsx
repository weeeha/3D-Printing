"use client";

import { useState } from "react";
import type { PrintFormat } from "./Model";

const FORMATS: Record<string, PrintFormat> = { stl: "stl", "3mf": "3mf" };

/** Check a file from disk: STL or 3MF, opened in the viewer with an estimate. */
export function DropZone({ onFile }: { onFile: (file: File, format: PrintFormat) => void }) {
  const [over, setOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const take = (file: File | undefined) => {
    if (!file) return;
    const format = FORMATS[file.name.split(".").pop()?.toLowerCase() ?? ""];
    if (!format) {
      setError(`${file.name} is not an STL or 3MF file.`);
      return;
    }
    setError(null);
    onFile(file, format);
  };

  return (
    <label
      onDragOver={(e) => { e.preventDefault(); setOver(true); }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => { e.preventDefault(); setOver(false); take(e.dataTransfer.files[0]); }}
      className={`relative flex flex-col gap-1 border border-dashed px-3 py-3.5 cursor-pointer
                  focus-within:outline focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-[var(--accent)]
                  ${over ? "border-[var(--accent)]" : "border-[var(--muted)] hover:border-[var(--accent)]"}`}
    >
      <input
        type="file"
        accept=".stl,.3mf"
        className="absolute w-px h-px opacity-0"
        onChange={(e) => { take(e.target.files?.[0]); e.target.value = ""; }}
      />
      <span className="text-[12px] font-semibold">Check a file from your computer</span>
      <span className="text-[10px] leading-relaxed text-[var(--muted)]">
        Drop an STL or 3MF here, or click to choose. You get a rough estimate until it is sliced.
      </span>
      {error && <span className="text-[11px] text-[var(--warn)]">{error}</span>}
    </label>
  );
}
