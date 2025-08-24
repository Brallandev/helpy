#!/bin/bash

# Auto Triage Frontend - Docker Build Script
# This script builds and optionally runs the Next.js frontend in Docker

set -e

# Configuration
IMAGE_NAME="auto-triage-frontend"
CONTAINER_NAME="auto-triage-frontend"
PORT="3000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Build the Docker image
build_image() {
    log_info "Building Docker image: $IMAGE_NAME"
    
    if docker build -t $IMAGE_NAME .; then
        log_success "Docker image built successfully!"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

# Stop and remove existing container
cleanup_container() {
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Stopping existing container: $CONTAINER_NAME"
        docker stop $CONTAINER_NAME
    fi
    
    if docker ps -aq -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Removing existing container: $CONTAINER_NAME"
        docker rm $CONTAINER_NAME
    fi
}

# Run the container
run_container() {
    log_info "Starting container: $CONTAINER_NAME on port $PORT"
    
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:3000 \
        --restart unless-stopped \
        $IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        log_success "Container started successfully!"
        log_info "Frontend is available at: http://localhost:$PORT"
        log_info "Health check: http://localhost:$PORT/api/health"
    else
        log_error "Failed to start container"
        exit 1
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --build-only    Build the Docker image only (don't run)"
    echo "  --run-only      Run the existing image (don't build)"
    echo "  --cleanup       Stop and remove the container"
    echo "  --logs          Show container logs"
    echo "  --help          Show this help message"
    echo ""
    echo "Default: Build and run the container"
}

# Show logs
show_logs() {
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Showing logs for container: $CONTAINER_NAME"
        docker logs -f $CONTAINER_NAME
    else
        log_error "Container $CONTAINER_NAME is not running"
        exit 1
    fi
}

# Main script logic
main() {
    case "${1:-}" in
        --build-only)
            check_docker
            build_image
            ;;
        --run-only)
            check_docker
            cleanup_container
            run_container
            ;;
        --cleanup)
            check_docker
            cleanup_container
            log_success "Container cleanup completed"
            ;;
        --logs)
            show_logs
            ;;
        --help)
            show_usage
            ;;
        "")
            # Default: build and run
            check_docker
            build_image
            cleanup_container
            run_container
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run the script
main "$@"
