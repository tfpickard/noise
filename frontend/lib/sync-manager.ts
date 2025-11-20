import { apiRequest } from "./api-client";
import { listPatterns, savePattern, type StoredPattern } from "./offline-db";

export interface SyncResult {
  synced: number;
  queued: number;
}

export async function enqueueOfflineSave(pattern: StoredPattern): Promise<void> {
  savePattern(pattern);
}

export async function syncPending(): Promise<SyncResult> {
  const patterns = listPatterns();
  let synced = 0;
  for (const pattern of patterns) {
    try {
      await apiRequest({ path: "/patterns", method: "POST", body: pattern });
      synced += 1;
    } catch (error) {
      console.warn("Sync failed, keeping offline", error);
    }
  }
  return { synced, queued: patterns.length - synced };
}
