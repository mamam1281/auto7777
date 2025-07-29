"""
테스트 코드 작성 가이드 문서
"""

# 카지노 클럽 웹앱 테스트 가이드

이 문서는 카지노 클럽 웹앱 백엔드의 테스트 코드 작성에 대한 가이드라인을 제공합니다.

## 테스트 구조

테스트 코드는 다음과 같이 구조화되어 있습니다:

```
tests/
├── conftest.py           # 공통 pytest 설정 및 fixture
├── unit/                 # 단위 테스트
│   ├── test_models.py    # 모델 단위 테스트
│   ├── test_services.py  # 서비스 단위 테스트
│   └── test_jwt_auth.py  # JWT 인증 단위 테스트
├── integration/          # 통합 테스트
│   ├── test_user_api.py  # 사용자 API 통합 테스트
│   └── test_game_api.py  # 게임 API 통합 테스트
└── e2e/                  # 엔드투엔드 테스트
```

## 테스트 실행 방법

### 모든 테스트 실행

```bash
pytest
```

### 특정 테스트 파일 실행

```bash
pytest tests/unit/test_jwt_auth.py
```

### 테스트 커버리지 확인

```bash
python run_test_coverage.py
```

## 테스트 작성 가이드라인

### 1. 단위 테스트 (Unit Tests)

단위 테스트는 개별 함수나 메서드의 기능을 검증합니다. 외부 의존성(데이터베이스, API 등)은 모킹(mocking)하여 격리된 환경에서 테스트합니다.

#### 예시: 서비스 계층 단위 테스트

```python
@pytest.fixture
def slot_service():
    # 레포지토리 모의객체 생성
    mock_user_repo = MagicMock()
    mock_action_repo = MagicMock()
    mock_reward_repo = MagicMock()
    mock_streak_repo = MagicMock()
    
    # 서비스 인스턴스 생성 및 반환
    return SlotMachineService(
        user_repo=mock_user_repo,
        action_repo=mock_action_repo,
        reward_repo=mock_reward_repo,
        streak_repo=mock_streak_repo,
        redis_client=MagicMock()
    )

def test_spin_insufficient_funds(slot_service):
    """잔액 부족 시 스핀 실패 테스트"""
    # 유저 목 설정
    mock_user = MagicMock()
    mock_user.regular_coins = 50
    
    # 스핀 요청 생성 (베팅 금액이 잔액보다 높음)
    spin_request = SlotSpinRequest(bet_amount=100)
    
    # 예외 발생 확인
    with pytest.raises(InsufficientFundsError):
        slot_service.spin(user=mock_user, spin_request=spin_request)
```

### 2. 통합 테스트 (Integration Tests)

통합 테스트는 여러 컴포넌트 간의 상호 작용을 검증합니다. 실제 데이터베이스 대신 테스트용 데이터베이스를 사용합니다.

#### 예시: API 통합 테스트

```python
@pytest.fixture
def client():
    """테스트 클라이언트 생성"""
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    """테스트용 사용자 생성 및 DB 저장"""
    user = User(
        nickname="testuser",
        email="test@example.com",
        hashed_password="$2b$12$abcdefghijklmnopqrstuvwxyzABCDEF",
        rank="STANDARD",
        regular_coins=1000,
        premium_coins=100,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_get_current_user_profile(client, test_user, auth_headers):
    """현재 사용자 프로필 조회 테스트"""
    # 인증된 사용자 프로필 조회
    response = client.get("/api/users/me", headers=auth_headers)
    
    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["nickname"] == test_user.nickname
    assert data["email"] == test_user.email
```

### 3. 비동기 코드 테스트

비동기 함수 테스트를 위해 `pytest.mark.asyncio` 데코레이터를 사용합니다.

```python
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """유효한 토큰으로 현재 사용자 가져오기 테스트"""
    # 테스트 코드...
```

### 4. 테스트 데이터베이스 설정

테스트는 실제 데이터베이스가 아닌 테스트용 데이터베이스(SQLite 메모리 DB 또는 테스트용 PostgreSQL)를 사용해야 합니다.

```python
# conftest.py
@pytest.fixture(scope="session")
def db_engine():
    """테스트용 데이터베이스 엔진 생성"""
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """테스트용 데이터베이스 세션 생성"""
    connection = db_engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
```

### 5. 모킹 가이드라인

외부 의존성은 `unittest.mock` 또는 `pytest-mock`을 사용하여 모킹합니다.

```python
@patch('app.services.slot_machine_service.random.choices')
def test_generate_spin_result(mock_choices, slot_service):
    # random.choices 목킹
    mock_choices.return_value = [Symbol.SEVEN, Symbol.SEVEN, Symbol.SEVEN]
    
    # 테스트 코드...
```

### 6. 파라미터화 테스트

유사한 테스트를 다양한 입력으로 실행하려면 파라미터화된 테스트를 사용합니다.

```python
@pytest.mark.parametrize("bet_amount,expected_error", [
    (0, ValueError),
    (-10, ValueError),
    (5000, InsufficientFundsError),
])
def test_invalid_bet_amounts(slot_service, bet_amount, expected_error):
    # 테스트 코드...
```

## 테스트 커버리지

코드 커버리지 목표:
- 서비스 계층: 90% 이상
- 모델 및 스키마: 80% 이상
- API 라우트: 80% 이상

커버리지 보고서는 `run_test_coverage.py` 스크립트를 실행하여 생성할 수 있습니다.

## 테스트 모범 사례

1. **각 테스트는 독립적이어야 함**: 테스트는 다른 테스트에 의존하지 않아야 합니다.
2. **명확한 테스트 이름 사용**: 테스트 이름은 무엇을 테스트하는지 명확히 나타내야 합니다.
3. **한 테스트당 하나의 개념 검증**: 각 테스트는 하나의 기능이나 동작만 검증해야 합니다.
4. **테스트 데이터 설정은 fixture로**: 반복적인 테스트 데이터 설정은 fixture로 분리합니다.
5. **예외 테스트도 포함**: 정상 동작뿐만 아니라 예외 상황도 테스트해야 합니다.

## 문제 해결

1. **모듈을 찾을 수 없는 경우**:
   - `PYTHONPATH`가 올바르게 설정되었는지 확인합니다.
   - 테스트를 프로젝트 루트에서 실행합니다.

2. **fixture를 찾을 수 없는 경우**:
   - `conftest.py`가 올바른 디렉토리에 있는지 확인합니다.
   - 중첩된 디렉토리 구조에서는 여러 `conftest.py`가 필요할 수 있습니다.

3. **비동기 테스트 실패**:
   - `pytest-asyncio` 플러그인이 설치되었는지 확인합니다.
   - `@pytest.mark.asyncio` 데코레이터를 사용했는지 확인합니다.
