"use client"

import { Toaster as Sonner } from "sonner"

export function Toaster() {
  return (
    <Sonner
      theme="dark"
      richColors
      closeButton
      position="top-right"
      toastOptions={{
        style: {
          background: "#18181b",
          border: "1px solid #3f3f46",
          color: "#fafafa",
        },
      }}
    />
  )
}
