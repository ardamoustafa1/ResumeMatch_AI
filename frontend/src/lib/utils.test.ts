import { describe, expect, it } from "vitest"

import { cn } from "./utils"

describe("cn", () => {
  it("joins truthy class names", () => {
    expect(cn("base", false, undefined, "active")).toBe("base active")
  })
})
