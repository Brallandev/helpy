# Docker Setup Verification Script for Windows
Write-Host "🐳 WhatsApp Mental Health Triage Bot - Docker Verification" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$allChecksPass = $true

# Check Docker installation
Write-Host "1. Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "   ✅ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker is not installed or not in PATH" -ForegroundColor Red
    $allChecksPass = $false
}

# Check Docker Compose
Write-Host "2. Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "   ✅ Docker Compose is installed: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker Compose is not installed" -ForegroundColor Red
    $allChecksPass = $false
}

# Check if Docker daemon is running
Write-Host "3. Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "   ✅ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker daemon is not running. Please start Docker Desktop." -ForegroundColor Red
    $allChecksPass = $false
}

# Check for required files
Write-Host "4. Checking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "Dockerfile",
    "docker-compose.yml", 
    "docker-compose.dev.yml",
    ".dockerignore",
    "docker-entrypoint.sh",
    "requirements.txt",
    "env.example"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file is missing" -ForegroundColor Red
        $allChecksPass = $false
    }
}

# Check .env file
Write-Host "5. Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ .env file exists" -ForegroundColor Green
    
    # Check required environment variables
    $requiredVars = @("WHATSAPP_TOKEN", "PHONE_NUMBER_ID", "VERIFY_TOKEN")
    $envContent = Get-Content ".env"
    
    foreach ($var in $requiredVars) {
        $varLine = $envContent | Where-Object { $_ -match "^$var=" }
        if ($varLine -and !($varLine -match "^$var=$")) {
            Write-Host "   ✅ $var is configured" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  $var needs to be configured in .env" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   ⚠️  .env file not found. Copy env.example to .env and configure your credentials." -ForegroundColor Yellow
    Write-Host "      Copy-Item env.example .env" -ForegroundColor White
}

# Test Docker build (if daemon is running)
Write-Host "6. Testing Docker build..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "   🔄 Building Docker image (this may take a few minutes)..." -ForegroundColor Blue
    
    $buildResult = docker build -t whatsapp-bot-test . 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Docker build successful" -ForegroundColor Green
        # Clean up test image
        docker rmi whatsapp-bot-test | Out-Null
    } else {
        Write-Host "   ❌ Docker build failed. Check Dockerfile and dependencies." -ForegroundColor Red
        $allChecksPass = $false
    }
} catch {
    Write-Host "   ⚠️  Skipping build test - Docker daemon not available" -ForegroundColor Yellow
}

# Final verdict
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
if ($allChecksPass) {
    Write-Host "🎉 All checks passed! Your Docker setup is ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Quick start commands:" -ForegroundColor Cyan
    Write-Host "   Development: docker-compose -f docker-compose.dev.yml up --build" -ForegroundColor White
    Write-Host "   Production:  docker-compose up -d --build" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 See DOCKER.md for complete deployment guide." -ForegroundColor Blue
} else {
    Write-Host "❌ Some checks failed. Please fix the issues above before proceeding." -ForegroundColor Red
    exit 1
}
