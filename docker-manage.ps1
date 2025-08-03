# Casino-Club F2P 고도화된 Docker 관리 스크립트 v3.0
param(
    [Parameter(Position = 0)]
    [string]$Command = "help",

    [Parameter(Position = 1)]
    [string]$Service = "",

    [switch]$Tools,
    [switch]$Force,
    [switch]$Monitoring
)

$ErrorActionPreference = "Stop"

# 컬러 출력 함수
function Write-ColoredOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-Help {
    Write-ColoredOutput "🎰 Casino-Club F2P 고도화 Docker 관리 도구 v3.0" "Cyan"
    Write-ColoredOutput "=" * 60 "Gray"
    Write-ColoredOutput "사용법: .\docker-manage.ps1 <명령어> [서비스] [옵션]" "Yellow"
    Write-ColoredOutput ""
    Write-ColoredOutput "📋 핵심 명령어:" "Green"
    Write-ColoredOutput "  check        - 개발환경 전체 점검" "White"
    Write-ColoredOutput "  setup        - 초기 환경 설정 및 구성" "White"
    Write-ColoredOutput "  start        - 서비스 시작" "White"
    Write-ColoredOutput "  stop         - 서비스 정지" "White"
    Write-ColoredOutput "  restart      - 서비스 재시작" "White"
    Write-ColoredOutput "  status       - 서비스 상태 및 헬스체크" "White"
    Write-ColoredOutput "  monitor      - 실시간 성능 모니터링" "White"
    Write-ColoredOutput "  logs         - 서비스 로그 확인" "White"
    Write-ColoredOutput "  shell        - 컨테이너 내부 접속" "White"
    Write-ColoredOutput ""
    Write-ColoredOutput "🗃️ 데이터베이스 관리:" "Green"
    Write-ColoredOutput "  migrate      - 데이터베이스 마이그레이션" "White"
    Write-ColoredOutput "  seed         - 테스트 데이터 생성" "White"
    Write-ColoredOutput "  backup       - 데이터베이스 백업" "White"
    Write-ColoredOutput "  reset-db     - 데이터베이스 리셋" "White"
    Write-ColoredOutput ""
    Write-ColoredOutput "🧪 테스트 & 빌드:" "Green"  
    Write-ColoredOutput "  test         - 테스트 실행" "White"
    Write-ColoredOutput "  build        - 이미지 빌드" "White"
    Write-ColoredOutput "  clean        - 정리 작업" "White"
    Write-ColoredOutput "  reset        - 완전 초기화" "White"
    Write-ColoredOutput ""
    Write-ColoredOutput "🔧 옵션:" "Green"
    Write-ColoredOutput "  --tools      - 개발 도구 포함 (pgAdmin, Redis Commander, Kafka UI)" "White"
    Write-ColoredOutput "  --monitoring - 모니터링 도구 포함" "White"
    Write-ColoredOutput "  --force      - 강제 실행" "White"
    Write-ColoredOutput ""
    Write-ColoredOutput "🎯 서비스별 작업:" "Green"
    Write-ColoredOutput "  backend      - 백엔드 서비스" "White"
    Write-ColoredOutput "  frontend     - 프론트엔드 서비스" "White"
    Write-ColoredOutput "  postgres     - PostgreSQL 데이터베이스" "White"
    Write-ColoredOutput "  redis        - Redis 캐시" "White"
    Write-ColoredOutput "  kafka        - Kafka 메시지 큐" "White"
    Write-ColoredOutput ""
    Write-ColoredOutput "📚 실용 예제:" "Green"
    Write-ColoredOutput "  .\docker-manage.ps1 check" "Gray"
    Write-ColoredOutput "  .\docker-manage.ps1 start --tools" "Gray"
    Write-ColoredOutput "  .\docker-manage.ps1 logs backend" "Gray"
    Write-ColoredOutput "  .\docker-manage.ps1 shell backend" "Gray"
    Write-ColoredOutput "  .\docker-manage.ps1 test coverage" "Gray"
    Write-ColoredOutput "  .\docker-manage.ps1 monitor" "Gray"
}

function Test-DockerRunning {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        Write-ColoredOutput "❌ Docker가 실행되지 않았습니다. Docker Desktop을 시작해주세요." "Red"
        exit 1
    }
}

function Setup-Environment {
    Write-ColoredOutput "🚀 Casino-Club F2P 환경 설정 시작..." "Cyan"
    
    # Docker 상태 확인
    Test-DockerRunning
    
    # 필수 디렉토리 생성
    $directories = @(
        "logs/backend",
        "logs/frontend",
        "logs/postgres",
        "logs/celery",
        "data/init",
        "data/backup"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-ColoredOutput "📁 디렉토리 생성: $dir" "Green"
        }
    }
    
    # 환경변수 파일 확인
    if (!(Test-Path ".env.development")) {
        Write-ColoredOutput "⚠️ .env.development 파일이 없습니다. 샘플 파일을 생성합니다." "Yellow"
        # 환경변수 파일 생성 로직 추가 필요
    }
    
    Write-ColoredOutput "✅ 환경 설정 완료!" "Green"
}

