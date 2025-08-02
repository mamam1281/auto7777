# Casino-Club F2P - Enhanced Docker Development Environment Manager
# PowerShell Script for Windows Development

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [string]$Service = "",
    [switch]$Tools = $false,
    [switch]$VerboseOutput = $false
)

# Helper function for colored output
function Write-ColoredOutput {
    param([string]$Text, [string]$Color = "White")
    
    $ConsoleColor = switch ($Color) {
        "Red" { [System.ConsoleColor]::Red }
        "Green" { [System.ConsoleColor]::Green }
        "Yellow" { [System.ConsoleColor]::Yellow }
        "Blue" { [System.ConsoleColor]::Blue }
        "Cyan" { [System.ConsoleColor]::Cyan }
        "Magenta" { [System.ConsoleColor]::Magenta }
        default { [System.ConsoleColor]::White }
    }
    
    Write-Host $Text -ForegroundColor $ConsoleColor
}

# Header display
function Show-Header {
    Write-ColoredOutput "================================================================" "Cyan"
    Write-ColoredOutput " Casino-Club F2P - Docker Development Environment Manager" "Yellow"
    Write-ColoredOutput "================================================================" "Cyan"
    Write-ColoredOutput "Version: 2.0 | Environment: Development | Platform: Windows" "Blue"
    Write-ColoredOutput "" "White"
}

# Environment check
function Test-Environment {
    Write-ColoredOutput "[*] Checking development environment..." "Blue"
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-ColoredOutput "[+] Docker: $dockerVersion" "Green"
    } catch {
        Write-ColoredOutput "[!] Docker not found or not running" "Red"
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-ColoredOutput "[+] Docker Compose: $composeVersion" "Green"
    } catch {
        Write-ColoredOutput "[!] Docker Compose not found" "Red"
        exit 1
    }
    
    # Check required files
    $requiredFiles = @("docker-compose.yml", ".env.development")
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-ColoredOutput "[+] Found: $file" "Green"
        } else {
            Write-ColoredOutput "[!] Missing: $file" "Red"
        }
    }
    
    Write-ColoredOutput "[*] Environment check completed!" "Green"
    Write-ColoredOutput "" "White"
}

# Service health check
function Test-ServiceHealth {
    Write-ColoredOutput "🏥 Checking service health..." "Blue"
    
    $services = @(
        @{Name="Backend API"; URL="http://localhost:8000/docs"; Container="cc_backend_dev"},
        @{Name="Frontend"; URL="http://localhost:3000"; Container="cc_frontend_dev"},
        @{Name="PostgreSQL"; Container="cc_postgres_dev"},
        @{Name="Redis"; Container="cc_redis_dev"},
        @{Name="Kafka"; Container="cc_kafka_dev"}
    )
    
    foreach ($service in $services) {
        $status = docker ps --filter "name=$($service.Container)" --format "{{.Status}}"
        if ($status -like "*Up*") {
            Write-ColoredOutput "✅ $($service.Name): Running" "Green"
            if ($service.URL) {
                Write-ColoredOutput "   🌐 Access: $($service.URL)" "Cyan"
            }
        } else {
            Write-ColoredOutput "❌ $($service.Name): Not running" "Red"
        }
    }
    
    if ($Tools) {
        Write-ColoredOutput "" "White"
        Write-ColoredOutput "🛠️ Development tools:" "Yellow"
        Write-ColoredOutput "   📊 pgAdmin: http://localhost:5050" "Cyan"
        Write-ColoredOutput "   🔴 Redis Commander: http://localhost:8081" "Cyan"
        Write-ColoredOutput "   📨 Kafka UI: http://localhost:8082" "Cyan"
    }
}

# Setup development environment
function Initialize-Environment {
    Write-ColoredOutput "🚀 Setting up development environment..." "Yellow"
    
    # Create required directories
    $directories = @("logs/backend", "logs/frontend", "logs/postgres", "logs/celery", "logs/nginx", "data/init", "data/backup")
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-ColoredOutput "📁 Created directory: $dir" "Blue"
        }
    }
    
    # Copy environment file if needed
    if (!(Test-Path ".env")) {
        if (Test-Path ".env.development") {
            Copy-Item ".env.development" ".env"
            Write-ColoredOutput "📋 Copied .env.development to .env" "Blue"
        }
    }
    
    # Build images
    Write-ColoredOutput "🔨 Building Docker images..." "Yellow"
    docker-compose build --no-cache
    
    Write-ColoredOutput "✅ Environment setup completed!" "Green"
}

