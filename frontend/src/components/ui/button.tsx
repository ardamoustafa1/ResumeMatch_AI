import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cn } from "@/lib/utils"

type Variant = "default" | "secondary" | "ghost" | "outline" | "danger"
type Size = "default" | "sm" | "lg" | "icon"

const variants: Record<Variant, string> = {
  default: "bg-blue-600 text-white shadow-lg shadow-blue-950/30 hover:bg-blue-500",
  secondary: "bg-zinc-800 text-zinc-100 hover:bg-zinc-700",
  ghost: "bg-transparent text-zinc-300 hover:bg-zinc-800 hover:text-white",
  outline: "border border-zinc-700 bg-transparent text-zinc-200 hover:border-zinc-500 hover:bg-zinc-900",
  danger: "bg-red-600 text-white hover:bg-red-500",
}

const sizes: Record<Size, string> = {
  default: "min-h-10 px-4 py-2 text-sm",
  sm: "min-h-8 rounded-md px-3 text-xs",
  lg: "min-h-12 rounded-full px-8 text-base",
  icon: "h-10 w-10",
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  asChild?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 disabled:cursor-not-allowed disabled:opacity-50",
          "rounded-lg", // Default rounding, size 'lg' overrides with 'rounded-full'
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"
