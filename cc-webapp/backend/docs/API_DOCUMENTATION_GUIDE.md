"""
카지노 클럽 웹앱 백엔드 API 문서화 가이드
"""

# 표준 OpenAPI 문서화 가이드

## API 문서화 표준

이 문서는 카지노 클럽 웹앱 백엔드 API의 문서화 표준을 정의합니다. 모든 API 엔드포인트는 이 가이드라인에 따라 문서화되어야 합니다.

### 1. 일반 원칙

- 모든 API 엔드포인트는 명확한 요약과 상세 설명을 포함해야 합니다.
- 파라미터, 요청 본문, 응답 형식은 상세히 문서화해야 합니다.
- 가능한 모든 응답 코드와 오류 상황을 명시해야 합니다.
- 예제 요청/응답을 제공해야 합니다.

### 2. FastAPI 데코레이터 사용 가이드

```python
@router.post(
    "/endpoint",
    summary="API 엔드포인트 요약",
    description="API 엔드포인트에 대한 상세한 설명. 마크다운 형식을 지원합니다.",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "인증되지 않음"},
        403: {"description": "권한 없음"},
        404: {"description": "리소스를 찾을 수 없음"},
        422: {"description": "입력값 검증 오류"},
    },
    tags=["카테고리"],
)
```

### 3. API 태그 구조

API는 다음 태그 카테고리로 구성됩니다:

- **users**: 사용자 관리 및 인증
- **games**: 게임 및 베팅 관련 기능
- **rewards**: 보상 및 이벤트
- **admin**: 관리자용 기능

### 4. Pydantic 모델 문서화

```python
class UserCreate(BaseModel):
    """사용자 생성 요청 모델."""
    
    nickname: str = Field(..., description="사용자 닉네임")
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호", min_length=8)
    
    class Config:
        schema_extra = {
            "example": {
                "nickname": "gamer123",
                "email": "user@example.com",
                "password": "securePassword123"
            }
        }
```

### 5. 엔드포인트 설명 샘플

#### 사용자 인증

```python
@router.post(
    "/token",
    summary="액세스 토큰 발급",
    description="""
    사용자 이메일과 비밀번호를 검증하고 액세스 토큰을 발급합니다.
    
    - **토큰 유효기간**: 액세스 토큰 30분, 리프레시 토큰 7일
    - **사용 방법**: 요청 헤더에 `Authorization: Bearer {token}` 형식으로 포함
    """,
    response_model=TokenResponse,
    responses={
        401: {"description": "잘못된 인증 정보"}
    },
    tags=["users"]
)
```

#### 게임 API

```python
@router.post(
    "/games/slots/spin",
    summary="슬롯 머신 스핀",
    description="""
    슬롯 머신을 회전하고 결과를 반환합니다.
    
    - **최소 베팅 금액**: 10 코인
    - **최대 베팅 금액**: 1000 코인
    - **잭팟 확률**: 약 0.1%
    """,
    response_model=SlotSpinResult,
    responses={
        400: {"description": "잘못된 요청"},
        402: {"description": "잔액 부족"},
        401: {"description": "인증되지 않음"}
    },
    tags=["games"]
)
```

### 6. API 버전 관리

모든 API 경로는 버전 접두사를 포함해야 합니다:

```
/api/v1/users/
/api/v1/games/
```

### 7. 보안 스키마

모든 인증이 필요한 API는 보안 요구사항을 명시해야 합니다:

```python
security=[{"bearerAuth": []}]
```

## 표준 문서화 템플릿

### 엔드포인트 템플릿

```python
@router.method(
    "/path",
    summary="간단한 요약",
    description="""
    상세한 설명.
    
    - **중요 정보**: 핵심 정보 강조
    - **제한사항**: 사용 제한 사항
    - **참고사항**: 추가 정보
    """,
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "잘못된 요청"},
        401: {"description": "인증되지 않음"},
        # 추가 응답 코드
    },
    tags=["카테고리"],
    deprecated=False,  # 필요한 경우 지원 중단 표시
)
```

### 모델 템플릿

```python
class ModelName(BaseModel):
    """모델 목적 설명."""
    
    field1: str = Field(..., description="필드 설명")
    field2: int = Field(..., description="필드 설명", ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "field1": "예시값",
                "field2": 123
            }
        }
```

## API 문서 페이지 접근 방법

완성된 API 문서는 다음 URL로 접근할 수 있습니다:

- **Swagger UI**: `/docs` - 대화형 API 테스트 및 문서
- **ReDoc**: `/redoc` - 읽기 쉬운 API 문서화
- **OpenAPI JSON**: `/api/v1/openapi.json` - 원시 OpenAPI 스키마