function Start-Services {
    Write-ColoredOutput "🚀 서비스 시작..." "Cyan"
    
    Test-DockerRunning
    
    $composeArgs = @("up", "-d", "--build")
    
    if ($Tools) {
        $composeArgs += "--profile"
        $composeArgs += "tools"
        Write-ColoredOutput "🛠️ 개발 도구 포함하여 시작..." "Yellow"
    }
    
    try {
        & docker-compose @composeArgs
        Write-ColoredOutput "✅ 서비스 시작 완료!" "Green"
        Show-ServiceStatus
    }
    catch {
        Write-ColoredOutput "❌ 서비스 시작 실패: $($_.Exception.Message)" "Red"
        exit 1
    }
}

function Stop-Services {
    Write-ColoredOutput "🛑 서비스 정지..." "Cyan"
    
    try {
        docker-compose down
        Write-ColoredOutput "✅ 서비스 정지 완료!" "Green"
    }
    catch {
        Write-ColoredOutput "❌ 서비스 정지 실패: $($_.Exception.Message)" "Red"
    }
}

function Show-ServiceStatus {
    Write-ColoredOutput "📊 서비스 상태:" "Cyan"
    docker-compose ps
    
    Write-ColoredOutput "`n🌐 서비스 URL:" "Cyan"
    Write-ColoredOutput "  Frontend:    http://localhost:3000" "Green"
    Write-ColoredOutput "  Backend API: http://localhost:8000" "Green"
    Write-ColoredOutput "  API Docs:    http://localhost:8000/docs" "Green"
    
    if ($Tools) {
        Write-ColoredOutput "  pgAdmin:     http://localhost:5050" "Yellow"
        Write-ColoredOutput "  Redis UI:    http://localhost:8081" "Yellow"
    }
}

function Show-Logs {
    if ($Service) {
        Write-ColoredOutput "📋 $Service 로그:" "Cyan"
        docker-compose logs -f $Service
    }
    else {
        Write-ColoredOutput "📋 전체 로그:" "Cyan"
        docker-compose logs -f
    }
}

function Reset-Environment {
    if (!$Force) {
        $confirm = Read-Host "⚠️ 모든 데이터가 삭제됩니다. 계속하시겠습니까? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-ColoredOutput "❌ 취소되었습니다." "Yellow"
            return
        }
    }
    
    Write-ColoredOutput "🧹 완전 초기화 시작..." "Red"
    
    # 컨테이너 정지 및 삭제
    docker-compose down --volumes --remove-orphans
    
    # 이미지 정리
    docker system prune -f
    
    # 로그 파일 정리
    if (Test-Path "logs") {
        Remove-Item -Path "logs\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Write-ColoredOutput "✅ 완전 초기화 완료!" "Green"
    Write-ColoredOutput "다음 명령어로 재시작하세요: .\docker-manage.ps1 setup" "Yellow"
}

# 누락된 함수들 추가
function Check-Environment {
    Write-ColoredOutput "🔍 개발환경 전체 점검 시작..." "Cyan"
    
    # Docker 상태 확인
    Test-DockerRunning
    Write-ColoredOutput "✅ Docker 실행 상태: 정상" "Green"
    
    # 환경 파일 확인
    $envFiles = @(".env.development", "docker-compose.yml", "cc-webapp/frontend/package.json")
    foreach ($file in $envFiles) {
        if (Test-Path $file) {
            Write-ColoredOutput "✅ $file: 존재" "Green"
        }
        else {
            Write-ColoredOutput "❌ $file: 누락" "Red"
        }
    }
    
    # 프론트엔드 의존성 확인
    Write-ColoredOutput "🔍 프론트엔드 의존성 점검..." "Yellow"
    if (Test-Path "cc-webapp/frontend/node_modules") {
        Write-ColoredOutput "✅ node_modules: 존재" "Green"
    }
    else {
        Write-ColoredOutput "⚠️ node_modules: 누락 - npm install 필요" "Yellow"
    }
    
    Write-ColoredOutput "✅ 환경 점검 완료!" "Green"
}

function Restart-Services {
    Write-ColoredOutput "🔄 서비스 재시작..." "Cyan"
    Stop-Services
    Start-Sleep 2
    Start-Services
}

function Show-Performance {
    Write-ColoredOutput "📊 실시간 성능 모니터링..." "Cyan"
    Write-ColoredOutput "Ctrl+C로 종료하세요" "Yellow"
    docker stats
}

