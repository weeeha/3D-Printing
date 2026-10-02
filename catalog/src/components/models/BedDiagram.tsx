import { BED, NO_GO, type Box } from "@/lib/models";

type Footprint = { box: Box; tower: boolean };

/**
 * The plate seen from above, front edge at the bottom: each part's footprint,
 * the prime tower for multi-colour prints, and the P1S no-go corner.
 */
export function BedDiagram({ footprints, tone }: { footprints: Footprint[]; tone: "accent" | "warn" }) {
  const colour = `var(--${tone})`;
  const hasTower = footprints.some((f) => f.tower);
  const [nx0, ny0, nx1, ny1] = NO_GO;
  return (
    <div className="flex flex-col gap-2">
      <svg viewBox="-6 -6 268 284" role="img" aria-label="Footprint on the 256 by 256 mm bed" className="block w-full max-w-[220px] h-auto">
        <defs>
          <pattern id="no-go-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="6" style={{ stroke: "var(--muted)" }} strokeWidth="1.5" />
          </pattern>
        </defs>
        <rect x="0" y="0" width={BED} height={BED} style={{ fill: "var(--ground)", stroke: "var(--rule)" }} strokeWidth="1.5" />
        <rect x={nx0} y={BED - ny1} width={nx1 - nx0} height={ny1 - ny0} fill="url(#no-go-hatch)" style={{ stroke: "var(--muted)" }} strokeWidth="1" />
        {footprints.map(({ box: [x0, y0, x1, y1], tower }, i) => (
          <rect
            key={i}
            x={x0}
            y={BED - y1}
            width={x1 - x0}
            height={y1 - y0}
            style={{ fill: tower ? "var(--muted)" : colour, fillOpacity: tower ? 0.25 : 0.2, stroke: tower ? "var(--muted)" : colour }}
            strokeWidth="1.5"
          />
        ))}
        <text x={BED / 2} y="274" textAnchor="middle" style={{ fill: "var(--muted)", font: "10px ui-monospace, monospace" }}>
          front · 256 mm
        </text>
      </svg>
      <div className="flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-[var(--muted)]">
        <span><i className="inline-block w-2.5 h-2.5 mr-1.5 align-[-1px] opacity-50" style={{ background: colour }} />parts</span>
        {hasTower && <span><i className="inline-block w-2.5 h-2.5 mr-1.5 align-[-1px] opacity-50 bg-[var(--muted)]" />prime tower</span>}
        <span><i className="inline-block w-2.5 h-2.5 mr-1.5 align-[-1px] opacity-35 bg-[var(--muted)]" />no-go corner</span>
      </div>
    </div>
  );
}
