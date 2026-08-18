import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Filament Shelf",
  description: "Every spool bought, and what is still on the shelf.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
