/**
 * Slice every print/**\/*.3mf with Bambu Studio's command line and write what
 * the /models page needs: src/data/models.json and a copy of each file in
 * public/models/. Run on the Mac with `npm run slice`; Vercel never runs it.
 *
 * A Bambu Studio project slices with its own settings. A bare mesh slices
 * with the P1S defaults below, after being moved onto the bed (see
 * slice-lib.mjs for why both of those steps are needed).
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, unlinkSync, writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { basename, dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  bedOffset, boundsOf, failureReason, flattenProfile, parseInfo, parsePlate, parseSettings, parseSliceInfo,
  placeItems, productLine, slug,
} from "./slice-lib.mjs";
// Node strips the types; the page uses the same reader, so placement measures what the viewer shows.
import { read3mf } from "../src/lib/read3mf.ts";

const CATALOG = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const REPO = resolve(CATALOG, "..");
const APP = "/Applications/BambuStudio.app";
const BIN = `${APP}/Contents/MacOS/BambuStudio`;
const PROFILES = `${APP}/Contents/Resources/profiles/BBL`;
const DEFAULTS = {
  machine: "Bambu Lab P1S 0.4 nozzle",
  process: "0.20mm Standard @BBL X1C",
  filament: "Bambu PLA Basic @BBL X1C",
};
/** Bare meshes carry no colour; render their thumbnails in the viewer's Geometry grey, not Bambu's default green. */
const NEUTRAL = "#B9BCC1";

if (!existsSync(BIN)) {
  console.error(`Bambu Studio not found at ${APP}. Install it, or run this on the Mac that has it.`);
  process.exit(1);
}

const tmp = mkdtempSync(join(tmpdir(), "slice-models-"));
// cwd is the temp dir: --info drops a result.json wherever it runs.
const run = (args) => execFileSync(BIN, args, { cwd: tmp, stdio: ["ignore", "pipe", "ignore"] }).toString();
const unzipText = (file, entry) => {
  try { return execFileSync("unzip", ["-p", file, entry], { maxBuffer: 1 << 28 }).toString(); }
  catch { return ""; }
};
const listZip = (file) => execFileSync("unzip", ["-Z1", file]).toString().split("\n");

function writeFlatDefaults() {
  const read = (kind, name) => JSON.parse(readFileSync(join(PROFILES, kind, `${name}.json`), "utf8"));
  const out = {};
  for (const [key, kind] of [["machine", "machine"], ["process", "process"], ["filament", "filament"]]) {
    out[key] = join(tmp, `${key}.json`);
    const flat = flattenProfile(kind, DEFAULTS[key], read);
    if (key === "filament") Object.assign(flat, { filament_colour: [NEUTRAL], default_filament_colour: [NEUTRAL] });
    writeFileSync(out[key], JSON.stringify(flat));
  }
  return out;
}

function printFiles(dir = join(REPO, "print")) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? printFiles(join(dir, e.name)) : e.name.endsWith(".3mf") ? [join(dir, e.name)] : [],
  ).sort();
}

/** Copy a bare mesh with every build item moved onto the bed. */
function placedCopy(file, offset, work) {
  const src = join(work, "src");
  mkdirSync(src, { recursive: true });
  execFileSync("unzip", ["-q", "-o", file, "-d", src]);
  const model = join(src, "3D/3dmodel.model");
  writeFileSync(model, placeItems(readFileSync(model, "utf8"), offset));
  const placed = join(work, "placed.3mf");
  execFileSync("zip", ["-q", "-r", "-X", placed, "."], { cwd: src });
  return placed;
}

