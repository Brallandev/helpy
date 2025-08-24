import path from 'path';

/** @type {import('next').NextConfig} */
const nextConfig = {
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
    // Cross-platform webpack configuration
    config.resolve = config.resolve || {};
    
    // Platform-specific optimizations
    if (process.platform === 'win32') {
      // Windows-specific: Disable symlinks to prevent case sensitivity issues with pnpm
      config.resolve.symlinks = false;
      // Disable cache with context to avoid path casing conflicts
      config.resolve.cacheWithContext = false;
      // Configure main fields for Windows
      config.resolve.mainFields = ['browser', 'module', 'main'];
      config.resolve.aliasFields = ['browser'];
    } else {
      // Linux/macOS: Enable symlinks for proper package resolution
      config.resolve.symlinks = true;
      // Enable cache with context for better performance
      config.resolve.cacheWithContext = true;
    }
    
    // Common configuration for all platforms
    config.resolve.enforceExtension = false;
    
    // Ensure path aliases work correctly on all platforms
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, '.'),
    };
    
    return config;
  },
}

export default nextConfig
