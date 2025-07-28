@echo off
REM ===================================
REM Casino-Club F2P 개발 도구 스크립트
REM ===================================

echo [INFO] Casino-Club F2P 개발 도구

REM 고정 경로 설정
set PROJECT_ROOT=c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
set BACKEND_PATH=%PROJECT_ROOT%\backend
set FRONTEND_PATH=%PROJECT_ROOT%\frontend

:start
echo ===================================
echo        개발 도구 메뉴
echo ===================================
echo 1. 백엔드 테스트 실행
echo 2. 프론트엔드 테스트 실행
echo 3. 프론트엔드 린트 검사
echo 4. 프론트엔드 타입 체크
echo 5. 관리자 계정 생성
echo 6. 데이터베이스 초기화
echo 7. 의존성 업데이트
echo 8. 빌드 테스트
echo 9. 메인 메뉴로 돌아가기
echo ===================================

set /p choice="선택하세요 (1-9): "

if "%choice%"=="1" (
    echo [INFO] 백엔드 테스트 실행 중...
    cd /d "%BACKEND_PATH%"
    call venv\Scripts\activate.bat
    pytest
    pause
    goto :start
)

if "%choice%"=="2" (
    echo [INFO] 프론트엔드 테스트 실행 중...
    cd /d "%FRONTEND_PATH%"
    npm test
    pause
    goto :start
)

if "%choice%"=="3" (
    echo [INFO] 프론트엔드 린트 검사 중...
    cd /d "%FRONTEND_PATH%"
    npm run lint
    pause
    goto :start
)

if "%choice%"=="4" (
    echo [INFO] 프론트엔드 타입 체크 중...
    cd /d "%FRONTEND_PATH%"
    npm run type-check
    pause
    goto :start
)

if "%choice%"=="5" (
    echo [INFO] 관리자 계정 생성 중...
    cd /d "%BACKEND_PATH%"
    call venv\Scripts\activate.bat
    python create_admin.py
    pause
    goto :start
)

if "%choice%"=="6" (
    echo [INFO] 데이터베이스 초기화 중...
    cd /d "%BACKEND_PATH%"
    call venv\Scripts\activate.bat
    python -c "from app.database import init_db; init_db()"
    echo [INFO] 데이터베이스 초기화 완료
    pause
    goto :start
)

if "%choice%"=="7" (
    echo [INFO] 의존성 업데이트 중...
    echo [INFO] 백엔드 의존성 업데이트...
    cd /d "%BACKEND_PATH%"
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --upgrade
    echo [INFO] 프론트엔드 의존성 업데이트...
    cd /d "%FRONTEND_PATH%"
    npm update
    echo [INFO] 의존성 업데이트 완료
    pause
    goto :start
)

if "%choice%"=="8" (
    echo [INFO] 빌드 테스트 중...
    echo [INFO] 프론트엔드 빌드 테스트...
    cd /d "%FRONTEND_PATH%"
    npm run build
    echo [INFO] 빌드 테스트 완료
    pause
    goto :start
)

if "%choice%"=="9" (
    echo [INFO] 메인 메뉴로 돌아갑니다...
    exit /b 0
)

echo [ERROR] 잘못된 선택입니다.
pause
goto :start
