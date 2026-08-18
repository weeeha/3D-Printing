"use client";

import { useEffect, useState } from "react";

export type Theme = "system" | "light" | "dark";

export const THEME_KEY = "filament-shelf-theme";

/** "system" clears the attribute so prefers-color-scheme takes over again. */
export function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", theme);
}

function readStoredTheme(): Theme {
  try {
    const t = localStorage.getItem(THEME_KEY);
    if (t === "light" || t === "dark" || t === "system") return t;
  } catch {
    /* storage blocked; fall through to system */
  }
  return "system";
}

const ICONS: Record<Theme, React.ReactNode> = {
  system: (
    <>
      <rect x="3" y="4" width="14" height="10" rx="1.6" />
      <path d="M7 17h6" />
    </>
  ),
  light: (
    <>
      <circle cx="10" cy="10" r="3.6" />
      <path d="M10 2.4v1.8M10 15.8v1.8M17.6 10h-1.8M4.2 10H2.4M15.37 4.63l-1.27 1.27M5.9 14.1l-1.27 1.27M15.37 15.37l-1.27-1.27M5.9 5.9L4.63 4.63" />
    </>
  ),
  dark: <path d="M16.2 11.6A6.6 6.6 0 1 1 8.4 3.8a5.4 5.4 0 0 0 7.8 7.8Z" />,
};

const LABELS: Record<Theme, string> = {
  system: "Match system",
  light: "Light",
  dark: "Dark",
};

const ORDER: Theme[] = ["system", "light", "dark"];

export function ThemeToggle() {
  // Start at "system" so server and first client render agree. The inline
  // script in layout.tsx has already painted the right colours by now; this
  // effect only syncs the control's own highlighted segment.
  const [theme, setTheme] = useState<Theme>("system");

  useEffect(() => {
    setTheme(readStoredTheme());
  }, []);

  const choose = (t: Theme) => {
    setTheme(t);
    applyTheme(t);
    try {
      localStorage.setItem(THEME_KEY, t);
    } catch {
      /* storage blocked; the choice still applies for this page view */
    }
  };

  return (
    <div
      role="radiogroup"
      aria-label="Colour theme"
      className="inline-flex items-center gap-0.5 rounded-full border
                 border-[var(--rule)] p-0.5"
    >
      {ORDER.map((t) => {
        const active = theme === t;
        return (
          <button
            key={t}
            type="button"
            role="radio"
            aria-checked={active}
            aria-label={LABELS[t]}
            title={LABELS[t]}
            onClick={() => choose(t)}
            className={`grid h-7 w-7 place-items-center rounded-full transition-colors ${
              active
                ? "bg-[var(--control)] text-[var(--ink)]"
                : "text-[var(--muted)] hover:text-[var(--ink)]"
            }`}
          >
            <svg
              viewBox="0 0 20 20"
              className="h-[15px] w-[15px]"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              {ICONS[t]}
            </svg>
          </button>
        );
      })}
    </div>
  );
}
