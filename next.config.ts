import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Multipart route uploads pass through Vinext's server-action parser first.
  experimental: { serverActions: { bodySizeLimit: '9mb' } },
};

export default nextConfig;
