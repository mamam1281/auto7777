#!/bin/bash

# Casino-Club F2P Docker Environment Management Script
# Simple Bash script for managing Docker containers and environment

# Default action
ACTION=${1:-help}

# Docker Compose files
COMPOSE_FILE="docker-compose.yml"
COMPOSE_DEV_FILE="docker-compose.override.yml"

# Color output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_color() {
    echo -e "${2}${1}${NC}"
}

show_help() {
    print_color "Casino-Club F2P Docker Environment Management" $CYAN
    print_color "=========================================" $CYAN
    echo ""
    print_color "Usage: ./docker-manage.sh <command> [service]" $YELLOW
    echo ""
    print_color "Commands:" $YELLOW
    echo "  start      - Start all containers"
    echo "  stop       - Stop all containers"
    echo "  restart    - Restart all containers"
    echo "  rebuild    - Rebuild services (specify service or all)"
    echo "  logs       - Show logs (specify service or all)"
    echo "  status     - Show container status"
    echo "  volumes    - List project volumes"
    echo "  reset      - Reset environment (removes volumes)"
    echo "  bash       - Open bash shell in container (requires service)"
    echo "  psql       - Connect to PostgreSQL container"
    echo "  redis-cli  - Connect to Redis container"
    echo "  help       - Show this help message"
    echo ""
    print_color "Examples:" $YELLOW
    echo "  ./docker-manage.sh start"
    echo "  ./docker-manage.sh logs backend"
    echo "  ./docker-manage.sh bash backend"
}

start_environment() {
    print_color "Starting Docker environment..." $GREEN
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE up -d
    
    if [ $? -eq 0 ]; then
        print_color "Environment started successfully!" $GREEN
        print_color "Frontend: http://localhost:3000" $CYAN
        print_color "Backend API: http://localhost:8000" $CYAN
        print_color "Swagger Docs: http://localhost:8000/docs" $CYAN
        print_color "PostgreSQL: localhost:5432" $CYAN
        print_color "Redis: localhost:6379" $CYAN
        docker-compose ps
    else
        print_color "Failed to start environment. Check logs for details." $RED
    fi
}

stop_environment() {
    print_color "Stopping Docker environment..." $YELLOW
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE down
    
    if [ $? -eq 0 ]; then
        print_color "Environment stopped successfully!" $GREEN
    else
        print_color "Failed to stop environment. Check logs for details." $RED
    fi
}

restart_environment() {
    print_color "Restarting Docker environment..." $YELLOW
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE restart
    
    if [ $? -eq 0 ]; then
        print_color "Environment restarted successfully!" $GREEN
        docker-compose ps
    else
        print_color "Failed to restart environment. Check logs for details." $RED
    fi
}

rebuild_environment() {
    print_color "Rebuilding Docker environment..." $YELLOW
    
    if [ -z "$2" ]; then
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE build
    else
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE build $2
    fi
    
    if [ $? -eq 0 ]; then
        print_color "Environment rebuilt successfully!" $GREEN
        print_color "Do you want to restart the containers now? (y/n)" $CYAN
        read -r restart
        
        if [ "$restart" = "y" ]; then
            restart_environment
        fi
    else
        print_color "Failed to rebuild environment. Check logs for details." $RED
    fi
}

show_logs() {
    if [ -z "$2" ]; then
        print_color "Showing logs for all services..." $CYAN
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE logs -f
    else
        print_color "Showing logs for $2..." $CYAN
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE logs -f $2
    fi
}

show_status() {
    print_color "Checking Docker container status..." $CYAN
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE ps
}

connect_postgres() {
    print_color "Connecting to PostgreSQL..." $CYAN
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE exec postgres psql -U cc_user -d cc_webapp
}

connect_redis() {
    print_color "Connecting to Redis..." $CYAN
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE exec redis redis-cli
}

reset_environment() {
    print_color "WARNING: This will reset all data. Are you sure? (y/n)" $RED
    read -r confirm
    
    if [ "$confirm" = "y" ]; then
        print_color "Stopping and removing all containers..." $YELLOW
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE down -v
        
        print_color "Environment reset complete!" $GREEN
        print_color "Do you want to restart the environment? (y/n)" $CYAN
        read -r restart
        
        if [ "$restart" = "y" ]; then
            start_environment
        fi
    else
        print_color "Reset cancelled." $YELLOW
    fi
}

execute_bash() {
    if [ -z "$2" ]; then
        print_color "Please specify a service name" $RED
        return 1
    fi
    
    print_color "Connecting to $2 container shell..." $CYAN
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE exec $2 bash
}

# Main command processing
case $ACTION in
    start)
        start_environment
        ;;
    stop)
        stop_environment
        ;;
    restart)
        restart_environment
        ;;
    rebuild)
        rebuild_environment "$@"
        ;;
    logs)
        show_logs "$@"
        ;;
    status)
        show_status
        ;;
    psql)
        connect_postgres
        ;;
    redis-cli)
        connect_redis
        ;;
    reset)
        reset_environment
        ;;
    bash)
        execute_bash "$@"
        ;;
    help|*)
        show_help
        ;;
esac
