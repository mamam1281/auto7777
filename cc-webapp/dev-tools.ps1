# ===================================
# Casino-Club F2P 개발 도구 스크립트 (PowerShell)
# ===================================

# 고정 경로 설정
$PROJECT_ROOT = "c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp"
$BACKEND_PATH = "$PROJECT_ROOT\backend"
$FRONTEND_PATH = "$PROJECT_ROOT\frontend"

Write-Host "[INFO] Casino-Club F2P 개발 도구" -ForegroundColor Green

function Show-DevMenu {
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "        개발 도구 메뉴" -ForegroundColor White
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "1. 백엔드 테스트 실행" -ForegroundColor White
    Write-Host "2. 프론트엔드 테스트 실행" -ForegroundColor White
    Write-Host "3. 프론트엔드 린트 검사" -ForegroundColor White
    Write-Host "4. 프론트엔드 타입 체크" -ForegroundColor White
    Write-Host "5. 관리자 계정 생성" -ForegroundColor White
    Write-Host "6. 데이터베이스 초기화" -ForegroundColor White
    Write-Host "7. 의존성 업데이트" -ForegroundColor White
    Write-Host "8. 빌드 테스트" -ForegroundColor White
    Write-Host "9. 메인 메뉴로 돌아가기" -ForegroundColor White
    Write-Host "===================================" -ForegroundColor Cyan
}

function Test-Backend {
    Write-Host "[INFO] 백엔드 테스트 실행 중..." -ForegroundColor Yellow
    Set-Location -Path $BACKEND_PATH
    & "$BACKEND_PATH\venv\Scripts\Activate.ps1"
    pytest
    Read-Host "Press any key to continue..."
}

function Test-Frontend {
    Write-Host "[INFO] 프론트엔드 테스트 실행 중..." -ForegroundColor Yellow
    Set-Location -Path $FRONTEND_PATH
    npm test
    Read-Host "Press any key to continue..."
}

function Lint-Frontend {
    Write-Host "[INFO] 프론트엔드 린트 검사 중..." -ForegroundColor Yellow
    Set-Location -Path $FRONTEND_PATH
    npm run lint
    Read-Host "Press any key to continue..."
}

function TypeCheck-Frontend {
    Write-Host "[INFO] 프론트엔드 타입 체크 중..." -ForegroundColor Yellow
    Set-Location -Path $FRONTEND_PATH
    npm run type-check
    Read-Host "Press any key to continue..."
}

function Create-AdminAccount {
    Write-Host "[INFO] 관리자 계정 생성 중..." -ForegroundColor Yellow
    Set-Location -Path $BACKEND_PATH
    & "$BACKEND_PATH\venv\Scripts\Activate.ps1"
    python create_admin.py
    Read-Host "Press any key to continue..."
}

function Initialize-Database {
    Write-Host "[INFO] 데이터베이스 초기화 중..." -ForegroundColor Yellow
    Set-Location -Path $BACKEND_PATH
    & "$BACKEND_PATH\venv\Scripts\Activate.ps1"
    python -c "from app.database import init_db; init_db()"
    Write-Host "[INFO] 데이터베이스 초기화 완료" -ForegroundColor Green
    Read-Host "Press any key to continue..."
}

function Update-Dependencies {
    Write-Host "[INFO] 의존성 업데이트 중..." -ForegroundColor Yellow
    
    Write-Host "[INFO] 백엔드 의존성 업데이트..." -ForegroundColor Yellow
    Set-Location -Path $BACKEND_PATH
    & "$BACKEND_PATH\venv\Scripts\Activate.ps1"
    pip install -r requirements.txt --upgrade
    
    Write-Host "[INFO] 프론트엔드 의존성 업데이트..." -ForegroundColor Yellow
    Set-Location -Path $FRONTEND_PATH
    npm update
    
    Write-Host "[INFO] 의존성 업데이트 완료" -ForegroundColor Green
    Read-Host "Press any key to continue..."
}

function Test-Build {
    Write-Host "[INFO] 빌드 테스트 중..." -ForegroundColor Yellow
    Set-Location -Path $FRONTEND_PATH
    npm run build
    Write-Host "[INFO] 빌드 테스트 완료" -ForegroundColor Green
    Read-Host "Press any key to continue..."
}

do {
    Show-DevMenu
    $choice = Read-Host "선택하세요 (1-9)"
    
    switch ($choice) {
        "1" { Test-Backend }
        "2" { Test-Frontend }
        "3" { Lint-Frontend }
        "4" { TypeCheck-Frontend }
        "5" { Create-AdminAccount }
        "6" { Initialize-Database }
        "7" { Update-Dependencies }
        "8" { Test-Build }
        "9" { 
            Write-Host "[INFO] 메인 메뉴로 돌아갑니다..." -ForegroundColor Yellow
            return
        }
        default { 
            Write-Host "[ERROR] 잘못된 선택입니다." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
    
    Set-Location -Path $PROJECT_ROOT
} while ($true)
