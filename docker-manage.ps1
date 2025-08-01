# Docker 환경 관리 스크립트

param (
    [string]$action = "help"
)

$ErrorActionPreference = "Stop"
$COMPOSE_FILE = "./docker-compose.yml"
$COMPOSE_DEV_FILE = "./docker-compose.override.yml"

function Show-Help {
    Write-Host "Casino-Club F2P 개발 환경 관리 스크립트"
    Write-Host "사용법: ./docker-manage.ps1 [action]"
    Write-Host ""
    Write-Host "가능한 액션:"
    Write-Host "  start       : 전체 개발 환경 시작"
    Write-Host "  stop        : 모든 컨테이너 중지"
    Write-Host "  restart     : 모든 컨테이너 재시작"
    Write-Host "  status      : 현재 컨테이너 상태 확인"
    Write-Host "  logs        : 전체 로그 보기"
    Write-Host "  backend     : 백엔드 로그 보기"
    Write-Host "  frontend    : 프론트엔드 로그 보기"
    Write-Host "  db          : 데이터베이스 로그 보기"
    Write-Host "  psql        : PostgreSQL CLI 연결"
    Write-Host "  redis-cli   : Redis CLI 연결"
    Write-Host "  cleanup     : 사용하지 않는 컨테이너/이미지 정리"
    Write-Host "  rebuild     : 전체 이미지 재빌드 및 시작"
    Write-Host ""
}

function Start-Environment {
    Write-Host "개발 환경 시작 중..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE up -d
    if ($LASTEXITCODE -ne 0) {
        Write-Error "환경 시작 실패!"
        exit 1
    }
    Write-Host "환경이 성공적으로 시작되었습니다."
    Write-Host "백엔드: http://localhost:8000/docs"
    Write-Host "프론트엔드: http://localhost:3000"
    docker-compose ps
}

function Stop-Environment {
    Write-Host "환경 중지 중..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE down
    Write-Host "환경이 성공적으로 중지되었습니다."
}

function Restart-Environment {
    Write-Host "환경 재시작 중..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE restart
    Write-Host "환경이 성공적으로 재시작되었습니다."
    docker-compose ps
}

function Show-Status {
    Write-Host "현재 환경 상태:"
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE ps
}

function Show-Logs {
    param (
        [string]$service = ""
    )
    
    if ($service -eq "") {
        Write-Host "모든 서비스 로그 표시 중..."
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE logs -f
    } else {
        Write-Host "$service 서비스 로그 표시 중..."
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE logs -f $service
    }
}

function Connect-Database {
    Write-Host "PostgreSQL에 연결 중..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE exec postgres psql -U cc_user -d cc_webapp
}

function Connect-Redis {
    Write-Host "Redis에 연결 중..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE exec redis redis-cli
}

function Clear-DockerResources {
    Write-Host "사용하지 않는 Docker 리소스 정리 중..."
    docker system prune -a --volumes -f
    Write-Host "정리 완료!"
}

function Reset-Environment {
    Write-Host "전체 환경 재빌드 중..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE down
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE build --no-cache
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_DEV_FILE up -d
    Write-Host "재빌드 및 시작 완료!"
    docker-compose ps
}

# 액션 실행
switch ($action) {
    "start" { Start-Environment }
    "stop" { Stop-Environment }
    "restart" { Restart-Environment }
    "status" { Show-Status }
    "logs" { Show-Logs }
    "backend" { Show-Logs "backend" }
    "frontend" { Show-Logs "frontend" }
    "db" { Show-Logs "postgres" }
    "psql" { Connect-Database }
    "redis-cli" { Connect-Redis }
    "cleanup" { Clear-DockerResources }
    "rebuild" { Reset-Environment }
    default { Show-Help }
}
