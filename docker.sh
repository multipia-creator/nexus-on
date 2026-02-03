#!/bin/bash
# Docker Compose Quick Start Scripts

# Development mode (with hot reload)
dev() {
    echo "🚀 Starting NEXUS in Development mode..."
    docker-compose -f docker-compose.dev.yml up --build
}

# Build all services
build() {
    echo "🔨 Building all Docker images..."
    docker-compose build --no-cache
}

# Production mode (detached)
serve() {
    echo "🌐 Starting NEXUS in Production mode..."
    docker-compose -f docker-compose.prod.yml up -d
    echo "✅ Services started!"
    echo "   Frontend: http://localhost:80"
    echo "   Backend:  http://localhost:8000 (internal)"
}

# Stop all services
stop() {
    echo "🛑 Stopping all services..."
    docker-compose -f docker-compose.dev.yml down
    docker-compose -f docker-compose.prod.yml down
    docker-compose down
}

# Show logs
logs() {
    docker-compose logs -f
}

# Health check
health() {
    echo "🏥 Checking service health..."
    echo "Backend: $(curl -s http://localhost:8000/health | jq -r .status 2>/dev/null || echo 'Not running')"
    echo "Frontend: $(curl -s http://localhost:8080/health 2>/dev/null || echo 'Not running')"
}

# Show usage
usage() {
    echo "NEXUS Docker Compose Commands:"
    echo "  ./docker.sh dev     - Start in development mode (hot reload)"
    echo "  ./docker.sh build   - Build all Docker images"
    echo "  ./docker.sh serve   - Start in production mode (detached)"
    echo "  ./docker.sh stop    - Stop all services"
    echo "  ./docker.sh logs    - Show logs"
    echo "  ./docker.sh health  - Check service health"
}

# Main
case "$1" in
    dev)
        dev
        ;;
    build)
        build
        ;;
    serve)
        serve
        ;;
    stop)
        stop
        ;;
    logs)
        logs
        ;;
    health)
        health
        ;;
    *)
        usage
        ;;
esac
