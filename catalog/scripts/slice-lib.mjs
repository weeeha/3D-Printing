/**
 * Pure helpers for slicing print/ with Bambu Studio's command line. Nothing
 * here touches the disk or spawns a process; slice-models.mjs does that.
 */

export const BED = 256;

/**
 * Resolve a Bambu system profile's `inherits` chain into one object. The CLI
 * reads only the file it is given, so an unflattened profile silently falls
 * back to built-in values (20% infill, filament density 0).
 */
export function flattenProfile(kind, name, readProfile) {
  const own = readProfile(kind, name);
  if (!own.inherits) return { ...own };
  const { inherits, ...rest } = own;
  return { ...flattenProfile(kind, inherits, readProfile), ...rest };
}

/** `--info` prints one block per object; take the union box and summed counts. */
export function parseInfo(text) {
  const all = (key) =>
    [...text.matchAll(new RegExp(`^${key} = +(-?[\\d.]+)`, "gm"))].map((m) => Number(m[1]));
  const min = ["min_x", "min_y", "min_z"].map((k) => Math.min(...all(k)));
  const max = ["max_x", "max_y", "max_z"].map((k) => Math.max(...all(k)));
  const sum = (key) => all(key).reduce((a, b) => a + b, 0);
  return {
    min,
    max,
    size: max.map((v, i) => round1(v - min[i])),
    objects: all("size_x").length,
    triangles: sum("number_of_facets"),
    volumeCm3: Math.round(sum("volume") / 10) / 100,
  };
}

/** Offset that centres the union on the bed and puts its lowest point on Z=0. */
export function bedOffset({ min, max }) {
  return [BED / 2 - (min[0] + max[0]) / 2, BED / 2 - (min[1] + max[1]) / 2, -min[2]];
}

/**
 * Move every build item by one shared offset, so a multi-part model stays
 * assembled. An item's own rotation is kept; the offset adds to its translation.
 */
export function placeItems(modelXml, offset) {
  return modelXml.replace(/<item\b([^>]*?)\s*\/>/g, (_, attrs) => {
    const id = attrs.match(/objectid="([^"]+)"/)?.[1];
    const given = attrs.match(/transform="([^"]+)"/)?.[1];
    const m = given ? given.trim().split(/\s+/).map(Number) : [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0];
    const placed = [...m.slice(0, 9), m[9] + offset[0], m[10] + offset[1], m[11] + offset[2]];
    return `<item objectid="${id}" transform="${placed.map(fmt).join(" ")}" />`;
  });
}

/** Time and per-slot grams from Metadata/slice_info.config. */
export function parseSliceInfo(xml) {
  const seconds = Number(xml.match(/key="prediction" value="(\d+)"/)?.[1] ?? NaN);
  const filaments = [...xml.matchAll(/<filament\b([^>]*)\/>/g)].map(([, attrs]) => {
    const a = (k) => attrs.match(new RegExp(`\\b${k}="([^"]*)"`))?.[1];
    return { slot: Number(a("id")), type: a("type"), hex: a("color"), grams: Number(a("used_g")) };
  });
  return { seconds, filaments };
}

/** Each object's footprint on the bed from Metadata/plate_1.json. */
export function parsePlate(json) {
  const plate = JSON.parse(json);
  return (plate.bbox_objects ?? []).map((o) => ({
    name: o.name,
    box: o.bbox.map(round1),
    tower: /wipe|prime/i.test(o.name),
  }));
}

/** The settings the panel shows, from the sliced project's settings. */
export function parseSettings(json) {
  const s = JSON.parse(json);
  const first = (v) => (Array.isArray(v) ? v[0] : v);
  return {
    settings: {
      printer: s.printer_settings_id,
      process: s.print_settings_id,
      layer: Number(s.layer_height),
      infill: s.sparse_infill_density,
      walls: Number(s.wall_loops),
      supports: s.enable_support === "1",
      nozzle: Number(first(s.nozzle_diameter)),
    },
    filamentPresets: Array.isArray(s.filament_settings_id) ? s.filament_settings_id : [s.filament_settings_id],
  };
}

/** "Bambu PLA Matte @BBL P1S 0.4 nozzle" -> "PLA Matte". Generic presets count as PLA Basic. */
export function productLine(preset) {
  return preset?.match(/^Bambu ((?:PLA|PETG|ABS|ASA|TPU|PC|PA)\b[^@]*?)\s*@/)?.[1] ?? "PLA Basic";
}

/** A sentence a person can act on, for a file the slicer refused. */
export function failureReason(size, slicerMessage) {
  const widest = Math.max(size[0], size[1]);
  if (widest >= BED - 0.1) {
    return `${widest.toFixed(1)} mm wide, the full width of the P1S bed. Bambu Studio only slices parts that sit fully inside the plate, so it refuses this file as it is.`;
  }
  return `Bambu Studio could not slice this file: ${slicerMessage}`;
}

export function slug(name) {
  return String(name).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function round1(v) {
  return Math.round(v * 10) / 10;
}

function fmt(v) {
  return String(Math.round(v * 1e6) / 1e6);
}
