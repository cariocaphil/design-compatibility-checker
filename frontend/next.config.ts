import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a minimal, self-contained server bundle for the container image.
  output: "standalone",
};

export default nextConfig;