# Start services
function Start-Services {
    param([string]$Profile = "")
    
    Write-ColoredOutput "🚀 Starting Casino-Club services..." "Yellow"
    
    $composeCmd = "docker-compose --env-file .env.development up -d"
    if ($Profile) {
        $composeCmd += " --profile $Profile"
    }
    
    Invoke-Expression $composeCmd
    
    Write-ColoredOutput "⏳ Waiting for services to start..." "Blue"
    Start-Sleep -Seconds 10
    
    Test-ServiceHealth
}

# Stop services
function Stop-Services {
    Write-ColoredOutput "🛑 Stopping Casino-Club services..." "Yellow"
    docker-compose down
    Write-ColoredOutput "✅ Services stopped" "Green"
}

# Restart services
function Restart-Services {
    param([string]$ServiceName = "")
    
    if ($ServiceName) {
        Write-ColoredOutput "🔄 Restarting service: $ServiceName..." "Yellow"
        docker-compose restart $ServiceName
    } else {
        Write-ColoredOutput "🔄 Restarting all services..." "Yellow"
        Stop-Services
        Start-Sleep -Seconds 5
        Start-Services
    }
    
    Write-ColoredOutput "✅ Restart completed" "Green"
}

# View logs
function Show-Logs {
    param([string]$ServiceName = "", [int]$Lines = 100)
    
    if ($ServiceName) {
        Write-ColoredOutput "📋 Showing logs for: $ServiceName" "Blue"
        docker-compose logs --tail=$Lines -f $ServiceName
    } else {
        Write-ColoredOutput "📋 Showing logs for all services" "Blue"
        docker-compose logs --tail=$Lines -f
    }
}

# Execute shell in container
function Enter-Shell {
    param([string]$ServiceName = "backend")
    
    Write-ColoredOutput "🐚 Entering shell for: $ServiceName" "Blue"
    
    $containerName = switch ($ServiceName) {
        "backend" { "cc_backend_dev" }
        "frontend" { "cc_frontend_dev" }
        "postgres" { "cc_postgres_dev" }
        "redis" { "cc_redis_dev" }
        default { "cc_${ServiceName}_dev" }
    }
    
    docker exec -it $containerName /bin/bash
}

# Run tests
function Invoke-Tests {
    param([string]$TestType = "all")
    
    Write-ColoredOutput "🧪 Running tests: $TestType" "Yellow"
    
    switch ($TestType) {
        "backend" {
            docker-compose exec backend python -m pytest tests/ -v --tb=short
        }
        "frontend" {
            docker-compose exec frontend npm run test
        }
        "coverage" {
            docker-compose exec backend python -m pytest tests/ --cov=app --cov-report=html --cov-report=term
        }
        default {
            Write-ColoredOutput "🔄 Running backend tests..." "Blue"
            docker-compose exec backend python -m pytest tests/ -v
            Write-ColoredOutput "🔄 Running frontend tests..." "Blue"
            docker-compose exec frontend npm run test:ci
        }
    }
    
    Write-ColoredOutput "✅ Tests completed" "Green"
}

# Database operations
function Invoke-DatabaseOperation {
    param([string]$Operation)
    
    switch ($Operation) {
        "migrate" {
            Write-ColoredOutput "🗄️ Running database migrations..." "Yellow"
            docker-compose exec backend alembic upgrade head
        }
        "seed" {
            Write-ColoredOutput "🌱 Seeding database..." "Yellow"
            docker-compose exec backend python scripts/seed_data.py
        }
        "reset" {
            Write-ColoredOutput "🔄 Resetting database..." "Yellow"
            docker-compose exec backend alembic downgrade base
            docker-compose exec backend alembic upgrade head
        }
        "backup" {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $backupFile = "data/backup/backup_$timestamp.sql"
            Write-ColoredOutput "💾 Creating database backup: $backupFile" "Yellow"
            docker-compose exec postgres pg_dump -U cc_user cc_webapp > $backupFile
        }
    }
}

