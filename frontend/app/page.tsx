import Link from "next/link";
import { motion } from "framer-motion";

const tiles = [
  {
    title: "Offline Canvas Exhibits",
    description:
      "Render procedural noise fully client-side with OffscreenCanvas and WebGPU compute shaders when available.",
  },
  {
    title: "Sync Queue",
    description:
      "Edits persist to IndexedDB instantly and opportunistically sync to the FastAPI backend when connectivity returns.",
  },
  {
    title: "Collaboration Ready",
    description:
      "WebSocket endpoints back multi-cursor sessions; UI hides gracefully when offline.",
  },
];

export default function Page() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-3">
        {tiles.map((tile) => (
          <motion.article
            key={tile.title}
            className="offline-card rounded-xl border border-slate-800 bg-slate-900/40 p-4 shadow-lg"
            whileHover={{ scale: 1.01 }}
            transition={{ type: "spring", stiffness: 220, damping: 20 }}
          >
            <h2 className="text-lg font-semibold mb-2">{tile.title}</h2>
            <p className="text-sm text-slate-300 leading-relaxed">{tile.description}</p>
          </motion.article>
        ))}
      </div>
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-300">
            API client is centralized in <code>lib/api-client.ts</code> and swaps to IndexedDB-first storage when offline.
          </p>
        </div>
        <Link className="text-cyan-400 text-sm" href="/discover">
          Discover
        </Link>
      </div>
    </div>
  );
}
