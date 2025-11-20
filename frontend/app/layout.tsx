import type { Metadata, Viewport } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
})

export const metadata: Metadata = {
  title: "Visual Noise Museum",
  description:
    "Explore the art of procedural noise generation with bleeding-edge web technologies",
  keywords: [
    "noise",
    "procedural generation",
    "webgpu",
    "canvas",
    "generative art",
    "perlin noise",
  ],
  authors: [{ name: "Visual Noise Museum" }],
}

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f5f5f5" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0a" },
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased bg-noise-dark text-noise-light">
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
