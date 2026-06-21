import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cn } from "@/lib/utils"

type Variant = "default" | "secondary" | "ghost" | "outline" | "danger"
type Size = "default" | "sm" | "lg" | "icon"

const variants: Record<Variant, string> = {
  default: "border border-white/10 bg-[#6c7cff] text-white shadow-[0_10px_30px_rgba(76,91,220,.28),inset_0_1px_0_rgba(255,255,255,.22)] hover:bg-[#7b89ff] hover:shadow-[0_14px_36px_rgba(76,91,220,.36)]",
  secondary: "border border-white/[0.08] bg-white/[0.055] text-zinc-100 hover:bg-white/[0.09]",
  ghost: "bg-transparent text-zinc-400 hover:bg-white/[0.06] hover:text-white",
  outline: "border border-white/[0.12] bg-black/10 text-zinc-200 hover:border-white/20 hover:bg-white/[0.055]",
  danger: "border border-red-400/20 bg-red-500/90 text-white hover:bg-red-500",
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
          "inline-flex items-center justify-center gap-2 font-semibold tracking-[-0.01em] transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#8f9aff] focus-visible:ring-offset-2 focus-visible:ring-offset-[#080a0f] disabled:cursor-not-allowed disabled:opacity-50",
          "rounded-xl",
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
