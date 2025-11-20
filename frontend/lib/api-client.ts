export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";

export interface ApiOptions<TBody> {
  path: string;
  method?: HttpMethod;
  body?: TBody;
}

export interface ApiClientConfig {
  baseUrl?: string;
  offline?: boolean;
}

const defaultConfig: ApiClientConfig = { baseUrl: "http://localhost:8000/api/v1" };

export async function apiRequest<TResponse, TBody = unknown>(
  options: ApiOptions<TBody>,
  config: ApiClientConfig = defaultConfig,
): Promise<TResponse> {
  if (config.offline) {
    throw new Error("Offline mode: request queued for sync");
  }

  const res = await fetch(`${config.baseUrl}${options.path}`, {
    method: options.method ?? "GET",
    headers: { "Content-Type": "application/json" },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return (await res.json()) as TResponse;
}
