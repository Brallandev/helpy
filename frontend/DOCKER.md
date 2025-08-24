# Auto Triage Frontend - Docker Deployment Guide

This guide explains how to build and deploy the Next.js frontend using Docker for production environments.

## 🐳 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+ (optional)

### Build and Run (Automated)
```bash
# Build and run the container
./build.sh

# Or build only
./build.sh --build-only

# Or run existing image
./build.sh --run-only
```

### Manual Build and Run
```bash
# Build the Docker image
docker build -t auto-triage-frontend .

# Run the container
docker run -d \
  --name auto-triage-frontend \
  -p 3000:3000 \
  --restart unless-stopped \
  auto-triage-frontend
```

### Using Docker Compose
```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## 📋 Configuration

### Environment Variables

The frontend supports the following environment variables:

```env
# Production settings
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1

# API Configuration (customize as needed)
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_WHATSAPP_BOT_URL=http://localhost:8001

# Optional: Analytics and monitoring
NEXT_PUBLIC_GA_ID=your_google_analytics_id
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
```

### Docker Environment Variables

You can pass environment variables to the container:

```bash
docker run -d \
  --name auto-triage-frontend \
  -p 3000:3000 \
  -e NODE_ENV=production \
  -e NEXT_PUBLIC_API_URL=https://your-api-domain.com/api \
  --restart unless-stopped \
  auto-triage-frontend
```

## 🏗️ Multi-Stage Build Details

The Dockerfile uses a multi-stage build process for optimization:

### Stage 1: Dependencies (`deps`)
- Based on `node:20-alpine`
- Installs only production dependencies
- Supports both npm and pnpm package managers

### Stage 2: Builder (`builder`)
- Copies dependencies from the deps stage
- Builds the Next.js application with optimizations
- Creates standalone output for minimal runtime

### Stage 3: Runner (`runner`)
- Minimal production runtime image
- Non-root user for security
- Only includes built application and necessary files
- ~90% smaller than development image

## 📊 Image Size Optimization

The production image is highly optimized:

```
REPOSITORY              TAG       SIZE
auto-triage-frontend   latest    ~150MB
```

Optimization techniques used:
- Multi-stage build
- Alpine Linux base image
- Standalone Next.js output
- Minimal runtime dependencies
- Non-root user execution
- Optimized layer caching

## 🔍 Health Checks

The container includes built-in health checks:

```bash
# Check container health
docker ps

# Manual health check
curl http://localhost:3000/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "auto-triage-frontend",
  "version": "1.0.0"
}
```

## 🛠️ Development vs Production

### Development
```bash
# Local development
npm run dev
# or
pnpm dev
```

### Production (Docker)
```bash
# Build and run production container
./build.sh
```

### Key Differences
- **Development**: Hot reloading, source maps, verbose logging
- **Production**: Optimized bundles, minimal runtime, security hardening

## 📝 Container Management

### Useful Commands

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# View container logs
docker logs auto-triage-frontend

# Follow logs in real-time
docker logs -f auto-triage-frontend

# Execute commands in container
docker exec -it auto-triage-frontend sh

# Stop container
docker stop auto-triage-frontend

# Remove container
docker rm auto-triage-frontend

# Remove image
docker rmi auto-triage-frontend
```

### Cleanup Script Commands

```bash
# Stop and remove container
./build.sh --cleanup

# View container logs
./build.sh --logs

# Show help
./build.sh --help
```

## 🔒 Security Considerations

### Container Security
- ✅ Non-root user execution (`nextjs:nodejs`)
- ✅ Minimal attack surface (Alpine Linux)
- ✅ No unnecessary packages in production
- ✅ Read-only filesystem where possible
- ✅ Health checks for monitoring

### Network Security
```bash
# Run with custom network
docker network create auto-triage-network
docker run -d \
  --name auto-triage-frontend \
  --network auto-triage-network \
  -p 3000:3000 \
  auto-triage-frontend
```

## 🚀 Production Deployment

### Single Container
```bash
# Production deployment
docker run -d \
  --name auto-triage-frontend \
  -p 80:3000 \
  -e NODE_ENV=production \
  -e NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  --restart unless-stopped \
  auto-triage-frontend
```

### With Load Balancer (nginx)
```bash
# Run multiple instances
docker run -d --name frontend-1 -p 3001:3000 auto-triage-frontend
docker run -d --name frontend-2 -p 3002:3000 auto-triage-frontend
docker run -d --name frontend-3 -p 3003:3000 auto-triage-frontend
```

### Docker Compose Production
```yaml
version: '3.8'
services:
  frontend:
    image: auto-triage-frontend:latest
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
    ports:
      - "3000-3002:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## 🐛 Troubleshooting

### Common Issues

**Build fails with memory issues:**
```bash
# Increase Docker memory limit or build with:
docker build --memory=4g -t auto-triage-frontend .
```

**Container won't start:**
```bash
# Check logs
docker logs auto-triage-frontend

# Check if port is available
netstat -tulpn | grep :3000
```

**Health check fails:**
```bash
# Test health endpoint manually
curl -f http://localhost:3000/api/health

# Check container network
docker exec -it auto-triage-frontend wget -qO- http://localhost:3000/api/health
```

**Permission issues:**
```bash
# Ensure proper file permissions
docker exec -it auto-triage-frontend ls -la

# Check if running as non-root
docker exec -it auto-triage-frontend whoami
```

### Performance Tuning

**Memory optimization:**
```bash
# Limit container memory
docker run -d \
  --name auto-triage-frontend \
  --memory=512m \
  --memory-swap=1g \
  -p 3000:3000 \
  auto-triage-frontend
```

**CPU optimization:**
```bash
# Limit CPU usage
docker run -d \
  --name auto-triage-frontend \
  --cpus="1.5" \
  -p 3000:3000 \
  auto-triage-frontend
```

## 📚 Additional Resources

- [Next.js Docker Documentation](https://nextjs.org/docs/deployment#docker-image)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Node.js Docker Best Practices](https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md)

---

**Note**: This Docker setup is optimized for production use with security, performance, and maintainability in mind.
