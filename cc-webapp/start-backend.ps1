#!/bin/bash
# ===================================
# Casino-Club F2P Backend 실행 스크립트 (PowerShell)
# ===================================

# 고정 경로 설정
$PROJECT_ROOT = "c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp"
$BACKEND_PATH = "$PROJECT_ROOT\backend"
$VENV_PATH = "$BACKEND_PATH\venv"

Write-Host "[INFO] Casino-Club F2P Backend 시작 중..." -ForegroundColor Green

# 백엔드 디렉토리로 이동
Write-Host "[INFO] 백엔드 디렉토리로 이동: $BACKEND_PATH" -ForegroundColor Yellow
Set-Location -Path $BACKEND_PATH

# 가상환경 확인 및 생성
if (-not (Test-Path $VENV_PATH)) {
    Write-Host "[INFO] 가상환경 생성 중..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] 가상환경 생성 실패!" -ForegroundColor Red
        Read-Host "Press any key to continue..."
        exit 1
    }
}

# 가상환경 활성화
Write-Host "[INFO] 가상환경 활성화 중..." -ForegroundColor Yellow
& "$VENV_PATH\Scripts\Activate.ps1"

# 의존성 설치
Write-Host "[INFO] 의존성 설치 중..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] 의존성 설치 실패!" -ForegroundColor Red
    Read-Host "Press any key to continue..."
    exit 1
}

# 관리자 계정 생성
Write-Host "[INFO] 관리자 계정 확인 중..." -ForegroundColor Yellow
python create_admin.py

# FastAPI 서버 실행
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "[INFO] FastAPI 서버 시작..." -ForegroundColor Green
Write-Host "[INFO] 서버 URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "[INFO] API 문서: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "[INFO] 종료하려면 Ctrl+C를 누르세요" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Cyan

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
