import type { NextConfig } from "next";

const nextConfig: NextConfig = {};

if (!process.env.VERCEL) {
  nextConfig.output = "standalone";
}

export default nextConfig;
