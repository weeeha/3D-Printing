import { formatDuration, formatMm, totalGrams, type ModelRecord } from "@/lib/models";
import { formatCad, sliceCost } from "@/lib/model-cost";

/** "49m · 40.3 g · $1.05", or "Not sliced · G-code conflict". `onInk` is for a selected (ink) row. */
export function ModelMeta({ m, onInk = false }: { m: ModelRecord; onInk?: boolean }) {
  if (m.slice.status === "failed") {
    return <><span className={onInk ? "" : "text-[var(--warn)]"}>Not sliced</span> · {m.slice.short}</>;
  }
  const cost = sliceCost(m.slice);
  return <>{formatDuration(m.slice.seconds)} · {formatMm(totalGrams(m.slice))} g{cost === null ? "" : ` · ${formatCad(cost)}`}</>;
}
