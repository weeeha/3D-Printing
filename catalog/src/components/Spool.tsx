"use client";

import type { Spool } from "@/lib/spools";
import type { Status } from "@/lib/status";
import { STATUS_LABEL } from "@/lib/status";

/** Lighten a hex toward white by `amount` (0..1). Used for the silk sheen. */
function lighten(hex: string, amount: number): string {
  const n = parseInt(hex.slice(1), 16);
  const mix = (c: number) => Math.round(c + (255 - c) * amount);
  const r = mix((n >> 16) & 255);
  const g = mix((n >> 8) & 255);
  const b = mix(n & 255);
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, "0")}`;
}

const RAINBOW = ["#E24B4B", "#EDB63C", "#5FBF7A", "#4A9BD6", "#9B5FBF"];

/** Turns of filament, from the hub out to the flange edge. */
const WINDINGS = Array.from({ length: 16 }, (_, i) => 18.5 + i * 1.6);

/** Fixed speckle offsets: deterministic, so spools do not shimmer on re-render. */
const SPECKLES: [number, number, number][] = [
  [38, 34, 1.5], [62, 30, 1.1], [70, 58, 1.4],
  [32, 64, 1.2], [50, 24, 1.0], [56, 72, 1.3],
];

export function SpoolSvg({
  spool,
  status,
  size = 64,
  onClick,
}: {
  spool: Spool;
  status: Status;
  size?: number;
  onClick?: () => void;
}) {
  const uid = spool.id.replace(/[^a-zA-Z0-9-]/g, "");
  const gradId = `g-${uid}`;
  const glowId = `bloom-${uid}`;
  const clipId = `clip-${uid}`;
  const shadeId = `shade-${uid}`;
  const { finish, hex, hex2 } = spool;

  const label = `${spool.colourName}, ${spool.productLine}, ${STATUS_LABEL[status]}`;

  const activate = () => onClick?.();
  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      activate();
    }
  };

  // Gone spools show the empty slot rather than disappearing, so the shelf
  // reads as having a hole where something used to be.
  if (status === "gone") {
    return (
      <svg
        viewBox="0 0 100 100"
        width={size}
        height={size}
        role="button"
        tabIndex={0}
        aria-label={label}
        onClick={activate}
        onKeyDown={onKey}
        className="cursor-pointer"
      >
        <circle
          cx="50" cy="50" r="46"
          fill="none" stroke="var(--muted)" strokeWidth="1.5"
          strokeDasharray="4 5" opacity="0.4"
        />
        <circle cx="50" cy="50" r="16" fill="none" stroke="var(--muted)"
          strokeWidth="1" opacity="0.3" />
      </svg>
    );
  }

  const coilFill =
    finish === "dual" || finish === "rainbow" || finish === "silk"
      ? `url(#${gradId})`
      : hex;
  const coilOpacity = finish === "translucent" ? 0.5 : 1;

  return (
    <svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      role="button"
      tabIndex={0}
      aria-label={label}
      onClick={activate}
      onKeyDown={onKey}
      className="cursor-pointer"
      filter={finish === "glow" ? `url(#${glowId})` : undefined}
    >
      <defs>
        {finish === "silk" && (
          <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={hex} />
            <stop offset="42%" stopColor={lighten(hex, 0.55)} />
            <stop offset="58%" stopColor={lighten(hex, 0.55)} />
            <stop offset="100%" stopColor={hex} />
          </linearGradient>
        )}
        {finish === "dual" && (
          <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={hex} />
            <stop offset="50%" stopColor={hex} />
            <stop offset="50%" stopColor={hex2 ?? hex} />
            <stop offset="100%" stopColor={hex2 ?? hex} />
          </linearGradient>
        )}
        {finish === "rainbow" && (
          <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
            {RAINBOW.map((c, i) => (
              <stop key={c} offset={`${(i / (RAINBOW.length - 1)) * 100}%`} stopColor={c} />
            ))}
          </linearGradient>
        )}
        {finish === "glow" && (
          <filter id={glowId} x="-25%" y="-25%" width="150%" height="150%">
            <feGaussianBlur stdDeviation="2.5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        )}
        <radialGradient id={shadeId} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#000" stopOpacity="0.30" />
          <stop offset="40%" stopColor="#000" stopOpacity="0" />
          <stop offset="82%" stopColor="#000" stopOpacity="0" />
          <stop offset="100%" stopColor="#000" stopOpacity="0.34" />
        </radialGradient>
        {status === "low" && (
          <clipPath id={clipId}>
            <rect x="0" y="50" width="100" height="50" />
          </clipPath>
        )}
      </defs>

      {/* Outer flange, the dark plastic disc you actually see edge-on */}
      <circle cx="50" cy="50" r="48" fill="#333834" />
      <circle cx="50" cy="50" r="48" fill="none" stroke="#12140F" strokeWidth="1.5" />

      {/* A part-used spool shows coil only in the lower half of the flange */}
      <g clipPath={status === "low" ? `url(#${clipId})` : undefined}
         opacity={status === "low" ? 0.85 : 1}>
        <circle cx="50" cy="50" r="44" fill={coilFill} opacity={coilOpacity} />

        {/* Winding texture: closely spaced turns, alternating light and dark,
            so the coil reads as wound filament rather than a flat disc. */}
        <g fill="none" strokeWidth="0.9">
          {WINDINGS.map((r, i) => (
            <circle
              key={r}
              cx="50" cy="50" r={r}
              stroke={i % 2 ? "rgba(255,255,255,.16)" : "rgba(0,0,0,.20)"}
            />
          ))}
        </g>

        {/* Depth: darker toward the outer edge and into the hub well */}
        <circle cx="50" cy="50" r="44" fill={`url(#${shadeId})`} />

        {(finish === "sparkle" || finish === "marble") && (
          <g fill="#FFFFFF" opacity="0.75">
            {SPECKLES.map(([cx, cy, r]) => (
              <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r={r} />
            ))}
          </g>
        )}
      </g>

      {/* Hub and centre hole */}
      <circle cx="50" cy="50" r="16" fill="#1A1D1B" />
      <circle cx="50" cy="50" r="6" fill="var(--ground)" />
    </svg>
  );
}
