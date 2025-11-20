"use client"

import { use, useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { renderNoiseToCanvas } from "@/lib/noise-generator"
import { syncManager } from "@/lib/sync-manager"

interface ExhibitParams {
  params: Promise<{ id: string }>
}

const exhibitDefaults: Record<string, any> = {
  perlin: {
    scale: 0.01,
    seed: Date.now(),
    colorMode: "grayscale",
  },
  fbm: {
    scale: 0.005,
    octaves: 6,
    persistence: 0.5,
    seed: Date.now(),
    colorMode: "grayscale",
  },
  turbulence: {
    scale: 0.01,
    seed: Date.now(),
    colorMode: "grayscale",
  },
  marble: {
    scale: 0.1,
    turbulencePower: 5,
    seed: Date.now(),
    colorMode: "grayscale",
  },
  worley: {
    cellCount: 10,
    seed: Date.now(),
    colorMode: "grayscale",
  },
}

export default function ExhibitPage({ params }: ExhibitParams) {
  const { id } = use(params)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [parameters, setParameters] = useState(exhibitDefaults[id] || exhibitDefaults.perlin)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    // Set canvas size
    const dpr = window.devicePixelRatio || 1
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr

    // Render noise
    renderNoiseToCanvas(canvas, id, parameters)
  }, [id, parameters])

  const handleParameterChange = (key: string, value: any) => {
    setParameters((prev) => ({ ...prev, [key]: value }))
  }

  const randomize = () => {
    setParameters((prev) => ({ ...prev, seed: Date.now() }))
  }

  const savePattern = async () => {
    setSaving(true)
    try {
      await syncManager.savePattern({
        exhibitType: id,
        title: `${id.charAt(0).toUpperCase() + id.slice(1)} Pattern`,
        parameters,
        seed: parameters.seed,
        isPublic: true,
      })
      alert("Pattern saved successfully!")
    } catch (error) {
      console.error("Failed to save pattern:", error)
      alert("Failed to save pattern")
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="min-h-screen bg-noise-dark p-4">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <Link href="/" className="text-noise-accent hover:underline">
            ← Back to Museum
          </Link>
          <h1 className="text-3xl font-bold capitalize">{id} Noise</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Canvas */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-noise-gray rounded-lg overflow-hidden aspect-video"
            >
              <canvas
                ref={canvasRef}
                className="w-full h-full"
                style={{ imageRendering: "pixelated" }}
              />
            </motion.div>

            {/* Actions */}
            <div className="mt-4 flex gap-3">
              <button
                onClick={randomize}
                className="px-6 py-2 bg-noise-accent hover:bg-noise-accent/80 rounded-lg font-semibold transition-colors"
              >
                Randomize
              </button>
              <button
                onClick={savePattern}
                disabled={saving}
                className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg font-semibold transition-colors"
              >
                {saving ? "Saving..." : "Save Pattern"}
              </button>
            </div>
          </div>

          {/* Controls */}
          <div className="bg-noise-gray rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Parameters</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Scale</label>
                <input
                  type="range"
                  min="0.001"
                  max="0.1"
                  step="0.001"
                  value={parameters.scale}
                  onChange={(e) => handleParameterChange("scale", parseFloat(e.target.value))}
                  className="w-full"
                />
                <span className="text-xs text-gray-400">{parameters.scale?.toFixed(3)}</span>
              </div>

              {id === "fbm" && (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-2">Octaves</label>
                    <input
                      type="range"
                      min="1"
                      max="8"
                      step="1"
                      value={parameters.octaves}
                      onChange={(e) => handleParameterChange("octaves", parseInt(e.target.value))}
                      className="w-full"
                    />
                    <span className="text-xs text-gray-400">{parameters.octaves}</span>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Persistence</label>
                    <input
                      type="range"
                      min="0.1"
                      max="0.9"
                      step="0.1"
                      value={parameters.persistence}
                      onChange={(e) =>
                        handleParameterChange("persistence", parseFloat(e.target.value))
                      }
                      className="w-full"
                    />
                    <span className="text-xs text-gray-400">{parameters.persistence}</span>
                  </div>
                </>
              )}

              {id === "worley" && (
                <div>
                  <label className="block text-sm font-medium mb-2">Cell Count</label>
                  <input
                    type="range"
                    min="3"
                    max="30"
                    step="1"
                    value={parameters.cellCount}
                    onChange={(e) => handleParameterChange("cellCount", parseInt(e.target.value))}
                    className="w-full"
                  />
                  <span className="text-xs text-gray-400">{parameters.cellCount}</span>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Color Mode</label>
                <select
                  value={parameters.colorMode}
                  onChange={(e) => handleParameterChange("colorMode", e.target.value)}
                  className="w-full bg-noise-dark border border-gray-600 rounded px-3 py-2"
                >
                  <option value="grayscale">Grayscale</option>
                  <option value="hue">Hue Gradient</option>
                  <option value="gradient">Two-Color Gradient</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Seed</label>
                <input
                  type="number"
                  value={parameters.seed}
                  onChange={(e) => handleParameterChange("seed", parseInt(e.target.value))}
                  className="w-full bg-noise-dark border border-gray-600 rounded px-3 py-2"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
