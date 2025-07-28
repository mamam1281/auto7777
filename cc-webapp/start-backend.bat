@echo off
REM ===================================
REM Casino-Club F2P Backend 실행 스크립트
REM ===================================

echo [INFO] Casino-Club F2P Backend 시작 중...

REM 고정 경로 설정
set PROJECT_ROOT=c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
set BACKEND_PATH=%PROJECT_ROOT%\backend
set VENV_PATH=%BACKEND_PATH%\venv

echo [INFO] 백엔드 디렉토리로 이동: %BACKEND_PATH%
cd /d "%BACKEND_PATH%"

REM 가상환경 확인 및 생성
if not exist "%VENV_PATH%" (
    echo [INFO] 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] 가상환경 생성 실패!
        pause
        exit /b 1
    )
)

REM 가상환경 활성화
echo [INFO] 가상환경 활성화 중...
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] 가상환경 활성화 실패!
    pause
    exit /b 1
)

REM 의존성 설치
echo [INFO] 의존성 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] 의존성 설치 실패!
    pause
    exit /b 1
)

REM 관리자 계정 생성 (이미 존재하면 스킵)
echo [INFO] 관리자 계정 확인 중...
python create_admin.py

REM FastAPI 서버 실행
echo [INFO] FastAPI 서버 시작...
echo [INFO] 서버 URL: http://localhost:8000
echo [INFO] API 문서: http://localhost:8000/docs
echo [INFO] 종료하려면 Ctrl+C를 누르세요
echo ===================================

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
