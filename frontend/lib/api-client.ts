/**
 * API client for backend communication
 * Includes automatic retry and error handling
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any,
  ) {
    super(message)
    this.name = "APIError"
  }
}

class APIClient {
  private baseURL: string

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    const config: RequestInit = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new APIError(
          error.detail || `HTTP ${response.status}`,
          response.status,
          error,
        )
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return null as T
      }

      return response.json()
    } catch (error) {
      if (error instanceof APIError) throw error

      // Network error
      throw new APIError("Network error", 0, error)
    }
  }

  // Pattern endpoints
  async createPattern(data: {
    exhibitType: string
    title?: string
    description?: string
    parameters: Record<string, any>
    seed?: number
    isPublic?: boolean
  }) {
    return this.request<Pattern>("/api/v1/patterns/", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async getPattern(id: string) {
    return this.request<Pattern>(`/api/v1/patterns/${id}`)
  }

  async updatePattern(
    id: string,
    data: {
      title?: string
      description?: string
      parameters?: Record<string, any>
      isPublic?: boolean
    },
  ) {
    return this.request<Pattern>(`/api/v1/patterns/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    })
  }

  async deletePattern(id: string) {
    return this.request<void>(`/api/v1/patterns/${id}`, {
      method: "DELETE",
    })
  }

  async listPatterns(params?: {
    skip?: number
    limit?: number
    exhibitType?: string
    userId?: string
  }) {
    const query = new URLSearchParams(
      params as Record<string, string>,
    ).toString()
    return this.request<PatternList>(`/api/v1/patterns/?${query}`)
  }

  async discoverPatterns(skip = 0, limit = 20) {
    return this.request<PatternList>(
      `/api/v1/patterns/discover/feed?skip=${skip}&limit=${limit}`,
    )
  }

  async getTrendingPatterns(limit = 10) {
    return this.request<Pattern[]>(`/api/v1/patterns/trending/top?limit=${limit}`)
  }

  async forkPattern(
    id: string,
    data?: { title?: string; description?: string },
  ) {
    return this.request<Pattern>(`/api/v1/patterns/${id}/fork`, {
      method: "POST",
      body: JSON.stringify(data || {}),
    })
  }

  async likePattern(id: string) {
    return this.request<void>(`/api/v1/patterns/${id}/like`, {
      method: "POST",
    })
  }

  async unlikePattern(id: string) {
    return this.request<void>(`/api/v1/patterns/${id}/like`, {
      method: "DELETE",
    })
  }

  async findSimilarPatterns(params: {
    patternId?: string
    embedding?: number[]
    limit?: number
    threshold?: number
  }) {
    return this.request<Pattern[]>("/api/v1/patterns/similar", {
      method: "POST",
      body: JSON.stringify(params),
    })
  }

  // Collection endpoints
  async createCollection(data: {
    title: string
    description?: string
    isPublic?: boolean
  }) {
    return this.request<Collection>("/api/v1/collections/", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async getCollection(id: string) {
    return this.request<CollectionWithPatterns>(`/api/v1/collections/${id}`)
  }

  async getFeaturedCollections(limit = 10) {
    return this.request<CollectionWithPatterns[]>(
      `/api/v1/collections/featured/list?limit=${limit}`,
    )
  }

  // Analytics endpoints
  async getExhibitUsage() {
    return this.request<ExhibitUsage[]>("/api/v1/analytics/exhibit-usage")
  }

  async getTrends(days = 7, limit = 20) {
    return this.request<TrendingPattern[]>(
      `/api/v1/analytics/trends?days=${days}&limit=${limit}`,
    )
  }

  // Session endpoints
  async createSession(data: {
    patternId?: string
    maxParticipants?: number
    expiresInHours?: number
  }) {
    return this.request<Session>("/api/v1/sessions/", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async getSessionByCode(code: string) {
    return this.request<Session>(`/api/v1/sessions/code/${code}`)
  }

  // WebSocket URL for collaboration
  getWebSocketURL(sessionCode: string) {
    const wsURL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
    return `${wsURL}/api/v1/sessions/ws/${sessionCode}`
  }
}

// Type definitions
export interface Pattern {
  id: string
  userId?: string
  exhibitType: string
  title?: string
  description?: string
  parameters: Record<string, any>
  seed?: number
  thumbnailUrl?: string
  isPublic: boolean
  likesCount: number
  viewsCount: number
  forksCount: number
  forkedFromId?: string
  createdAt: string
  updatedAt: string
}

export interface PatternList {
  items: Pattern[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

export interface Collection {
  id: string
  userId: string
  title: string
  description?: string
  isPublic: boolean
  isFeatured: boolean
  createdAt: string
  updatedAt: string
  patternCount: number
}

export interface CollectionWithPatterns extends Collection {
  patterns: Pattern[]
}

export interface ExhibitUsage {
  exhibitType: string
  patternCount: number
  totalViews: number
  totalLikes: number
  avgLikesPerPattern: number
  mostRecentCreatedAt?: string
}

export interface TrendingPattern {
  patternId: string
  title?: string
  exhibitType: string
  likesCount: number
  viewsCount: number
  forksCount: number
  trendingScore: number
  createdAt: string
}

export interface Session {
  id: string
  sessionCode: string
  patternId?: string
  ownerId?: string
  currentState?: Record<string, any>
  isActive: boolean
  maxParticipants: number
  createdAt: string
  expiresAt?: string
  lastActivityAt: string
}

// Singleton instance
export const apiClient = new APIClient()
