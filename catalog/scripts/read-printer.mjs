/**
 * Read the AMS state from the printer over local MQTT and write it to
 * src/data/printer-state.json.
 *
 * Run with `npm run printer`. Needs catalog/.env.local (see .env.example).
 * The printer must be on, in LAN Mode, and Bambu Studio must be closed: the
 * P1 series only serves one local MQTT client at a time.
 *
 * Scope, stated plainly: this can only see spools currently loaded in the AMS,
 * and `remain` is only populated for spools with a readable Bambu RFID tag.
 * The rest of the shelf is a manual count.
 */
import mqtt from "mqtt";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));

function loadEnv() {
  const out = {};
  try {
    for (const line of readFileSync(resolve(here, "../.env.local"), "utf8").split("\n")) {
      const m = line.match(/^\s*([A-Z_]+)\s*=\s*(.*)\s*$/);
      if (m) out[m[1]] = m[2].trim();
    }
  } catch {
    throw new Error("No catalog/.env.local. Copy .env.example and fill it in.");
  }
  for (const k of ["BAMBU_IP", "BAMBU_SERIAL", "BAMBU_CODE"]) {
    if (!out[k]) throw new Error(`${k} missing from catalog/.env.local`);
  }
  return out;
}

const num = (v) => {
  const n = Number(v);
  return v === undefined || v === null || v === "" || Number.isNaN(n) ? null : n;
};

/** Shape the raw MQTT payload into just what the shelf needs. */
export function toPrinterState(payload, readAt) {
  const p = payload.print ?? {};
  const units = p.ams?.ams ?? [];
  const slots = [];
  for (const unit of units) {
    for (const t of unit.tray ?? []) {
      const hex = `#${String(t.tray_color ?? "").slice(0, 6).toUpperCase()}`;
      slots.push({
        slot: `${"AB"[Number(unit.id)] ?? unit.id}${Number(t.id) + 1}`,
        uuid: t.tray_uuid ?? "",
        sku: t.tray_id_name ?? "",
        productLine: t.tray_sub_brands ?? "",
        material: t.tray_type ?? "",
        hex: /^#[0-9A-F]{6}$/.test(hex) ? hex : null,
        // -1 or absent means no readable RFID, so no estimate exists.
        remain: typeof t.remain === "number" && t.remain >= 0 ? t.remain : null,
      });
    }
  }
  return {
    readAt,
    printing: p.gcode_state === "RUNNING" ? (p.subtask_name ?? null) : null,
    percent: p.gcode_state === "RUNNING" ? (p.mc_percent ?? null) : null,
    // The printer sends these as strings; coerce at the boundary so the app
    // never has to wonder which it is getting.
    ams: units.map((u) => ({
      unit: Number(u.id),
      humidityRh: num(u.humidity_raw),
      tempC: num(u.temp),
    })),
    slots,
  };
}

async function main() {
  const { BAMBU_IP, BAMBU_SERIAL, BAMBU_CODE } = loadEnv();
  const client = mqtt.connect(`mqtts://${BAMBU_IP}:8883`, {
    username: "bblp",
    password: BAMBU_CODE,
    rejectUnauthorized: false, // printer presents a self-signed BBL cert
    connectTimeout: 10000,
    reconnectPeriod: 0,
  });

  const state = await new Promise((ok, fail) => {
    const timer = setTimeout(
      () => fail(new Error("No AMS payload in 25s. Is Bambu Studio still open?")),
      25000,
    );
    client.on("error", (e) => { clearTimeout(timer); fail(e); });
    client.on("connect", () => {
      client.subscribe(`device/${BAMBU_SERIAL}/report`, (err) => {
        if (err) return fail(err);
        client.publish(
          `device/${BAMBU_SERIAL}/request`,
          JSON.stringify({ pushing: { sequence_id: "1", command: "pushall" } }),
        );
      });
    });
    client.on("message", (_t, buf) => {
      const payload = JSON.parse(buf.toString());
      if (!payload.print?.ams) return; // heartbeat, not the full push
      clearTimeout(timer);
      ok(toPrinterState(payload, new Date().toISOString()));
    });
  });

  client.end();
  const dest = resolve(here, "../src/data/printer-state.json");
  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, JSON.stringify(state, null, 2) + "\n");

  const withRfid = state.slots.filter((s) => s.remain !== null).length;
  console.log(`Read ${state.slots.length} slots, ${withRfid} with RFID data.`);
  for (const s of state.slots) {
    console.log(`  ${s.slot}  ${s.productLine.padEnd(12)} ${s.hex ?? "-"}  ${s.remain ?? "-"}%`);
  }
  console.log(`Wrote ${dest}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((e) => { console.error(e.message); process.exit(1); });
}