function Enter-Container {
    if (!$Service) {
        Write-ColoredOutput "❌ 서비스를 지정해주세요. 예: .\docker-manage.ps1 shell backend" "Red"
        return
    }
    
    Write-ColoredOutput "🚪 $Service 컨테이너 접속..." "Cyan"
    
    switch ($Service.ToLower()) {
        "backend" { docker-compose exec backend bash }
        "frontend" { docker-compose exec frontend sh }
        "postgres" { docker-compose exec postgres psql -U cc_user -d cc_webapp }
        "redis" { docker-compose exec redis redis-cli }
        default {
            Write-ColoredOutput "❌ 지원되지 않는 서비스: $Service" "Red"
            Write-ColoredOutput "지원 서비스: backend, frontend, postgres, redis" "Yellow"
        }
    }
}

function Run-Migration {
    Write-ColoredOutput "🗃️ 데이터베이스 마이그레이션 실행..." "Cyan"
    docker-compose exec backend python -m alembic upgrade head
    Write-ColoredOutput "✅ 마이그레이션 완료!" "Green"
}

function Seed-TestData {
    Write-ColoredOutput "🌱 테스트 데이터 생성..." "Cyan"
    docker-compose exec backend python db_auto_init.py
    Write-ColoredOutput "✅ 테스트 데이터 생성 완료!" "Green"
}

function Backup-Database {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "data/backup/cc_webapp_$timestamp.sql"
    
    Write-ColoredOutput "💾 데이터베이스 백업 생성..." "Cyan"
    docker-compose exec postgres pg_dump -U cc_user cc_webapp > $backupFile
    Write-ColoredOutput "✅ 백업 완료: $backupFile" "Green"
}

function Reset-Database {
    Write-ColoredOutput "🗃️ 데이터베이스 리셋..." "Red"
    docker-compose exec postgres psql -U cc_user -c "DROP DATABASE IF EXISTS cc_webapp;"
    docker-compose exec postgres psql -U cc_user -c "CREATE DATABASE cc_webapp;"
    Run-Migration
    Seed-TestData
    Write-ColoredOutput "✅ 데이터베이스 리셋 완료!" "Green"
}

function Run-Tests {
    Write-ColoredOutput "🧪 테스트 실행..." "Cyan"
    
    if ($Service -eq "coverage") {
        Write-ColoredOutput "📊 커버리지 포함 백엔드 테스트..." "Yellow"
        docker-compose exec backend pytest --cov=app --cov-report=html --cov-report=term
    }
    elseif ($Service -eq "frontend") {
        Write-ColoredOutput "🖥️ 프론트엔드 테스트..." "Yellow"
        docker-compose exec frontend npm test
    }
    elseif ($Service -eq "backend") {
        Write-ColoredOutput "⚙️ 백엔드 테스트..." "Yellow"
        docker-compose exec backend pytest -v
    }
    else {
        Write-ColoredOutput "🧪 전체 테스트..." "Yellow"
        docker-compose exec backend pytest -v
        docker-compose exec frontend npm test -- --passWithNoTests
    }
    
    Write-ColoredOutput "✅ 테스트 완료!" "Green"
}

function Build-Images {
    Write-ColoredOutput "🏗️ Docker 이미지 빌드..." "Cyan"
    
    if ($Service) {
        Write-ColoredOutput "🎯 $Service 서비스 빌드..." "Yellow"
        docker-compose build --no-cache $Service
    }
    else {
        Write-ColoredOutput "🎯 전체 서비스 빌드..." "Yellow"
        docker-compose build --no-cache
    }
    
    Write-ColoredOutput "✅ 빌드 완료!" "Green"
}

function Clean-Environment {
    Write-ColoredOutput "🧹 환경 정리..." "Cyan"
    
    if ($Service -eq "volumes") {
        Write-ColoredOutput "📦 볼륨 정리..." "Yellow"
        docker-compose down --volumes
        docker volume prune -f
    }
    elseif ($Service -eq "containers") {
        Write-ColoredOutput "📦 컨테이너 정리..." "Yellow"
        docker-compose down --remove-orphans
        docker container prune -f
    }
    else {
        Write-ColoredOutput "🗑️ 일반 정리..." "Yellow"
        docker-compose down
        docker system prune -f --volumes
    }
    
    Write-ColoredOutput "✅ 정리 완료!" "Green"
}

# 메인 실행 로직
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "check" { Check-Environment }
    "setup" { Setup-Environment }
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" { Restart-Services }
    "status" { Show-ServiceStatus }
    "monitor" { Show-Performance }
    "logs" { Show-Logs }
    "shell" { Enter-Container }
    "migrate" { Run-Migration }
    "seed" { Seed-TestData }
    "backup" { Backup-Database }
    "reset-db" { Reset-Database }
    "test" { Run-Tests }
    "build" { Build-Images }
    "clean" { Clean-Environment }
    "reset" { Reset-Environment }
    default {
        Write-ColoredOutput "❌ 알 수 없는 명령어: $Command" "Red"
        Show-Help
        exit 1
    }
}
