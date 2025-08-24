/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  webpack: (config, { dev, isServer }) => {
    // Fix case sensitivity issues on Windows by configuring webpack resolution
    config.resolve = config.resolve || {};
    
    // Disable symlinks to prevent case sensitivity issues with pnpm
    config.resolve.symlinks = false;
    
    // Disable cache with context to avoid path casing conflicts
    config.resolve.cacheWithContext = false;
    
    // Configure case sensitivity for modules
    config.resolve.enforceExtension = false;
    
    // Additional optimization for Windows case sensitivity
    if (process.platform === 'win32') {
      config.resolve.mainFields = ['browser', 'module', 'main'];
      config.resolve.aliasFields = ['browser'];
    }
    
    return config;
  },
}

export default nextConfig
