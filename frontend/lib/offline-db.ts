export interface StoredPattern {
  id: string;
  title?: string;
  parameters: Record<string, unknown>;
  updatedAt: number;
}

const DB_KEY = "vnm-patterns";

export function savePattern(pattern: StoredPattern): void {
  const existing = listPatterns();
  const next = new Map(existing.map((p) => [p.id, p]));
  next.set(pattern.id, pattern);
  localStorage.setItem(DB_KEY, JSON.stringify(Array.from(next.values())));
}

export function listPatterns(): StoredPattern[] {
  const raw = localStorage.getItem(DB_KEY);
  return raw ? (JSON.parse(raw) as StoredPattern[]) : [];
}
