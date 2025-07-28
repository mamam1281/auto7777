# ===================================
# Casino-Club F2P Frontend 실행 스크립트 (PowerShell)
# ===================================

# 고정 경로 설정
$PROJECT_ROOT = "c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp"
$FRONTEND_PATH = "$PROJECT_ROOT\frontend"

Write-Host "[INFO] Casino-Club F2P Frontend 시작 중..." -ForegroundColor Green

# 프론트엔드 디렉토리로 이동
Write-Host "[INFO] 프론트엔드 디렉토리로 이동: $FRONTEND_PATH" -ForegroundColor Yellow
Set-Location -Path $FRONTEND_PATH

# Node.js 확인
Write-Host "[INFO] Node.js 버전 확인..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Node.js가 설치되지 않았습니다!" -ForegroundColor Red
    Write-Host "[INFO] Node.js를 설치해주세요: https://nodejs.org/" -ForegroundColor Cyan
    Read-Host "Press any key to continue..."
    exit 1
}
Write-Host "[INFO] Node.js 버전: $nodeVersion" -ForegroundColor Green

# npm 의존성 설치
Write-Host "[INFO] npm 의존성 설치 중..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] npm 의존성 설치 실패!" -ForegroundColor Red
    Read-Host "Press any key to continue..."
    exit 1
}

# Next.js 개발 서버 실행
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "[INFO] Next.js 개발 서버 시작..." -ForegroundColor Green
Write-Host "[INFO] 프론트엔드 URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host "[INFO] 관리자 페이지: http://localhost:3000/admin" -ForegroundColor Cyan
Write-Host "[INFO] 관리자 계정: admin / admin123" -ForegroundColor Yellow
Write-Host "[INFO] 종료하려면 Ctrl+C를 누르세요" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Cyan

npm run dev
