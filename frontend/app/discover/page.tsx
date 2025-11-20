"use client"

import { useQuery } from "@tanstack/react-query"
import { motion } from "framer-motion"
import Link from "next/link"
import { apiClient } from "@/lib/api-client"
import { offlineDB } from "@/lib/offline-db"
import { useEffect, useState } from "react"

export default function DiscoverPage() {
  const [isOnline, setIsOnline] = useState(true)

  useEffect(() => {
    setIsOnline(navigator.onLine)

    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener("online", handleOnline)
    window.addEventListener("offline", handleOffline)

    return () => {
      window.removeEventListener("online", handleOnline)
      window.removeEventListener("offline", handleOffline)
    }
  }, [])

  // Fetch patterns from API when online
  const { data: onlinePatterns, isLoading } = useQuery({
    queryKey: ["discover-patterns"],
    queryFn: () => apiClient.discoverPatterns(0, 20),
    enabled: isOnline,
  })

  // Load local patterns when offline
  const [localPatterns, setLocalPatterns] = useState<any[]>([])

  useEffect(() => {
    if (!isOnline) {
      offlineDB.getAllPatterns().then(setLocalPatterns).catch(console.error)
    }
  }, [isOnline])

  const patterns = isOnline ? onlinePatterns?.items || [] : localPatterns

  return (
    <main className="min-h-screen bg-noise-dark p-4">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="text-noise-accent hover:underline mb-4 inline-block">
            ← Back to Museum
          </Link>
          <h1 className="text-4xl font-bold mb-2">Discover Patterns</h1>
          <p className="text-gray-400">
            {isOnline
              ? "Explore patterns created by the community"
              : "Viewing your locally saved patterns (offline)"}
          </p>
        </div>

        {/* Pattern Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-noise-gray rounded-lg h-64 skeleton" />
            ))}
          </div>
        ) : patterns.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {patterns.map((pattern, index) => (
              <motion.div
                key={pattern.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-noise-gray rounded-lg overflow-hidden hover:ring-2 hover:ring-noise-accent transition-all"
              >
                <Link href={`/exhibit/${pattern.exhibitType || pattern.exhibit_type}`}>
                  <div className="aspect-video bg-noise-dark flex items-center justify-center">
                    <span className="text-6xl opacity-20">🎨</span>
                  </div>
                  <div className="p-4">
                    <h3 className="font-bold text-lg mb-1">
                      {pattern.title || "Untitled Pattern"}
                    </h3>
                    <p className="text-sm text-gray-400 mb-3 capitalize">
                      {pattern.exhibitType || pattern.exhibit_type}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>❤️ {pattern.likesCount || pattern.likes_count || 0}</span>
                      <span>👁️ {pattern.viewsCount || pattern.views_count || 0}</span>
                      {!isOnline && (
                        <span
                          className={`ml-auto text-xs px-2 py-1 rounded ${
                            pattern.syncStatus === "synced"
                              ? "bg-green-600"
                              : pattern.syncStatus === "pending"
                                ? "bg-yellow-600"
                                : "bg-gray-600"
                          }`}
                        >
                          {pattern.syncStatus}
                        </span>
                      )}
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <p className="text-gray-400 text-lg">
              {isOnline ? "No patterns found" : "No saved patterns yet"}
            </p>
            <Link
              href="/"
              className="inline-block mt-4 px-6 py-3 bg-noise-accent rounded-lg font-semibold hover:bg-noise-accent/80 transition-colors"
            >
              Create Your First Pattern
            </Link>
          </div>
        )}
      </div>
    </main>
  )
}
