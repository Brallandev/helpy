#!/bin/bash
set -e

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Wait for dependencies if needed
if [ "$WAIT_FOR_DEPS" = "true" ]; then
    log "Waiting for dependencies..."
    
    # Wait for Redis if configured
    if [ -n "$REDIS_URL" ]; then
        log "Waiting for Redis..."
        until redis-cli -u "$REDIS_URL" ping; do
            log "Redis is unavailable - sleeping"
            sleep 1
        done
        log "Redis is up!"
    fi
fi

# Validate required environment variables
log "Validating environment variables..."
required_vars=("WHATSAPP_TOKEN" "PHONE_NUMBER_ID" "VERIFY_TOKEN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log "ERROR: Required environment variable $var is not set"
        exit 1
    fi
done
log "Environment validation passed!"

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Set default values
export PORT="${PORT:-8000}"
export GRAPH_API_VERSION="${GRAPH_API_VERSION:-v20.0}"

log "Starting WhatsApp Mental Health Triage Bot..."
log "Port: $PORT"
log "Graph API Version: $GRAPH_API_VERSION"

# Execute the main command
exec "$@"
