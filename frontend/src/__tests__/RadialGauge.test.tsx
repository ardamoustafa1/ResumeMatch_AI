import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { RadialGauge } from "../components/dashboard/RadialGauge"

describe("RadialGauge", () => {
  it("renders the score correctly", () => {
    render(<RadialGauge score={85} />)
    expect(screen.getByText("85%")).toBeInTheDocument()
  })
})
