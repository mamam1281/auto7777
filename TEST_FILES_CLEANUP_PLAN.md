# 📋 테스트 및 분석 파일 정리 계획

## 🔍 분석 대상 파일들

### 📁 루트 디렉토리 파일들
1. **test_api_integration.py** (113 lines) - API 통합 테스트 스크립트
2. **test_profile.sh** (빈 파일) - 프로파일 테스트 스크립트
3. **test-edit.tsx** (51 lines) - React 테스트 컴포넌트
4. **test.db** (299KB) - SQLite 테스트 데이터베이스
5. **VIRTUAL_ENVIRONMENT_ANALYSIS.md** - 가상환경 분석 보고서

## 📊 분석 결과

### ✅ 유용한 파일 - 적절한 위치로 이동

#### 1. test_api_integration.py
- **현재 위치**: 루트 디렉토리
- **평가**: 유용한 API 테스트 도구
- **목적지**: `cc-webapp/backend/tests/integration/`
- **이유**: 백엔드 통합 테스트로 분류, 개발 중 활용 가능

#### 2. test-edit.tsx
- **현재 위치**: 루트 디렉토리  
- **평가**: React 컴포넌트 테스트 예제
- **목적지**: `cc-webapp/frontend/src/components/test/`
- **이유**: 프론트엔드 테스트 컴포넌트로 분류

#### 3. VIRTUAL_ENVIRONMENT_ANALYSIS.md
- **현재 위치**: 루트 디렉토리
- **평가**: 중요한 분석 문서
- **목적지**: `docs/analysis/`
- **이유**: 프로젝트 분석 문서로 체계적 관리

### 🗃️ 아카이브할 파일

#### 4. test_profile.sh
- **현재 위치**: 루트 디렉토리
- **평가**: 빈 파일, 사용되지 않음
- **목적지**: `archive/empty_files/`
- **이유**: 내용이 없어 실용성 없음

#### 5. test.db
- **현재 위치**: 루트 디렉토리
- **평가**: SQLite 테스트 DB (299KB)
- **목적지**: `archive/sqlite_legacy/`
- **이유**: PostgreSQL로 전환 완료, SQLite는 레거시

## 🎯 실행 계획

### Phase 1: 디렉토리 구조 확장
```
cc-webapp/
  backend/
    tests/
      integration/              # 백엔드 통합 테스트
  frontend/
    src/
      components/
        test/                   # 프론트엔드 테스트 컴포넌트
docs/
  analysis/                     # 프로젝트 분석 문서
archive/
  empty_files/                  # 빈 파일들
  sqlite_legacy/                # SQLite 관련 레거시
```

### Phase 2: 파일 이동 작업
1. **유용한 파일들 이동**
   - test_api_integration.py → backend/tests/integration/
   - test-edit.tsx → frontend/src/components/test/
   - VIRTUAL_ENVIRONMENT_ANALYSIS.md → docs/analysis/

2. **아카이브 파일들 이동**
   - test_profile.sh → archive/empty_files/
   - test.db → archive/sqlite_legacy/

### Phase 3: 파일 최신화
- API 테스트 스크립트: 현재 엔드포인트에 맞게 업데이트
- React 컴포넌트: TypeScript 타입 완성도 향상
- 분석 문서: 현재 프로젝트 상태 반영

## 💡 기대 효과

✅ **정리된 테스트 환경**
- 백엔드/프론트엔드 테스트 파일 분리
- 통합 테스트 도구 체계적 관리

✅ **문서화 개선**
- 분석 문서들의 체계적 보관
- 프로젝트 히스토리 추적 가능

✅ **레거시 정리**
- SQLite 관련 파일들 아카이브
- 불필요한 파일들 제거

---
*Repository 패턴 구축과 연계한 테스트 환경 정리*
