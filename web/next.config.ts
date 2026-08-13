import type { NextConfig } from "next";

const nextConfig: NextConfig = {};

if (process.env.ACREOPS_STATIC_EXPORT === "1") {
  nextConfig.output = "export";
  nextConfig.images = { unoptimized: true };
  nextConfig.trailingSlash = true;
  const basePath = process.env.ACREOPS_BASE_PATH;
  if (basePath) {
    nextConfig.basePath = basePath;
    nextConfig.assetPrefix = basePath;
  }
} else if (!process.env.VERCEL && !process.env.NETLIFY) {
  nextConfig.output = "standalone";
}

export default nextConfig;
