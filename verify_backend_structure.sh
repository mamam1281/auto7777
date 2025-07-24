#!/bin/bash
# 🔍 백엔드 구조 표준화 검증 스크립트

echo "🚀 CC Webapp 백엔드 구조 표준화 검증 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 결과 추적
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 체크 함수
check_step() {
    local description="$1"
    local command="$2"
    local expected_result="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "\n${BLUE}📋 체크 ${TOTAL_CHECKS}: ${description}${NC}"
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 통과${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ 실패${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        echo -e "${YELLOW}💡 권장 해결방법: ${expected_result}${NC}"
        return 1
    fi
}

# 실패 시 상세 로그 함수
detailed_check() {
    local description="$1"
    local command="$2"
    local log_file="/tmp/cc_webapp_check.log"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "\n${BLUE}📋 상세 체크 ${TOTAL_CHECKS}: ${description}${NC}"
    
    if eval "$command" > "$log_file" 2>&1; then
        echo -e "${GREEN}✅ 통과${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ 실패${NC}"
        echo -e "${YELLOW}🔍 에러 로그:${NC}"
        cat "$log_file"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

echo -e "\n${BLUE}🔍 Phase 1: 프로젝트 구조 검증${NC}"

# 1. 필수 디렉토리 존재 확인
check_step "cc-webapp/backend 디렉토리 존재" \
    "test -d cc-webapp/backend" \
    "cc-webapp/backend 디렉토리를 생성하세요"

check_step "cc-webapp/backend/app 디렉토리 존재" \
    "test -d cc-webapp/backend/app" \
    "cc-webapp/backend/app 디렉토리를 생성하세요"

# 2. 핵심 파일 존재 확인
check_step "main.py 파일 존재" \
    "test -f cc-webapp/backend/app/main.py" \
    "app/main.py 파일을 생성하세요"

check_step "models.py 파일 존재" \
    "test -f cc-webapp/backend/app/models.py" \
    "app/models.py 파일을 생성하세요"

check_step "requirements.txt 파일 존재" \
    "test -f cc-webapp/backend/requirements.txt" \
    "requirements.txt 파일을 생성하세요"

echo -e "\n${BLUE}🔍 Phase 2: Import 경로 검증${NC}"

# 3. 잘못된 import 패턴 검색
echo -e "\n${YELLOW}🔍 잘못된 import 패턴 검색 중...${NC}"

# backend.app 패턴 검색
BACKEND_IMPORTS=$(find cc-webapp/backend -name "*.py" -exec grep -l "from backend\.app\." {} \; 2>/dev/null)
if [ -n "$BACKEND_IMPORTS" ]; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    echo -e "${RED}❌ 잘못된 backend.app import 발견:${NC}"
    echo "$BACKEND_IMPORTS"
    echo -e "${YELLOW}💡 해결방법: 'from backend.app.' → 'from app.'으로 수정${NC}"
else
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    echo -e "${GREEN}✅ backend.app import 패턴 없음${NC}"
fi

# 상대 경로 import 검색
RELATIVE_IMPORTS=$(find cc-webapp/backend -name "*.py" -exec grep -l "from \.\." {} \; 2>/dev/null)
if [ -n "$RELATIVE_IMPORTS" ]; then
    echo -e "${YELLOW}⚠️ 상대 경로 import 발견 (검토 필요):${NC}"
    echo "$RELATIVE_IMPORTS"
    echo -e "${YELLOW}💡 권장: 상대 경로를 절대 경로로 변경 고려${NC}"
fi

echo -e "\n${BLUE}🔍 Phase 3: Docker 설정 검증${NC}"

# 4. Docker 파일 검증
check_step "Dockerfile 존재" \
    "test -f cc-webapp/backend/Dockerfile" \
    "cc-webapp/backend/Dockerfile을 생성하세요"

check_step "docker-compose.yml의 backend 서비스 확인" \
    "grep -q 'backend:' docker-compose.yml" \
    "docker-compose.yml에 backend 서비스를 추가하세요"

# 5. Docker 빌드 테스트 (실제 빌드는 시간이 오래 걸리므로 설정만 검증)
check_step "Docker Compose 설정 구문 검증" \
    "docker-compose config > /dev/null" \
    "docker-compose.yml 구문을 수정하세요"

echo -e "\n${BLUE}🔍 Phase 4: Python 환경 검증${NC}"

# 6. Python 의존성 검증
if [ -f "cc-webapp/backend/requirements.txt" ]; then
    check_step "requirements.txt 구문 검증" \
        "python -m pip install --dry-run -r cc-webapp/backend/requirements.txt" \
        "requirements.txt의 패키지 버전을 확인하세요"
fi

echo -e "\n${BLUE}🔍 Phase 5: 실제 동작 테스트${NC}"

# 7. 컨테이너 빌드 및 실행 테스트
echo -e "\n${YELLOW}🐳 Docker 빌드 테스트 시작...${NC}"
detailed_check "Docker backend 이미지 빌드" \
    "cd cc-webapp/backend && docker build -t cc-webapp-backend-test ."

if [ $? -eq 0 ]; then
    echo -e "\n${YELLOW}🚀 컨테이너 실행 테스트...${NC}"
    
    # 컨테이너 실행 (30초 후 자동 종료)
    detailed_check "컨테이너 실행 테스트" \
        "timeout 30s docker run --rm cc-webapp-backend-test || test $? -eq 124"
        
    # 이미지 정리
    docker rmi cc-webapp-backend-test > /dev/null 2>&1
fi

echo -e "\n${BLUE}🔍 Phase 6: API 엔드포인트 검증${NC}"

# 8. Docker Compose 전체 실행 테스트
if command -v docker-compose &> /dev/null; then
    echo -e "\n${YELLOW}🔄 Docker Compose 전체 스택 테스트...${NC}"
    
    # 백그라운드에서 실행
    docker-compose up -d > /dev/null 2>&1
    
    # 30초 대기 후 헬스체크
    echo -e "${YELLOW}⏳ 서비스 시작 대기 (30초)...${NC}"
    sleep 30
    
    # 헬스체크 엔드포인트 테스트
    check_step "백엔드 헬스체크 응답" \
        "curl -f http://localhost:8000/health" \
        "백엔드 서비스가 정상 실행되지 않습니다"
    
    check_step "API 문서 페이지 접근" \
        "curl -f http://localhost:8000/docs" \
        "FastAPI 문서 페이지에 접근할 수 없습니다"
    
    # 서비스 정리
    docker-compose down > /dev/null 2>&1
else
    echo -e "${YELLOW}⚠️ docker-compose가 설치되지 않아 전체 스택 테스트 생략${NC}"
fi

echo -e "\n${BLUE}🔍 Phase 7: 테스트 실행 검증${NC}"

# 9. Pytest 테스트 실행
if [ -d "cc-webapp/backend/tests" ]; then
    echo -e "\n${YELLOW}🧪 Pytest 테스트 실행...${NC}"
    
    # Docker 컨테이너 내에서 테스트 실행
    detailed_check "Pytest 테스트 실행" \
        "docker-compose run --rm backend pytest tests/ -v"
else
    echo -e "${YELLOW}⚠️ tests 디렉토리가 없어 테스트 생략${NC}"
fi

# 최종 결과 리포트
echo -e "\n${BLUE}📊 최종 검증 결과${NC}"
echo -e "=================================="
echo -e "총 체크 항목: ${TOTAL_CHECKS}"
echo -e "${GREEN}통과: ${PASSED_CHECKS}${NC}"
echo -e "${RED}실패: ${FAILED_CHECKS}${NC}"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 모든 검증 통과! 백엔드 구조 표준화 성공!${NC}"
    echo -e "다음 단계: Phase 1.2 데이터베이스 스키마 작업을 시작하세요."
    exit 0
else
    echo -e "\n${RED}⚠️ ${FAILED_CHECKS}개 항목이 실패했습니다.${NC}"
    echo -e "${YELLOW}실패한 항목들을 수정한 후 다시 실행하세요.${NC}"
    
    # 일반적인 해결 방법 제시
    echo -e "\n${BLUE}💡 일반적인 해결 방법:${NC}"
    echo -e "1. Import 경로 수정:"
    echo -e "   ${YELLOW}find cc-webapp/backend -name '*.py' -exec sed -i 's/from backend\.app\./from app./g' {} +${NC}"
    echo -e "2. Docker 설정 확인:"
    echo -e "   ${YELLOW}docker-compose config${NC}"
    echo -e "3. 의존성 설치:"
    echo -e "   ${YELLOW}pip install -r cc-webapp/backend/requirements.txt${NC}"
    
    exit 1
fi
