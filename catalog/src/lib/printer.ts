import type { Spool } from "./spools";
import type { Status } from "./status";

export type PrinterSlot = {
  slot: string;
  uuid: string;
  sku: string;
  productLine: string;
  material: string;
  hex: string | null;
  /** null when the tag is unreadable or absent, so no estimate exists. */
  remain: number | null;
};

export type PrinterState = {
  readAt: string;
  printing: string | null;
  percent: number | null;
  ams: { unit: number; humidityRh: number | null; tempC: number | null }[];
  slots: PrinterSlot[];
};

/** Below this, a spool is worth flagging before you start a long print. */
export const LOW_THRESHOLD = 30;

export function statusFromRemain(remain: number | null): Status | null {
  if (remain === null) return null;
  if (remain === 0) return "gone";
  if (remain < LOW_THRESHOLD) return "low";
  return "have";
}

/**
 * Tie each AMS slot to one ledger spool.
 *
 * The RFID tag identifies a filament product and colour, not which of your
 * seven identical charcoal rolls is loaded. So a slot claims the first
 * unclaimed spool matching product line and colour, and each spool can be
 * claimed only once. That is honest about the ambiguity rather than pretending
 * to know which physical roll is in the machine.
 */
export function matchSlots(
  slots: PrinterSlot[],
  spools: Spool[],
): Record<string, string> {
  const claimed = new Set<string>();
  const bySlot: Record<string, string> = {};

  for (const slot of slots) {
    if (!slot.hex) continue;
    const hex = slot.hex.toUpperCase();
    const candidates = spools.filter(
      (s) =>
        !claimed.has(s.id) &&
        s.hex.toUpperCase() === hex &&
        s.productLine.toLowerCase() === slot.productLine.toLowerCase(),
    );
    // Fall back to colour alone when the product name does not line up, which
    // happens for bundles the printer reports under a generic product name.
    const pool = candidates.length
      ? candidates
      : spools.filter((s) => !claimed.has(s.id) && s.hex.toUpperCase() === hex);
    const pick = pool[0];
    if (!pick) continue;
    claimed.add(pick.id);
    bySlot[slot.slot] = pick.id;
  }
  return bySlot;
}

/** Statuses the printer is confident about, keyed by spool id. */
export function derivedStatuses(
  state: PrinterState,
  spools: Spool[],
): Record<string, Status> {
  const bySlot = matchSlots(state.slots, spools);
  const out: Record<string, Status> = {};
  for (const slot of state.slots) {
    const id = bySlot[slot.slot];
    const st = statusFromRemain(slot.remain);
    if (id && st) out[id] = st;
  }
  return out;
}
