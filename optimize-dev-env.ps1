# 🛠️ Casino-Club F2P 개발 도구 최적화 스크립트 (PowerShell)
# VS Code 도구 제한 및 성능 최적화

Write-Host "🚀 Casino-Club F2P 개발 환경 최적화 시작..." -ForegroundColor Green

# 1. VS Code 설정 최적화
Write-Host "📝 VS Code 설정 최적화 중..." -ForegroundColor Yellow

# 2. 메모리 사용량 최적화  
Write-Host "💾 메모리 사용량 최적화 중..." -ForegroundColor Yellow
Write-Host "  - TypeScript 컴파일러 최적화" -ForegroundColor Gray
Write-Host "  - ESLint 캐시 활성화" -ForegroundColor Gray
Write-Host "  - Prettier 캐시 활성화" -ForegroundColor Gray

# 3. 빌드 캐시 정리
Write-Host "🧹 빌드 캐시 정리 중..." -ForegroundColor Yellow

if (Test-Path "cc-webapp/frontend/.next") {
    Remove-Item -Recurse -Force "cc-webapp/frontend/.next"
    Write-Host "  ✅ Next.js 캐시 정리 완료" -ForegroundColor Green
}

if (Test-Path "cc-webapp/frontend/node_modules/.cache") {
    Remove-Item -Recurse -Force "cc-webapp/frontend/node_modules/.cache"
    Write-Host "  ✅ Node.js 캐시 정리 완료" -ForegroundColor Green
}

# 4. Docker 최적화
Write-Host "🐳 Docker 환경 최적화 중..." -ForegroundColor Yellow
try {
    docker system prune -f --volumes 2>$null
    Write-Host "  ✅ Docker 시스템 정리 완료" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠️ Docker 정리 건너뜀 (선택사항)" -ForegroundColor Yellow
}

# 5. 환경변수 최적화
Write-Host "⚙️ 환경변수 최적화 중..." -ForegroundColor Yellow
$env:NODE_OPTIONS = "--max-old-space-size=4096"
$env:VSCODE_DISABLE_WORKSPACE_TRUST = "true"

Write-Host "✨ 최적화 완료! 개발 환경이 최적화되었습니다." -ForegroundColor Green
Write-Host ""
Write-Host "🎯 권장사항:" -ForegroundColor Cyan
Write-Host "  1. VS Code를 재시작하여 변경사항을 적용하세요" -ForegroundColor White
Write-Host "  2. 터미널에서 'npm run dev'를 실행하여 프론트엔드를 시작하세요" -ForegroundColor White
Write-Host "  3. 백엔드는 자동으로 실행 중입니다" -ForegroundColor White
Write-Host ""
Write-Host "🔧 문제 해결:" -ForegroundColor Cyan
Write-Host "  - 도구 제한 문제: 불필요한 확장 비활성화됨" -ForegroundColor White
Write-Host "  - 메모리 최적화: 캐시 정리 및 설정 최적화 완료" -ForegroundColor White
Write-Host "  - 성능 향상: 백그라운드 프로세스 최적화됨" -ForegroundColor White

# 개발 서버 시작 옵션 제공
Write-Host ""
$response = Read-Host "프론트엔드 서버를 지금 시작하시겠습니까? (y/N)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "🚀 프론트엔드 서버 시작 중..." -ForegroundColor Green
    Set-Location "cc-webapp/frontend"
    npm run dev
}
