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
  const configured = process.env.NEXT_PUBLIC_WS_URL
  const baseUrl = configured 
    ? `${configured}/ws/analysis/${analysisId}`
    : `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.hostname}${process.env.NODE_ENV === "development" ? ":8000" : ""}/ws/analysis/${analysisId}`;
  return `${baseUrl}?ticket=${ticket}`
}