function sliceOne(file, defaults) {
  const name = basename(file, ".3mf");
  const id = slug(name);
  const work = join(tmp, id);
  mkdirSync(work, { recursive: true });
  const fromFile = listZip(file).includes("Metadata/project_settings.config");
  const info = parseInfo(run(["--info", file]));
  const bounds = boundsOf(read3mf(new Uint8Array(readFileSync(file))));

  const base = {
    id, name,
    folder: relative(join(REPO, "print"), dirname(file)),
    file: relative(REPO, file),
    sha256: createHash("sha256").update(readFileSync(file)).digest("hex"),
    parts: info.objects,
    triangles: info.triangles,
    volumeCm3: info.volumeCm3,
    size: bounds.size,
    settingsSource: fromFile ? "file" : "defaults",
  };

  // Bare meshes are moved onto the bed; record where, so a refused file still has a footprint.
  const offset = bedOffset(bounds);
  const input = fromFile ? file : placedCopy(file, offset, work);
  const footprint = fromFile ? null
    : [bounds.min[0] + offset[0], bounds.min[1] + offset[1], bounds.max[0] + offset[0], bounds.max[1] + offset[1]].map((v) => Math.round(v * 10) / 10);
  const settingsArgs = fromFile ? [] : [
    "--arrange", "0", "--load-settings", `${defaults.machine};${defaults.process}`, "--load-filaments", defaults.filament,
  ];

  // The plate thumbnail renders without slicing, so a file the slicer refuses still gets one.
  const thumbDir = join(work, "thumb");
  mkdirSync(thumbDir, { recursive: true }); // --export-png writes nothing into a missing folder
  let thumb = null;
  try {
    run(["--export-png", "0", "--outputdir", thumbDir, ...settingsArgs, input]);
    const png = readdirSync(thumbDir).find((f) => /^plate_1.*\.png$/.test(f));
    if (png) thumb = join(thumbDir, png);
  } catch {}
  base.thumbnail = thumb !== null;

  const out = join(work, "out");
  mkdirSync(out, { recursive: true }); // result.json, with the slicer's own error, only lands in an existing folder
  try {
    run(["--slice", "0", "--outputdir", out, "--export-3mf", "sliced.3mf", ...settingsArgs, input]);
  } catch {
    const result = existsSync(join(out, "result.json")) ? JSON.parse(readFileSync(join(out, "result.json"), "utf8")) : {};
    const message = result.error_string ?? "no result was written";
    return { record: { ...base, slice: { status: "failed", ...failureReason(message), slicerMessage: message.trim(), footprint } }, thumb };
  }

  const sliced = join(out, "sliced.3mf");
  const { seconds, filaments } = parseSliceInfo(unzipText(sliced, "Metadata/slice_info.config"));
  const { settings, filamentPresets } = parseSettings(unzipText(sliced, "Metadata/project_settings.config"));
  const plate = parsePlate(unzipText(sliced, "Metadata/plate_1.json"));
  if (filaments.some((f) => !(f.grams > 0))) {
    throw new Error(`${name}: a filament came back with no weight. Check the profile flattening.`);
  }
  return {
    thumb,
    record: {
      ...base,
      slice: {
        status: "sliced",
        seconds,
        filaments: filaments.map((f) => ({
          slot: f.slot,
          type: f.type,
          line: fromFile ? productLine(filamentPresets[f.slot - 1]) : productLine(DEFAULTS.filament),
          hex: fromFile ? f.hex : null,
          grams: Math.round(f.grams * 10) / 10,
        })),
        plate,
        settings,
      },
    },
  };
}

try {
  const defaults = writeFlatDefaults();
  const version = execFileSync("plutil", ["-extract", "CFBundleShortVersionString", "raw", "-o", "-", `${APP}/Contents/Info.plist`]).toString().trim();
  const results = printFiles().map((file) => {
    const result = sliceOne(file, defaults);
    const s = result.record.slice;
    console.log(`${result.record.file.padEnd(48)} ${s.status === "sliced" ? `${Math.round(s.seconds / 60)} min` : "not sliced"}${result.thumb ? "" : ", no thumbnail"}`);
    return result;
  });
  const models = results.map((r) => r.record);

  // public/models/ holds each print file and its plate thumbnail, nothing else.
  const publicDir = join(CATALOG, "public/models");
  mkdirSync(publicDir, { recursive: true });
  const keep = new Set(results.flatMap((r) => [`${r.record.id}.3mf`, ...(r.thumb ? [`${r.record.id}.png`] : [])]));
  for (const f of readdirSync(publicDir)) if (!keep.has(f)) unlinkSync(join(publicDir, f));
  for (const { record, thumb } of results) {
    copyFileSync(join(REPO, record.file), join(publicDir, `${record.id}.3mf`));
    if (thumb) copyFileSync(thumb, join(publicDir, `${record.id}.png`));
  }

  const data = { slicedAt: new Date().toISOString().slice(0, 10), slicer: `Bambu Studio ${version}`, models };
  writeFileSync(join(CATALOG, "src/data/models.json"), `${JSON.stringify(data, null, 2)}\n`);
  console.log(`\n${models.length} files, ${models.filter((m) => m.slice.status === "sliced").length} sliced. Wrote src/data/models.json and public/models/.`);
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
