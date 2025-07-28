# ===================================
# Casino-Club F2P 전체 실행 스크립트 (PowerShell)
# ===================================

# 고정 경로 설정
$PROJECT_ROOT = "c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp"

Write-Host "[INFO] Casino-Club F2P 전체 시스템 시작 중..." -ForegroundColor Green
Write-Host "[INFO] 프로젝트 루트: $PROJECT_ROOT" -ForegroundColor Yellow

Set-Location -Path $PROJECT_ROOT

function Show-Menu {
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "     Casino-Club F2P 실행 메뉴" -ForegroundColor White
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "1. 백엔드만 실행 (FastAPI)" -ForegroundColor White
    Write-Host "2. 프론트엔드만 실행 (Next.js)" -ForegroundColor White
    Write-Host "3. 전체 실행 (백엔드 + 프론트엔드)" -ForegroundColor White
    Write-Host "4. 개발 도구 (테스트, 린트 등)" -ForegroundColor White
    Write-Host "5. 종료" -ForegroundColor White
    Write-Host "===================================" -ForegroundColor Cyan
}

function Start-Backend {
    Write-Host "[INFO] 백엔드 서버를 시작합니다..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-File", "start-backend.ps1"
}

function Start-Frontend {
    Write-Host "[INFO] 프론트엔드 서버를 시작합니다..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-File", "start-frontend.ps1"
}

function Start-Both {
    Write-Host "[INFO] 전체 시스템을 시작합니다..." -ForegroundColor Green
    Write-Host "[INFO] 백엔드 서버 시작 중..." -ForegroundColor Yellow
    Start-Backend
    Start-Sleep -Seconds 5
    Write-Host "[INFO] 프론트엔드 서버 시작 중..." -ForegroundColor Yellow
    Start-Frontend
}

function Start-DevTools {
    Write-Host "[INFO] 개발 도구를 시작합니다..." -ForegroundColor Green
    & ".\dev-tools.ps1"
}

do {
    Show-Menu
    $choice = Read-Host "선택하세요 (1-5)"
    
    switch ($choice) {
        "1" { Start-Backend; break }
        "2" { Start-Frontend; break }
        "3" { Start-Both; break }
        "4" { Start-DevTools; break }
        "5" { 
            Write-Host "[INFO] 종료합니다..." -ForegroundColor Yellow
            exit 0
        }
        default { 
            Write-Host "[ERROR] 잘못된 선택입니다." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
} while ($true)