# Clean up resources
function Invoke-Cleanup {
    param([string]$Type = "containers")
    
    Write-ColoredOutput "🧹 Cleaning up Docker resources..." "Yellow"
    
    switch ($Type) {
        "containers" {
            docker container prune -f
        }
        "images" {
            docker image prune -f
        }
        "volumes" {
            Write-ColoredOutput "⚠️ This will delete all data volumes. Continue? (y/N)" "Red"
            $confirm = Read-Host
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                docker-compose down -v
                docker volume prune -f
            }
        }
        "all" {
            docker system prune -af
        }
    }
    
    Write-ColoredOutput "✅ Cleanup completed" "Green"
}

# Performance monitoring
function Show-Performance {
    Write-ColoredOutput "📊 Performance monitoring..." "Blue"
    
    Write-ColoredOutput "🖥️ System resources:" "Yellow"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
    Write-ColoredOutput "💾 Disk usage:" "Yellow"
    docker system df
}

# Show help
function Show-Help {
    Show-Header
    Write-ColoredOutput "📚 Available Commands:" "Yellow"
    Write-ColoredOutput "" "White"
    
    $commands = @(
        @{Cmd="help"; Desc="Show this help message"},
        @{Cmd="check"; Desc="Check development environment"},
        @{Cmd="setup"; Desc="Initialize development environment"},
        @{Cmd="start [--tools]"; Desc="Start all services (add --tools for dev tools)"},
        @{Cmd="stop"; Desc="Stop all services"},
        @{Cmd="restart [service]"; Desc="Restart services (all or specific)"},
        @{Cmd="status"; Desc="Show service health status"},
        @{Cmd="logs [service]"; Desc="Show logs (all or specific service)"},
        @{Cmd="shell [service]"; Desc="Enter shell for service (default: backend)"},
        @{Cmd="test [type]"; Desc="Run tests (all/backend/frontend/coverage)"},
        @{Cmd="migrate"; Desc="Run database migrations"},
        @{Cmd="seed"; Desc="Seed database with test data"},
        @{Cmd="backup"; Desc="Create database backup"},
        @{Cmd="reset-db"; Desc="Reset database"},
        @{Cmd="clean [type]"; Desc="Clean Docker resources (containers/images/volumes/all)"},
        @{Cmd="monitor"; Desc="Show performance monitoring"},
        @{Cmd="build"; Desc="Rebuild Docker images"}
    )
    
    foreach ($cmd in $commands) {
        Write-Host ("  {0,-20} {1}" -f $cmd.Cmd, $cmd.Desc) -ForegroundColor White
    }
    
    Write-ColoredOutput "" "White"
    Write-ColoredOutput "💡 Examples:" "Yellow"
    Write-ColoredOutput "  .\docker-manage.ps1 start --tools     # Start with development tools" "Cyan"
    Write-ColoredOutput "  .\docker-manage.ps1 logs backend      # Show backend logs" "Cyan"
    Write-ColoredOutput "  .\docker-manage.ps1 shell frontend    # Enter frontend container" "Cyan"
    Write-ColoredOutput "  .\docker-manage.ps1 test coverage     # Run tests with coverage" "Cyan"
}

# Main execution
Show-Header

switch ($Command.ToLower()) {
    "help" { Show-Help }
    "check" { Test-Environment }
    "setup" { Initialize-Environment }
    "start" { 
        $profile = if ($Tools) { "tools" } else { "" }
        Start-Services -Profile $profile 
    }
    "stop" { Stop-Services }
    "restart" { Restart-Services -ServiceName $Service }
    "status" { Test-ServiceHealth }
    "logs" { Show-Logs -ServiceName $Service }
    "shell" { Enter-Shell -ServiceName $(if ($Service) { $Service } else { "backend" }) }
    "test" { Invoke-Tests -TestType $(if ($Service) { $Service } else { "all" }) }
    "migrate" { Invoke-DatabaseOperation -Operation "migrate" }
    "seed" { Invoke-DatabaseOperation -Operation "seed" }
    "backup" { Invoke-DatabaseOperation -Operation "backup" }
    "reset-db" { Invoke-DatabaseOperation -Operation "reset" }
    "clean" { Invoke-Cleanup -Type $(if ($Service) { $Service } else { "containers" }) }
    "monitor" { Show-Performance }
    "build" { 
        Write-ColoredOutput "🔨 Rebuilding Docker images..." "Yellow"
        docker-compose build --no-cache
        Write-ColoredOutput "✅ Build completed" "Green"
    }
    default { 
        Write-ColoredOutput "❌ Unknown command: $Command" "Red"
        Write-ColoredOutput "Use '.\docker-manage.ps1 help' for available commands" "Yellow"
    }
}
