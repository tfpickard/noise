import type { ReactNode } from "react";
import "./globals.css";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <header className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="text-lg font-semibold">Visual Noise Museum</div>
          <span className="text-xs rounded-full bg-emerald-600/20 px-3 py-1 border border-emerald-500/40">
            Offline-first demo shell
          </span>
        </header>
        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}
