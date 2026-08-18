/**
 * Explode the two CSV ledgers in printer/ into one record per physical spool.
 *
 * The CSVs are the source of truth and are never written by the app. This
 * script is the only thing that reads them, and it runs at build time.
 *
 * Only filament belongs on the shelf: from orders.csv that is the "filament"
 * and "support" categories, and from orders-amazon.csv everything except the
 * adhesive glue. Printers, hotends, accessories and spares live in
 * printer/inventory.md instead.
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { lookupColour } from "../src/lib/colours.mjs";

const slug = (s) =>
  String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

function parseCsv(text) {
  const [header, ...rows] = text.trim().split("\n");
  const cols = header.split(",");
  return rows
    .filter((line) => line.trim().length > 0)
    .map((line) => {
      const cells = line.split(",");
      return Object.fromEntries(cols.map((c, i) => [c.trim(), (cells[i] ?? "").trim()]));
    });
}

function materialOf(productLine) {
  const p = productLine.toLowerCase();
  if (p.includes("petg")) return "PETG";
  if (p.startsWith("pva")) return "PVA";
  if (p.startsWith("support")) return "Support";
  return "PLA";
}

export function buildSpools(bambuCsv, amazonCsv) {
  const out = [];
  const counters = new Map();

  const push = (rec) => {
    const prefix = `${rec.source}-${slug(rec.productLine)}-${
      rec.colourCode || slug(rec.colourName)
    }`;
    const n = (counters.get(prefix) ?? 0) + 1;
    counters.set(prefix, n);
    out.push({ ...rec, id: `${prefix}-${n}` });
  };

  // Never default a missing colour. A silently grey spool is a data bug the
  // page would hide, so fail the build instead.
  const colour = (key, label) => {
    const s = lookupColour(key);
    if (!s) throw new Error(`No colour mapping for "${key}" (from ${label})`);
    return s;
  };

  // ---------- Bambu Lab ----------
  for (const r of parseCsv(bambuCsv)) {
    if (r.category !== "filament" && r.category !== "support") continue;

    const qty = Number(r.qty);
    const paid = Number(r.line_paid_cad);
    const variant = r.variant ?? "";
    const codeMatch = variant.match(/\((\d{5})\)/);
    const colourCode = codeMatch ? codeMatch[1] : "";

    // The ten-roll refill pack. Split 5/5, an assumption documented in the
    // spec because the order email gives no per-colour count.
    if (r.item === "PLA Matte Refill Pack 10 Rolls") {
      for (const [code, name] of [
        ["11100", "Matte Ivory White"],
        ["11101", "Matte Charcoal"],
      ]) {
        const s = colour(code, r.item);
        for (let i = 0; i < 5; i++) {
          push({
            source: "bambu", brand: "Bambu Lab", material: "PLA",
            productLine: "PLA Matte", colourName: name, colourCode: code,
            hex: s.hex, hex2: s.hex2, finish: s.finish, weightKg: 1,
            isRefill: true, orderId: r.order_id, orderDate: r.order_date,
            pricePaidCad: Number((paid / 10).toFixed(2)),
          });
        }
      }
      continue;
    }

    // The CMYK lithophane bundle ships as four process-colour rolls.
    if (r.item === "PLA CMYK Lithophane Bundle") {
      for (const [key, name] of [
        ["litho cyan", "Cyan"], ["litho magenta", "Magenta"],
        ["litho yellow", "Yellow"], ["litho black", "Black"],
      ]) {
        const s = colour(key, r.item);
        push({
          source: "bambu", brand: "Bambu Lab", material: "PLA",
          productLine: "PLA CMYK Lithophane Bundle", colourName: name,
          colourCode: "", hex: s.hex, hex2: s.hex2, finish: s.finish,
          weightKg: 1, isRefill: false, orderId: r.order_id,
          orderDate: r.order_date, pricePaidCad: Number((paid / 4).toFixed(2)),
        });
      }
      continue;
    }

    // Default: one record per unit of qty.
    // Colour is always the first variant segment, except where the variant is
    // only a size (Support for PA/PET is "0.5kg"), in which case the product
    // name is the only colour information there is.
    // Strip any parenthetical: variants carry either "(11101)" or "(#792B36)".
    const isSizeOnly = (t) => /^\d+(\.\d+)?\s?kg(\s*[x*]\s*\d+)?$/i.test(t);
    const firstSegment = variant.split("/")[0].replace(/\([^)]*\)/g, "").trim();
    const nameFromVariant = isSizeOnly(firstSegment) ? "" : firstSegment;
    const colourName = nameFromVariant || r.item;
    const key = colourCode || colourName;
    const s = colour(key, `${r.item} / ${variant}`);
    const weightKg = /0\.5\s?kg/i.test(variant) ? 0.5 : 1;

    for (let i = 0; i < qty; i++) {
      push({
        source: "bambu", brand: "Bambu Lab", material: materialOf(r.item),
        productLine: r.item, colourName, colourCode,
        hex: s.hex, hex2: s.hex2, finish: s.finish, weightKg,
        isRefill: /refill/i.test(variant), orderId: r.order_id,
        orderDate: r.order_date, pricePaidCad: Number((paid / qty).toFixed(2)),
      });
    }
  }

  // ---------- Amazon, third party ----------
  for (const r of parseCsv(amazonCsv)) {
    if (r.item.toLowerCase().includes("not filament")) continue;
    const key = `${r.brand}:${r.item}:${r.colour}`;
    const s = colour(key, key);
    push({
      source: "amazon", brand: r.brand, material: materialOf(r.item),
      productLine: r.item, colourName: r.colour, colourCode: "",
      hex: s.hex, hex2: s.hex2, finish: s.finish, weightKg: 1,
      isRefill: false, orderId: r.order_id || "", orderDate: r.order_date,
      pricePaidCad: null,
    });
  }

  return out;
}

// Compare as URLs: a plain `file://${argv[1]}` breaks on paths with spaces.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const here = dirname(fileURLToPath(import.meta.url));
  const spools = buildSpools(
    readFileSync(resolve(here, "../../printer/orders.csv"), "utf8"),
    readFileSync(resolve(here, "../../printer/orders-amazon.csv"), "utf8"),
  );
  const dest = resolve(here, "../src/data/spools.json");
  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, JSON.stringify(spools, null, 2));
  console.log(`Wrote ${spools.length} spools to ${dest}`);
}
