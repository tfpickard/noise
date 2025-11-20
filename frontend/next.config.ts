import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  experimental: {
    // Enable React 19 features
    reactCompiler: true,
    // Enable modern optimizations
    optimizePackageImports: ["framer-motion"],
  },
  // Modern image optimization
  images: {
    formats: ["image/avif", "image/webp"],
  },
  // TypeScript
  typescript: {
    ignoreBuildErrors: false,
  },
  // ESLint (using Biome instead)
  eslint: {
    ignoreDuringBuilds: true,
  },
}

export default nextConfig
