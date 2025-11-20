/**
 * IndexedDB wrapper for offline storage
 * Stores pattern configurations and user data
 */

import { openDB, DBSchema, IDBPDatabase } from "idb"

interface Pattern {
  id: string
  exhibitType: string
  title?: string
  description?: string
  parameters: Record<string, any>
  seed?: number
  thumbnail?: string
  createdAt: number
  updatedAt: number
  syncStatus: "synced" | "pending" | "local"
  remoteId?: string
}

interface Settings {
  key: string
  value: any
}

interface NoiseMuseumDB extends DBSchema {
  patterns: {
    key: string
    value: Pattern
    indexes: {
      "by-exhibit": string
      "by-sync-status": string
      "by-created": number
    }
  }
  settings: {
    key: string
    value: Settings
  }
  queue: {
    key: string
    value: {
      id: string
      action: "create" | "update" | "delete"
      resource: "pattern" | "like" | "collection"
      data: any
      timestamp: number
    }
    indexes: {
      "by-timestamp": number
    }
  }
}

class OfflineDB {
  private db: IDBPDatabase<NoiseMuseumDB> | null = null
  private readonly dbName = "noise-museum"
  private readonly version = 1

  async init() {
    if (this.db) return this.db

    this.db = await openDB<NoiseMuseumDB>(this.dbName, this.version, {
      upgrade(db) {
        // Patterns store
        if (!db.objectStoreNames.contains("patterns")) {
          const patternStore = db.createObjectStore("patterns", { keyPath: "id" })
          patternStore.createIndex("by-exhibit", "exhibitType")
          patternStore.createIndex("by-sync-status", "syncStatus")
          patternStore.createIndex("by-created", "createdAt")
        }

        // Settings store
        if (!db.objectStoreNames.contains("settings")) {
          db.createObjectStore("settings", { keyPath: "key" })
        }

        // Sync queue store
        if (!db.objectStoreNames.contains("queue")) {
          const queueStore = db.createObjectStore("queue", { keyPath: "id" })
          queueStore.createIndex("by-timestamp", "timestamp")
        }
      },
    })

    return this.db
  }

  // Pattern operations
  async savePattern(pattern: Omit<Pattern, "createdAt" | "updatedAt">) {
    const db = await this.init()
    const now = Date.now()
    const fullPattern: Pattern = {
      ...pattern,
      createdAt: now,
      updatedAt: now,
      syncStatus: pattern.syncStatus || "local",
    }
    await db.put("patterns", fullPattern)
    return fullPattern
  }

  async getPattern(id: string) {
    const db = await this.init()
    return db.get("patterns", id)
  }

  async getAllPatterns() {
    const db = await this.init()
    return db.getAll("patterns")
  }

  async getPatternsByExhibit(exhibitType: string) {
    const db = await this.init()
    return db.getAllFromIndex("patterns", "by-exhibit", exhibitType)
  }

  async updatePattern(id: string, updates: Partial<Pattern>) {
    const db = await this.init()
    const pattern = await db.get("patterns", id)
    if (!pattern) throw new Error("Pattern not found")

    const updated = {
      ...pattern,
      ...updates,
      updatedAt: Date.now(),
    }
    await db.put("patterns", updated)
    return updated
  }

  async deletePattern(id: string) {
    const db = await this.init()
    await db.delete("patterns", id)
  }

  // Settings operations
  async getSetting<T = any>(key: string): Promise<T | undefined> {
    const db = await this.init()
    const setting = await db.get("settings", key)
    return setting?.value
  }

  async setSetting(key: string, value: any) {
    const db = await this.init()
    await db.put("settings", { key, value })
  }

  // Sync queue operations
  async addToQueue(
    action: "create" | "update" | "delete",
    resource: "pattern" | "like" | "collection",
    data: any,
  ) {
    const db = await this.init()
    const id = `${resource}-${action}-${Date.now()}-${Math.random()}`
    await db.add("queue", {
      id,
      action,
      resource,
      data,
      timestamp: Date.now(),
    })
    return id
  }

  async getQueue() {
    const db = await this.init()
    return db.getAllFromIndex("queue", "by-timestamp")
  }

  async removeFromQueue(id: string) {
    const db = await this.init()
    await db.delete("queue", id)
  }

  async clearQueue() {
    const db = await this.init()
    const tx = db.transaction("queue", "readwrite")
    await tx.store.clear()
    await tx.done
  }

  // Utility
  async clear() {
    const db = await this.init()
    const tx = db.transaction(["patterns", "settings", "queue"], "readwrite")
    await Promise.all([
      tx.objectStore("patterns").clear(),
      tx.objectStore("settings").clear(),
      tx.objectStore("queue").clear(),
    ])
    await tx.done
  }
}

// Singleton instance
export const offlineDB = new OfflineDB()
