@echo off
REM ===================================
REM Casino-Club F2P Frontend 실행 스크립트
REM ===================================

echo [INFO] Casino-Club F2P Frontend 시작 중...

REM 고정 경로 설정
set PROJECT_ROOT=c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
set FRONTEND_PATH=%PROJECT_ROOT%\frontend

echo [INFO] 프론트엔드 디렉토리로 이동: %FRONTEND_PATH%
cd /d "%FRONTEND_PATH%"

REM Node.js 및 npm 확인
echo [INFO] Node.js 버전 확인...
node --version
if errorlevel 1 (
    echo [ERROR] Node.js가 설치되지 않았습니다!
    echo [INFO] Node.js를 설치해주세요: https://nodejs.org/
    pause
    exit /b 1
)

REM npm 의존성 설치
echo [INFO] npm 의존성 설치 중...
npm install
if errorlevel 1 (
    echo [ERROR] npm 의존성 설치 실패!
    pause
    exit /b 1
)

REM Next.js 개발 서버 실행
echo [INFO] Next.js 개발 서버 시작...
echo [INFO] 프론트엔드 URL: http://localhost:3000
echo [INFO] 관리자 페이지: http://localhost:3000/admin
echo [INFO] 관리자 계정: admin / admin123
echo [INFO] 종료하려면 Ctrl+C를 누르세요
echo ===================================

npm run dev

pause
