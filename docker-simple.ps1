# Docker 환경 관리 스크립트 (간소화 버전)
param ([string]$action = "help", [string]$service = "")

$ErrorActionPreference = "Stop"

# Docker Compose 파일 설정
$COMPOSE_FILE = "./docker-compose.yml"
$COMPOSE_DEV_FILE = "./docker-compose.override.yml"

# 텍스트 색상 함수
function Write-ColorText {
    param (
        [string]$text,
        [string]$color = "White"
    )
    Write-Host $text -ForegroundColor $color
}

# Docker Compose 명령어 함수
function Start-Docker {
    Write-ColorText "🚀 Docker 컨테이너 시작 중..." "Green"
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE up -d
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "✅ 환경이 성공적으로 시작되었습니다." "Green"
        Write-ColorText "🌐 프론트엔드: http://localhost:3000" "Cyan"
        Write-ColorText "🔧 백엔드 API: http://localhost:8000" "Cyan"
        Write-ColorText "📚 API 문서: http://localhost:8000/docs" "Cyan"
        docker-compose ps
    }
    else {
        Write-ColorText "❌ 환경 시작 실패. 로그를 확인하세요." "Red"
    }
}

function Stop-Docker {
    Write-ColorText "🛑 Docker 컨테이너 중지 중..." "Yellow"
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE down
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "✅ 환경이 성공적으로 중지되었습니다." "Green"
    }
    else {
        Write-ColorText "❌ 환경 중지 실패. 로그를 확인하세요." "Red"
    }
}

function Restart-Docker {
    Write-ColorText "🔄 Docker 컨테이너 재시작 중..." "Yellow"
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE restart
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "✅ 환경이 성공적으로 재시작되었습니다." "Green"
        docker-compose ps
    }
    else {
        Write-ColorText "❌ 환경 재시작 실패. 로그를 확인하세요." "Red"
    }
}

function Show-Status {
    Write-ColorText "📊 현재 컨테이너 상태:" "Cyan"
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE ps
}

function Show-Logs {
    if ($service -eq "") {
        Write-ColorText "📜 모든 서비스 로그 표시 중..." "Cyan"
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE logs -f
    }
    else {
        Write-ColorText "📜 $service 서비스 로그 표시 중..." "Cyan"
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE logs -f $service
    }
}

function Connect-Database {
    Write-ColorText "🔌 PostgreSQL에 연결 중..." "Cyan"
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE exec postgres psql -U cc_user -d cc_webapp
}

function Connect-Redis {
    Write-ColorText "🔌 Redis에 연결 중..." "Cyan"
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE exec redis redis-cli
}

function Enter-Container {
    if ($service -eq "") {
        Write-ColorText "❌ 서비스 이름을 지정해주세요." "Red"
        return
    }
    Write-ColorText "🔌 $service 컨테이너에 연결 중..." "Cyan"
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE exec $service bash
}

function Show-Help {
    Write-ColorText "🎮 Casino-Club F2P 개발 환경 관리 (간소화 버전)" "Cyan"
    Write-ColorText "================================================" "Cyan"
    Write-ColorText "사용법: ./docker-simple.ps1 [액션] [서비스]" "Yellow"
    Write-ColorText "`n가능한 액션:" "Yellow"
    Write-ColorText "  start       : 전체 개발 환경 시작" "White"
    Write-ColorText "  stop        : 모든 컨테이너 중지" "White"
    Write-ColorText "  restart     : 모든 컨테이너 재시작" "White"
    Write-ColorText "  status      : 현재 컨테이너 상태 확인" "White"
    Write-ColorText "  logs        : 전체 로그 보기 (또는 특정 서비스)" "White"
    Write-ColorText "  backend     : 백엔드 로그 보기" "White"
    Write-ColorText "  frontend    : 프론트엔드 로그 보기" "White"
    Write-ColorText "  db          : 데이터베이스 로그 보기" "White"
    Write-ColorText "  psql        : PostgreSQL CLI 연결" "White"
    Write-ColorText "  redis-cli   : Redis CLI 연결" "White"
    Write-ColorText "  bash        : 컨테이너 bash 쉘 접속 (서비스명 필요)" "White"
    Write-ColorText "`n예제:" "Yellow"
    Write-ColorText "  ./docker-simple.ps1 start" "White"
    Write-ColorText "  ./docker-simple.ps1 logs backend" "White"
    Write-ColorText "  ./docker-simple.ps1 bash backend" "White"
}

# 액션 실행
try {
    switch ($action) {
        "start" { Start-Docker }
        "stop" { Stop-Docker }
        "restart" { Restart-Docker }
        "status" { Show-Status }
        "logs" { Show-Logs }
        "backend" { Show-Logs "backend" }
        "frontend" { Show-Logs "frontend" }
        "db" { Show-Logs "postgres" }
        "psql" { Connect-Database }
        "redis-cli" { Connect-Redis }
        "bash" { Enter-Container }
        default { Show-Help }
    }
}
catch {
    Write-ColorText "❌ 오류 발생: $_" "Red"
    exit 1
}
