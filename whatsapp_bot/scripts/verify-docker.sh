#!/bin/bash

# Docker Setup Verification Script
echo "🐳 WhatsApp Mental Health Triage Bot - Docker Verification"
echo "========================================================"

# Check Docker installation
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker is installed: $(docker --version)"
else
    echo "   ❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check Docker Compose
echo "2. Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo "   ✅ Docker Compose is installed: $(docker-compose --version)"
else
    echo "   ❌ Docker Compose is not installed"
    exit 1
fi

# Check if Docker daemon is running
echo "3. Checking Docker daemon..."
if docker info &> /dev/null; then
    echo "   ✅ Docker daemon is running"
else
    echo "   ❌ Docker daemon is not running. Please start Docker Desktop or Docker service."
    exit 1
fi

# Check for required files
echo "4. Checking required files..."
required_files=(
    "Dockerfile"
    "docker-compose.yml" 
    "docker-compose.dev.yml"
    ".dockerignore"
    "docker-entrypoint.sh"
    "requirements.txt"
    "env.example"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file is missing"
        all_files_exist=false
    fi
done

# Check .env file
echo "5. Checking environment configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
    
    # Check required environment variables
    required_vars=("WHATSAPP_TOKEN" "PHONE_NUMBER_ID" "VERIFY_TOKEN")
    for var in "${required_vars[@]}"; do
        if grep -q "^$var=" .env && ! grep -q "^$var=$" .env; then
            echo "   ✅ $var is configured"
        else
            echo "   ⚠️  $var needs to be configured in .env"
        fi
    done
else
    echo "   ⚠️  .env file not found. Copy env.example to .env and configure your credentials."
    echo "      cp env.example .env"
fi

# Test Docker build (if daemon is running)
echo "6. Testing Docker build..."
if docker info &> /dev/null; then
    echo "   🔄 Building Docker image (this may take a few minutes)..."
    if docker build -t whatsapp-bot-test . &> /dev/null; then
        echo "   ✅ Docker build successful"
        # Clean up test image
        docker rmi whatsapp-bot-test &> /dev/null
    else
        echo "   ❌ Docker build failed. Check Dockerfile and dependencies."
        all_files_exist=false
    fi
fi

# Final verdict
echo ""
echo "========================================================"
if [ "$all_files_exist" = true ] && docker info &> /dev/null; then
    echo "🎉 All checks passed! Your Docker setup is ready."
    echo ""
    echo "🚀 Quick start commands:"
    echo "   Development: docker-compose -f docker-compose.dev.yml up --build"
    echo "   Production:  docker-compose up -d --build"
    echo ""
    echo "📖 See DOCKER.md for complete deployment guide."
else
    echo "❌ Some checks failed. Please fix the issues above before proceeding."
    exit 1
fi
