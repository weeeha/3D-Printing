import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Filament Shelf",
  description: "Every spool bought, and what is still on the shelf.",
};

/**
 * Runs before first paint so an explicit light/dark choice is applied without a
 * flash of the wrong theme. Deliberately tiny, synchronous and failure-tolerant:
 * if localStorage throws (private mode, blocked storage) we fall through to the
 * system preference rather than breaking the page.
 */
const NO_FLASH = `(function(){try{var t=localStorage.getItem("filament-shelf-theme");if(t==="light"||t==="dark"){document.documentElement.setAttribute("data-theme",t);}}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: NO_FLASH }} />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
