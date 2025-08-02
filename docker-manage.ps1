# Casino-Club F2P Docker 관리 스크립트 v2.0
param(
    [Parameter(Position=0)]
    [string]$Command = "help",

    [Parameter(Position=1)]
    [string]$Service = "",

    [switch]$Tools,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# 컬러 출력 함수
function Write-ColoredOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-Help {
    Write-ColoredOutput "🎰 Casino-Club F2P Docker 관리 도구" "Cyan"
    Write-ColoredOutput "=" * 50 "Gray"
    Write-ColoredOutput "사용법: .\docker-manage.ps1 <명령어> [옵션]" "Yellow"
    Write-ColoredOutput ""
    Write-ColoredOutput "📋 주요 명령어:" "Green"
    Write-ColoredOutput "  setup        - 초기 환경 설정" "White"
    Write-ColoredOutput "  start        - 서비스 시작" "White"
    Write-ColoredOutput "  stop         - 서비스 정지" "White"
    Write-ColoredOutput "  restart      - 서비스 재시작" "White"
    Write-ColoredOutput "  status       - 서비스 상태 확인" "White"
    Write-ColoredOutput "  logs         - 로그 확인" "White"
    Write-ColoredOutput "  clean        - 정리 작업" "White"
    Write-ColoredOutput "  reset        - 완전 초기화" "White"
    Write-ColoredOutput ""
    Write-ColoredOutput "🔧 옵션:" "Green"
    Write-ColoredOutput "  --tools      - 개발 도구 포함 (pgAdmin, Redis Commander)" "White"
    Write-ColoredOutput "  --force      - 강제 실행" "White"
    Write-ColoredOutput ""
    Write-ColoredOutput "📚 예제:" "Green"
    Write-ColoredOutput "  .\docker-manage.ps1 start --tools" "Gray"
    Write-ColoredOutput "  .\docker-manage.ps1 logs backend" "Gray"
    Write-ColoredOutput "  .\docker-manage.ps1 reset --force" "Gray"
}

function Test-DockerRunning {
    try {
        docker info | Out-Null
        return $true
    } catch {
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
    } catch {
        Write-ColoredOutput "❌ 서비스 시작 실패: $($_.Exception.Message)" "Red"
        exit 1
    }
}

function Stop-Services {
    Write-ColoredOutput "🛑 서비스 정지..." "Cyan"
    
    try {
        docker-compose down
        Write-ColoredOutput "✅ 서비스 정지 완료!" "Green"
    } catch {
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
    } else {
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

# 메인 실행 로직
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "setup" { Setup-Environment }
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" { Stop-Services; Start-Services }
    "status" { Show-ServiceStatus }
    "logs" { Show-Logs }
    "reset" { Reset-Environment }
    "clean" { Reset-Environment }
    default {
        Write-ColoredOutput "❌ 알 수 없는 명령어: $Command" "Red"
        Show-Help
        exit 1
    }
}
