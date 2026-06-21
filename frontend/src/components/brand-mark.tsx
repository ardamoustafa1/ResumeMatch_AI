import { Sparkles } from "lucide-react"

import { cn } from "@/lib/utils"

export function BrandMark({
  compact = false,
  className,
}: {
  compact?: boolean
  className?: string
}) {
  return (
    <div className={cn("inline-flex items-center gap-3", className)}>
      <span className="brand-symbol" aria-hidden="true">
        <Sparkles className="size-[52%]" strokeWidth={2.2} />
      </span>
      {!compact && (
        <span className="text-[15px] font-semibold tracking-[-0.02em] text-white">
          NetworkForge
        </span>
      )}
    </div>
  )
}
