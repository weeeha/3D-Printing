import data from "@/data/models.json";

/** P1S build plate, mm. */
export const BED = 256;
/** Front-left corner the P1S never prints in (bed_exclude_area in Bambu's machine profile). */
export const NO_GO: Box = [0, 0, 18, 28];

/** x0 y0 x1 y1 on the bed, mm, origin front-left. */
export type Box = [number, number, number, number];

export type Filament = { slot: number; type: string; line: string; hex: string | null; grams: number };
export type PlateObject = { name: string; box: Box; tower: boolean };
export type SliceSettings = {
  printer: string; process: string; layer: number; infill: string; walls: number; supports: boolean; nozzle: number;
};
export type Sliced = { status: "sliced"; seconds: number; filaments: Filament[]; plate: PlateObject[]; settings: SliceSettings };
export type Failed = { status: "failed"; reason: string; slicerMessage: string };

export type ModelRecord = {
  id: string;
  name: string;
  folder: string;
  file: string;
  sha256: string;
  parts: number;
  triangles: number;
  volumeCm3: number;
  size: [number, number, number];
  settingsSource: "file" | "defaults";
  slice: Sliced | Failed;
};

export type ModelsData = { slicedAt: string; slicer: string; models: ModelRecord[] };

/** Written by `npm run slice`; JSON imports type loosely, so assert the shape once here. */
export const MODELS = data as unknown as ModelsData;

export function formatDuration(seconds: number): string {
  const m = Math.max(1, Math.round(seconds / 60));
  return m < 60 ? `${m}m` : `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, "0")}m`;
}

export const formatMm = (v: number) => v.toFixed(1);

export function unionBox(boxes: { box: Box }[]): Box {
  return boxes.reduce<Box>(
    (u, { box: b }) => [Math.min(u[0], b[0]), Math.min(u[1], b[1]), Math.max(u[2], b[2]), Math.max(u[3], b[3])],
    [Infinity, Infinity, -Infinity, -Infinity],
  );
}

/** Distance from the box to the nearest bed edge. */
export function clearance(box: Box): number {
  return Math.max(0, Math.min(box[0], box[1], BED - box[2], BED - box[3]));
}

/** Where a part lands when centred on the bed, for files the slicer never placed. */
export function centredBox([x, y]: [number, number, number]): Box {
  return [BED / 2 - x / 2, BED / 2 - y / 2, BED / 2 + x / 2, BED / 2 + y / 2];
}

export const totalGrams = (s: Sliced) => s.filaments.reduce((t, f) => t + f.grams, 0);
