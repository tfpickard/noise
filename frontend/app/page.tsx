"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { OfflineIndicator } from "@/components/ui/offline-indicator"

const exhibits = [
  {
    id: "perlin",
    title: "Perlin Noise",
    description: "Classic smooth gradient noise for natural-looking patterns",
    color: "from-blue-500 to-purple-500",
  },
  {
    id: "simplex",
    title: "Simplex Noise",
    description: "Improved Perlin with better performance and visual quality",
    color: "from-green-500 to-teal-500",
  },
  {
    id: "worley",
    title: "Worley Noise",
    description: "Cellular patterns based on Voronoi diagrams",
    color: "from-orange-500 to-red-500",
  },
  {
    id: "fbm",
    title: "Fractional Brownian Motion",
    description: "Multi-octave noise for complex terrain-like patterns",
    color: "from-purple-500 to-pink-500",
  },
  {
    id: "turbulence",
    title: "Turbulence",
    description: "Chaotic noise patterns with high frequency detail",
    color: "from-cyan-500 to-blue-500",
  },
  {
    id: "marble",
    title: "Marble",
    description: "Sine-distorted noise creating marble-like textures",
    color: "from-gray-400 to-gray-600",
  },
]

export default function Home() {
  return (
    <main className="min-h-screen noise-texture">
      <OfflineIndicator />

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto"
        >
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Visual Noise Museum
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8 text-balance">
            Explore the art and mathematics of procedural noise generation with cutting-edge web
            technologies
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/exhibit/perlin"
              className="px-8 py-3 bg-noise-accent hover:bg-noise-accent/80 rounded-lg font-semibold transition-colors"
            >
              Start Exploring
            </Link>
            <Link
              href="/discover"
              className="px-8 py-3 bg-noise-gray hover:bg-noise-gray/80 rounded-lg font-semibold transition-colors"
            >
              Discover Gallery
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Exhibits Grid */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center">Noise Exhibits</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exhibits.map((exhibit, index) => (
            <motion.div
              key={exhibit.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
            >
              <Link
                href={`/exhibit/${exhibit.id}`}
                className="block group relative overflow-hidden rounded-xl bg-noise-gray hover:bg-noise-gray/80 transition-all"
              >
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${exhibit.color} opacity-0 group-hover:opacity-20 transition-opacity`}
                />
                <div className="p-6 relative z-10">
                  <h3 className="text-2xl font-bold mb-2 group-hover:text-white transition-colors">
                    {exhibit.title}
                  </h3>
                  <p className="text-gray-400 group-hover:text-gray-300 transition-colors">
                    {exhibit.description}
                  </p>
                  <div className="mt-4 text-noise-accent group-hover:translate-x-2 transition-transform inline-block">
                    Explore →
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="text-center">
            <div className="text-4xl mb-4">🚀</div>
            <h3 className="text-xl font-bold mb-2">Bleeding Edge Tech</h3>
            <p className="text-gray-400">
              Built with Next.js 15, React 19, WebGPU, and modern CSS features
            </p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-4">📱</div>
            <h3 className="text-xl font-bold mb-2">Offline First</h3>
            <p className="text-gray-400">
              Works fully offline with IndexedDB storage and progressive enhancement
            </p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-4">🎨</div>
            <h3 className="text-xl font-bold mb-2">Community Driven</h3>
            <p className="text-gray-400">
              Share, remix, and discover patterns created by the community
            </p>
          </div>
        </div>
      </section>
    </main>
  )
}
