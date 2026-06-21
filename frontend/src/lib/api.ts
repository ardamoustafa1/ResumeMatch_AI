const API_PREFIX = "/api/v1"

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

async function parseError(response: Response): Promise<string> {
  try {
    const data = await response.json()
    if (typeof data.detail === "string") return data.detail
    if (data.detail?.error) return data.detail.error
    if (data.error) return data.error
  } catch {
    // Use the generic status message below.
  }
  return response.statusText || "Request failed"
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  retry = true,
): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...(!(init.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...init.headers,
    },
  })

  if (response.status === 401 && retry && path !== "/auth/refresh") {
    const refreshed = await fetch(`${API_PREFIX}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    })
    if (refreshed.ok) return apiFetch<T>(path, init, false)
  }

  if (!response.ok) {
    throw new ApiError(await parseError(response), response.status)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export function websocketUrl(analysisId: string, ticket: string): string {
  let baseUrl = '';
  if (typeof window !== "undefined") {
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      baseUrl = `ws://${window.location.hostname}:8000/api/v1/ws/analysis/${analysisId}`;
    } else {
      baseUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/api/v1/ws/analysis/${analysisId}`;
    }
  } else {
    baseUrl = `ws://localhost:8000/api/v1/ws/analysis/${analysisId}`;
  }
  return `${baseUrl}?ticket=${ticket}`;
}
