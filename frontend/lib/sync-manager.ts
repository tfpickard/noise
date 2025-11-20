/**
 * Sync manager for offline-first architecture
 * Handles syncing local data with backend when online
 */

import { apiClient } from "./api-client"
import { offlineDB } from "./offline-db"

class SyncManager {
  private syncInProgress = false
  private syncInterval: NodeJS.Timeout | null = null

  /**
   * Start automatic background sync
   */
  startAutoSync(intervalMs = 30000) {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
    }

    this.syncInterval = setInterval(() => {
      if (navigator.onLine) {
        this.sync().catch(console.error)
      }
    }, intervalMs)

    // Also sync when coming back online
    window.addEventListener("online", () => {
      this.sync().catch(console.error)
    })
  }

  /**
   * Stop automatic sync
   */
  stopAutoSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
      this.syncInterval = null
    }
  }

  /**
   * Manually trigger sync
   */
  async sync() {
    if (this.syncInProgress || !navigator.onLine) {
      return { success: false, reason: "sync-in-progress or offline" }
    }

    this.syncInProgress = true
    const results = {
      uploaded: 0,
      failed: 0,
      errors: [] as Error[],
    }

    try {
      const queue = await offlineDB.getQueue()

      for (const item of queue) {
        try {
          await this.processQueueItem(item)
          await offlineDB.removeFromQueue(item.id)
          results.uploaded++
        } catch (error) {
          console.error("Failed to sync item:", item, error)
          results.failed++
          results.errors.push(
            error instanceof Error ? error : new Error(String(error)),
          )

          // Remove from queue if it's a client error (4xx)
          if (error instanceof Error && error.message.includes("4")) {
            await offlineDB.removeFromQueue(item.id)
          }
        }
      }

      // Update sync status of local patterns
      await this.updatePatternSyncStatus()

      return { success: true, ...results }
    } finally {
      this.syncInProgress = false
    }
  }

  /**
   * Process a single queue item
   */
  private async processQueueItem(item: any) {
    const { action, resource, data } = item

    if (resource === "pattern") {
      switch (action) {
        case "create":
          const created = await apiClient.createPattern(data)
          // Update local pattern with remote ID
          await offlineDB.updatePattern(data.id, {
            remoteId: created.id,
            syncStatus: "synced",
          })
          break

        case "update":
          if (data.remoteId) {
            await apiClient.updatePattern(data.remoteId, data)
            await offlineDB.updatePattern(data.id, { syncStatus: "synced" })
          }
          break

        case "delete":
          if (data.remoteId) {
            await apiClient.deletePattern(data.remoteId)
          }
          break
      }
    } else if (resource === "like") {
      if (action === "create") {
        await apiClient.likePattern(data.patternId)
      } else if (action === "delete") {
        await apiClient.unlikePattern(data.patternId)
      }
    }
  }

  /**
   * Update sync status of local patterns
   */
  private async updatePatternSyncStatus() {
    const patterns = await offlineDB.getAllPatterns()

    for (const pattern of patterns) {
      if (pattern.syncStatus === "pending" && pattern.remoteId) {
        // Verify it exists on server
        try {
          await apiClient.getPattern(pattern.remoteId)
          await offlineDB.updatePattern(pattern.id, { syncStatus: "synced" })
        } catch (error) {
          // Pattern doesn't exist on server, mark as local
          await offlineDB.updatePattern(pattern.id, {
            syncStatus: "local",
            remoteId: undefined,
          })
        }
      }
    }
  }

  /**
   * Save pattern with offline support
   */
  async savePattern(pattern: {
    exhibitType: string
    title?: string
    description?: string
    parameters: Record<string, any>
    seed?: number
    isPublic?: boolean
  }) {
    const id = `local-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    // Save locally first
    const localPattern = await offlineDB.savePattern({
      id,
      ...pattern,
      syncStatus: "pending",
    })

    // Try to sync immediately if online
    if (navigator.onLine) {
      try {
        const remotePattern = await apiClient.createPattern(pattern)
        await offlineDB.updatePattern(id, {
          remoteId: remotePattern.id,
          syncStatus: "synced",
        })
        return { ...localPattern, remoteId: remotePattern.id }
      } catch (error) {
        // Add to queue for later sync
        await offlineDB.addToQueue("create", "pattern", { id, ...pattern })
      }
    } else {
      // Add to queue for later sync
      await offlineDB.addToQueue("create", "pattern", { id, ...pattern })
    }

    return localPattern
  }

  /**
   * Delete pattern with offline support
   */
  async deletePattern(id: string) {
    const pattern = await offlineDB.getPattern(id)

    if (!pattern) {
      throw new Error("Pattern not found")
    }

    // Delete locally
    await offlineDB.deletePattern(id)

    // Queue for sync if it has a remote ID
    if (pattern.remoteId) {
      if (navigator.onLine) {
        try {
          await apiClient.deletePattern(pattern.remoteId)
        } catch (error) {
          await offlineDB.addToQueue("delete", "pattern", {
            remoteId: pattern.remoteId,
          })
        }
      } else {
        await offlineDB.addToQueue("delete", "pattern", {
          remoteId: pattern.remoteId,
        })
      }
    }
  }
}

// Singleton instance
export const syncManager = new SyncManager()
