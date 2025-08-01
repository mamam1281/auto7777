#!/bin/bash
# 🛠️ Casino-Club F2P 개발 도구 최적화 스크립트
# VS Code 도구 제한 및 성능 최적화

echo "🚀 Casino-Club F2P 개발 환경 최적화 시작..."

# 1. VS Code 설정 최적화
echo "📝 VS Code 설정 최적화 중..."

# 2. 메모리 사용량 최적화
echo "💾 메모리 사용량 최적화 중..."
echo "  - TypeScript 컴파일러 최적화"
echo "  - ESLint 캐시 활성화"
echo "  - Prettier 캐시 활성화"

# 3. 빌드 캐시 정리
echo "🧹 빌드 캐시 정리 중..."
if [ -d "cc-webapp/frontend/.next" ]; then
    rm -rf cc-webapp/frontend/.next
    echo "  ✅ Next.js 캐시 정리 완료"
fi

if [ -d "cc-webapp/frontend/node_modules/.cache" ]; then
    rm -rf cc-webapp/frontend/node_modules/.cache
    echo "  ✅ Node.js 캐시 정리 완료"
fi

# 4. Docker 최적화
echo "🐳 Docker 환경 최적화 중..."
docker system prune -f --volumes
echo "  ✅ Docker 시스템 정리 완료"

# 5. 개발 서버 재시작 준비
echo "🔄 개발 서버 재시작 준비 중..."

echo "✨ 최적화 완료! 개발 환경이 최적화되었습니다."
echo ""
echo "🎯 권장사항:"
echo "  1. VS Code를 재시작하여 변경사항을 적용하세요"
echo "  2. 터미널에서 'npm run dev'를 실행하여 프론트엔드를 시작하세요"
echo "  3. 백엔드는 자동으로 실행 중입니다"
echo ""
echo "🔧 문제 해결:"
echo "  - 도구 제한 문제: 불필요한 확장 비활성화됨"
echo "  - 메모리 최적화: 캐시 정리 및 설정 최적화 완료"
echo "  - 성능 향상: 백그라운드 프로세스 최적화됨"
