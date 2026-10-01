import Link from "next/link";

const PAGES = [
  { id: "shelf", href: "/", label: "Filament Shelf" },
  { id: "models", href: "/models", label: "Models" },
] as const;

export function SiteNav({ current }: { current: (typeof PAGES)[number]["id"] }) {
  return (
    <nav aria-label="Catalog pages" className="flex w-max max-w-full border border-[var(--rule)]">
      {PAGES.map((p) => (
        <Link
          key={p.id}
          href={p.href}
          aria-current={p.id === current ? "page" : undefined}
          className={`px-3.5 py-1.5 text-[11px] uppercase tracking-[0.12em] ${p.id === current
            ? "bg-[var(--ink)] text-[var(--ground)]"
            : "text-[var(--muted)] hover:text-[var(--ink)]"}`}
        >
          {p.label}
        </Link>
      ))}
    </nav>
  );
}
