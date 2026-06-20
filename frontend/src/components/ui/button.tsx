import * as React from "react"

import { cn } from "@/lib/utils"

type Variant = "default" | "secondary" | "ghost" | "outline" | "danger"

const variants: Record<Variant, string> = {
  default:
    "bg-blue-600 text-white shadow-lg shadow-blue-950/30 hover:bg-blue-500",
  secondary: "bg-zinc-800 text-zinc-100 hover:bg-zinc-700",
  ghost: "bg-transparent text-zinc-300 hover:bg-zinc-800 hover:text-white",
  outline:
    "border border-zinc-700 bg-transparent text-zinc-200 hover:border-zinc-500 hover:bg-zinc-900",
  danger: "bg-red-600 text-white hover:bg-red-500",
}

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
}

export function Button({
  className,
  variant = "default",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "inline-flex min-h-10 items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 disabled:cursor-not-allowed disabled:opacity-50",
        variants[variant],
        className,
      )}
      {...props}
    />
  )
}
