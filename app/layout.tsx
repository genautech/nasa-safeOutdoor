import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import { Suspense } from "react"
import { BackendStatus } from "@/components/backend-status"

export const metadata: Metadata = {
  title: "SafeOutdoor - AI-Powered Outdoor Safety Advisor",
  description:
    "Plan your outdoor adventures with AI-powered safety analysis using NASA TEMPO satellite data, air quality monitoring, and weather forecasts.",
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
