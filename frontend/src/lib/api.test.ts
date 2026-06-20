import { afterEach, describe, expect, it, vi } from "vitest"

import { ApiError, apiFetch } from "./api"

describe("apiFetch", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("returns parsed JSON for successful requests", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ status: "ok" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    )

    await expect(apiFetch<{ status: string }>("/health")).resolves.toEqual({
      status: "ok",
    })
  })

  it("throws a typed error for failed requests", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "No access" }), {
          status: 403,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    )

    await expect(apiFetch("/private", {}, false)).rejects.toEqual(
      new ApiError("No access", 403),
    )
  })
})
