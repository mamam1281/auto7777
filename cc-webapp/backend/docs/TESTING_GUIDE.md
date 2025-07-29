# 🧪 Casino Club 백엔드 테스트 가이드

## 📊 현재 테스트 상태 (2025-07-30)

### 커버리지 현황
- **전체 커버리지**: 41% (목표: 80%)
- **테스트 파일**: 280+ 개
- **환경**: Python 3.11.9 (SQLAlchemy 호환성)

### 성공한 부분 ✅
```
app/models/               90%+   (완료)
app/schemas/             100%    (완료) 
app/core/                70%+    (기본 완료)
app/repositories/        44%     (부분 완료)
```

### 개선 필요 부분 ⚠️
```
app/services/            20-40%  (핵심 비즈니스 로직)
app/routers/             30-60%  (API 엔드포인트)
app/utils/               20-30%  (유틸리티 함수들)
```

## 🚀 테스트 실행 방법

### 1. 환경 설정
```bash
# Docker 실행 (필수)
cd c:\Users\bdbd\dd\auto7777\cc-webapp
docker-compose up -d

# Python 3.11 환경 활성화
cd backend
.venv311\Scripts\activate
```

### 2. 전체 테스트 실행
```bash
# 커버리지와 함께 전체 테스트
python -m pytest -v --cov=app --cov-report=term-missing --cov-report=html:coverage_html --cov-report=xml:coverage.xml tests/

# 빠른 테스트 (오류만 표시)
python -m pytest --tb=no --disable-warnings -q

# 특정 파일만 테스트
python -m pytest tests/test_game_service.py -v
```

### 3. 커버리지 리포트 확인
```bash
# HTML 리포트 열기
start coverage_html/index.html

# 터미널에서 상세 리포트
python -m pytest --cov=app --cov-report=term-missing tests/
```

## 🏗️ 테스트 구조

### 디렉토리 구조
```
tests/
├── integration/          # 통합 테스트
│   ├── test_game_api.py
│   └── test_user_api.py
├── services/             # 서비스 레이어 테스트
│   └── test_cj_ai_service.py
├── unit/                 # 단위 테스트
│   ├── test_jwt_auth.py
│   └── test_quick_health.py
├── utils/                # 유틸리티 테스트
│   └── test_reward_utils.py
├── routers/              # 라우터 테스트
│   └── test_doc_titles.py
└── test_*.py            # 메인 테스트 파일들
```

### 테스트 타입별 현황
- **단위 테스트**: 120+ (서비스, 유틸리티)
- **통합 테스트**: 40+ (API 엔드포인트)  
- **기능 테스트**: 80+ (게임 로직, 인증)
- **성능 테스트**: 10+ (확률, 대량 데이터)

## 🎯 우선순위 개선 계획

### Phase 1: 핵심 서비스 테스트 강화 (41% → 60%)
```
1. game_service.py        59% → 85%
2. gacha_service.py       18% → 80%
3. token_service.py       16% → 80%
4. user_service.py        33% → 80%
```

### Phase 2: API 라우터 테스트 (60% → 75%)
```
1. games.py              60% → 85%
2. auth.py               45% → 80%
3. gacha.py              50% → 80%
4. rewards.py            66% → 85%
```

### Phase 3: 유틸리티 및 마이너 (75% → 80%+)
```
1. utils/ 전체           20-30% → 70%+
2. routers/ 나머지       30-60% → 75%+
3. 에러 핸들링 강화
```

## 🔧 알려진 이슈와 해결 방법

### 1. Python 버전 호환성
```bash
# ❌ Python 3.13에서 SQLAlchemy 오류
# AssertionError: Class <SQLCoreOperations> inherits TypingOnly

# ✅ 해결 방법: Python 3.11 사용
.venv311\Scripts\activate
```

### 2. TestClient 초기화 오류
```python
# ❌ 이전 방식
client = TestClient(app=app)

# ✅ 수정된 방식  
client = TestClient(app)
```

### 3. Import 오류
```python
# 누락된 모듈들은 try/except로 처리
try:
    from app.services.missing_service import Service
except ImportError:
    pytest.skip("Service module not available")
```

## 📈 커버리지 향상 전략

### 1. 서비스 레이어 우선
- 비즈니스 로직의 핵심이므로 최우선
- Mock을 활용한 의존성 분리
- Edge case 시나리오 추가

### 2. API 엔드포인트 테스트
- FastAPI TestClient 활용
- 인증/권한 시나리오
- 입력 검증 및 에러 처리

### 3. 유틸리티 함수 완성
- 순수 함수들이므로 테스트하기 쉬움
- 경계값 테스트 추가
- 예외 상황 처리 검증

## 🛠️ 테스트 작성 가이드라인

### 1. 명명 규칙
```python
def test_service_action_expected_result():
    """설명: 서비스의 특정 액션이 예상 결과를 반환하는지 테스트"""

def test_api_endpoint_with_valid_input():
    """설명: API 엔드포인트가 유효한 입력으로 정상 동작하는지 테스트"""
```

### 2. Mock 사용
```python
@patch('app.services.game_service.repository')
def test_game_service_with_mock(mock_repo):
    mock_repo.get_user.return_value = test_user
    # 테스트 로직
```

### 3. 픽스처 활용
```python
@pytest.fixture
def test_user(db_session):
    user = User(nickname="test", rank="VIP")
    db_session.add(user)
    db_session.commit()
    return user
```

## 📋 배포 전 체크리스트

### 필수 검증 항목
- [ ] 전체 테스트 통과율 > 95%
- [ ] 코드 커버리지 > 80%
- [ ] Docker 환경에서 정상 실행
- [ ] API 엔드포인트 200/401/404 응답 확인
- [ ] 데이터베이스 마이그레이션 정상

### 성능 검증
- [ ] 가챠 확률 분포 검증 (10,000회)
- [ ] 동시 사용자 100명 시뮬레이션
- [ ] 메모리 사용량 < 512MB
- [ ] 응답 시간 < 200ms (평균)

## 📞 문제 해결 및 지원

### 자주 발생하는 문제
1. **SQLAlchemy 오류** → Python 3.11 사용
2. **Import 오류** → 모듈 경로 확인
3. **Docker 연결 실패** → 컨테이너 상태 확인
4. **테스트 DB 오류** → 마이그레이션 실행

### 추가 정보
- 테스트 관련 이슈: GitHub Issues
- 커버리지 리포트: `coverage_html/index.html`
- CI/CD 로그: GitHub Actions

---

**마지막 업데이트**: 2025-07-30  
**현재 커버리지**: 41% (목표: 80%)  
**테스트 환경**: Python 3.11.9 + Docker
