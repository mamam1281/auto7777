@echo off
REM ===================================
REM Casino-Club F2P 전체 실행 스크립트
REM ===================================

echo [INFO] Casino-Club F2P 전체 시스템 시작 중...

REM 고정 경로 설정
set PROJECT_ROOT=c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp

echo [INFO] 프로젝트 루트: %PROJECT_ROOT%
cd /d "%PROJECT_ROOT%"

echo ===================================
echo     Casino-Club F2P 실행 메뉴
echo ===================================
echo 1. 백엔드만 실행 (FastAPI)
echo 2. 프론트엔드만 실행 (Next.js)
echo 3. 전체 실행 (백엔드 + 프론트엔드)
echo 4. 개발 도구 (테스트, 린트 등)
echo 5. 종료
echo ===================================

set /p choice="선택하세요 (1-5): "

if "%choice%"=="1" (
    echo [INFO] 백엔드만 실행합니다...
    start "Backend Server" cmd /k "start-backend.bat"
    goto :end
)

if "%choice%"=="2" (
    echo [INFO] 프론트엔드만 실행합니다...
    start "Frontend Server" cmd /k "start-frontend.bat"
    goto :end
)

if "%choice%"=="3" (
    echo [INFO] 전체 시스템을 실행합니다...
    echo [INFO] 백엔드 서버 시작 중...
    start "Backend Server" cmd /k "start-backend.bat"
    timeout /t 5 /nobreak >nul
    echo [INFO] 프론트엔드 서버 시작 중...
    start "Frontend Server" cmd /k "start-frontend.bat"
    goto :end
)

if "%choice%"=="4" (
    echo [INFO] 개발 도구 메뉴로 이동...
    call dev-tools.bat
    goto :end
)

if "%choice%"=="5" (
    echo [INFO] 종료합니다...
    goto :end
)

echo [ERROR] 잘못된 선택입니다.
pause
goto :start

:end
echo [INFO] 실행 완료!
pause
