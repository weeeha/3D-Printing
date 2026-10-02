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

/**
 * `--info` prints one block per object. Only its counts are trustworthy: it centres every
 * object on itself, so its min/max (and any union of them) say nothing about placement.
 */
export function parseInfo(text) {
  const sum = (key) =>
    [...text.matchAll(new RegExp(`^${key} = +(-?[\\d.]+)`, "gm"))].reduce((t, m) => t + Number(m[1]), 0);
  return {
    objects: [...text.matchAll(/^size_x = /gm)].length,
    triangles: sum("number_of_facets"),
    volumeCm3: Math.round(sum("volume") / 10) / 100,
  };
}

/** Where the file really puts its parts: every vertex through its part's column-major matrix. */
export function boundsOf(parts) {
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  for (const { positions: p, matrix: m } of parts) {
    for (let i = 0; i < p.length; i += 3) {
      const x = p[i], y = p[i + 1], z = p[i + 2];
      const v = [
        m[0] * x + m[4] * y + m[8] * z + m[12],
        m[1] * x + m[5] * y + m[9] * z + m[13],
        m[2] * x + m[6] * y + m[10] * z + m[14],
      ];
      for (let k = 0; k < 3; k++) {
        if (v[k] < min[k]) min[k] = v[k];
        if (v[k] > max[k]) max[k] = v[k];
      }
    }
  }
  return { min, max, size: max.map((v, i) => round1(v - min[i])) };
}

/** The P1S never prints in its front-left 18 x 28 mm corner (bed_exclude_area). */
export const NO_GO = [0, 0, 18, 28];
/** Clearance kept from that corner; touching its edge is enough for Bambu Studio to refuse. */
const NO_GO_MARGIN = 5;

/**
 * Offset that centres the parts on the bed, puts their lowest point on Z=0, and steps them
 * back (or right, if there is no room behind) when the footprint reaches into the no-go corner.
 */
export function bedOffset({ min, max }) {
  const off = [BED / 2 - (min[0] + max[0]) / 2, BED / 2 - (min[1] + max[1]) / 2, 0 - min[2]];
  const x0 = min[0] + off[0], y0 = min[1] + off[1], x1 = max[0] + off[0], y1 = max[1] + off[1];
  const [, , cornerX, cornerY] = NO_GO;
  if (x0 < cornerX + NO_GO_MARGIN && y0 < cornerY + NO_GO_MARGIN) {
    const back = cornerY + NO_GO_MARGIN - y0;
    const right = cornerX + NO_GO_MARGIN - x0;
    if (y1 + back <= BED) off[1] += back;
    else if (x1 + right <= BED) off[0] += right;
  }
  return off;
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

/** A short label and a sentence a person can act on, from the slicer's own error. */
export function failureReason(slicerMessage) {
  if (/G-code conflicts/i.test(slicerMessage)) {
    return {
      short: "G-code conflict",
      reason: "Bambu Studio found print paths from different parts colliding. The file's parts are separate objects that overlap, so it refuses to slice it as it is. Open it in Bambu Studio to see where they collide.",
    };
  }
  if (/Object conflicts/i.test(slicerMessage)) {
    return {
      short: "object conflict",
      reason: "Bambu Studio reports an object conflict: a part reaches into the bed's no-go corner or past its edge.",
    };
  }
  return { short: "slicer error", reason: `Bambu Studio could not slice this file: ${slicerMessage.trim()}` };
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
