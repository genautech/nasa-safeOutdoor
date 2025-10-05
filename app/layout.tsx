import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import { Suspense } from "react"
import { BackendStatus } from "@/components/backend-status"

export const metadata: Metadata = {
  title: "Safe Outdoor v3.0 – NASA Space Apps 2025",
  description:
    "NASA-powered outdoor safety insights blending TEMPO, OMI, MERRA-2, and GPM data with wearable and calendar intelligence.",
  manifest: "/manifest.json",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable} antialiased`}>
        <Suspense fallback={null}>{children}</Suspense>
        <BackendStatus />
        <Analytics />
      </body>
    </html>
  )
}
