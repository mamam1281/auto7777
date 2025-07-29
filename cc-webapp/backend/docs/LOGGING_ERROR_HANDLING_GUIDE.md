"""
로깅 및 에러 처리 가이드 문서
"""

# 카지노 클럽 웹앱 로깅 및 에러 처리 가이드

이 문서는 카지노 클럽 웹앱 백엔드의 로깅 및 에러 처리에 대한 가이드라인과 모범 사례를 제공합니다.

## 로깅 시스템

### 구조적 로깅

애플리케이션은 `structlog` 라이브러리를 사용하여 구조적 로깅을 구현합니다. 구조적 로깅은 일반 텍스트 메시지 대신 구조화된 데이터를 로깅하여 쿼리 및 분석을 용이하게 합니다.

### 로깅 레벨

로깅 레벨은 다음과 같이 사용됩니다:

- **DEBUG**: 개발 및 디버깅에 유용한 상세 정보
- **INFO**: 일반적인 애플리케이션 이벤트 및 흐름
- **WARNING**: 오류가 아닌 잠재적 문제 또는 이상 징후
- **ERROR**: 처리된 오류 (애플리케이션이 계속 실행될 수 있음)
- **CRITICAL**: 심각한 오류 (애플리케이션이 계속 실행될 수 없음)

### 컨텍스트 관리

로그 컨텍스트는 요청 전체에 걸쳐 유지됩니다. `LoggingContextMiddleware`는 각 요청에 대해 고유한 요청 ID를 생성하고 추가 컨텍스트 정보를 포함합니다.

```python
# 미들웨어를 통한 컨텍스트 추가
@app.middleware("http")
async def logging_context_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    context = {
        "request_id": request_id,
        "path": request.url.path,
        "method": request.method,
        "client_ip": request.client.host,
    }
    with structlog.contextvars.bound_contextvars(**context):
        # 요청 처리 시작 기록
        logger.info("Request started")
        start_time = time.time()
        try:
            response = await call_next(request)
            # 요청 처리 완료 기록
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                status_code=response.status_code,
                process_time=f"{process_time:.4f}s",
            )
            return response
        except Exception as e:
            # 요청 처리 중 오류 발생 기록
            process_time = time.time() - start_time
            logger.exception(
                "Request failed",
                error=str(e),
                process_time=f"{process_time:.4f}s",
            )
            raise
```

### 로그 포맷

개발 환경에서는 색상이 지정된 콘솔 로그가, 프로덕션 환경에서는 JSON 형식의 로그가 생성됩니다:

```json
{
    "timestamp": "2023-09-04T12:34:56.789Z",
    "level": "info",
    "event": "User logged in",
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "path": "/api/auth/login",
    "method": "POST",
    "user_id": 42,
    "client_ip": "192.168.1.1"
}
```

### 로깅 사용 예시

```python
# 로거 가져오기
import structlog
logger = structlog.get_logger()

# 기본 로깅
logger.info("Simple log message")

# 추가 컨텍스트와 함께 로깅
logger.info("User registered", user_id=user.id, email=user.email)

# 예외 로깅
try:
    # 코드 실행
except Exception as e:
    logger.exception("Failed to process payment", 
                     user_id=user.id, 
                     payment_id=payment.id,
                     error=str(e))
```

## 예외 처리 시스템

### 커스텀 예외 계층구조

애플리케이션은 다음과 같은 예외 계층구조를 사용합니다:

```
AppBaseException
├── AuthenticationException
│   ├── InvalidTokenError
│   └── ExpiredTokenError
├── AuthorizationException
│   └── InsufficientPermissionsError
├── ResourceException
│   ├── ResourceNotFoundException
│   └── ResourceAlreadyExistsException
├── ValidationException
│   └── InvalidParameterError
├── BusinessLogicException
│   ├── InsufficientFundsError
│   ├── InvalidGameStateError
│   └── RateLimitExceededError
└── ExternalServiceException
    └── DatabaseConnectionError
```

### 예외 처리 미들웨어

전역 예외 처리 미들웨어는 처리되지 않은 모든 예외를 잡아 일관된 오류 응답으로 변환합니다:

```python
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger = structlog.get_logger()
        # 예외 정보 로깅
        logger.error("Unhandled exception", 
                     error=str(e), 
                     error_type=type(e).__name__,
                     path=request.url.path)
        
        # 커스텀 예외인 경우
        if isinstance(e, AppBaseException):
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        
        # 기타 예외인 경우 500 Internal Server Error
        return JSONResponse(
            status_code=500,
            content={"detail": "내부 서버 오류가 발생했습니다"}
        )
```

### 예외 핸들러

특정 예외 유형에 대한 전용 핸들러를 등록할 수 있습니다:

```python
@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "field_errors": exc.field_errors
        }
    )
```

### 커스텀 예외 사용 예시

```python
# 커스텀 예외 정의
class InsufficientFundsError(BusinessLogicException):
    def __init__(self, required_amount: int, available_amount: int):
        super().__init__(
            status_code=400,
            detail=f"잔액이 부족합니다. 필요: {required_amount}, 보유: {available_amount}"
        )
        self.required_amount = required_amount
        self.available_amount = available_amount

# 예외 사용
def process_bet(user, bet_amount):
    if user.balance < bet_amount:
        raise InsufficientFundsError(
            required_amount=bet_amount,
            available_amount=user.balance
        )
```

## 모범 사례

### 로깅 모범 사례

1. **유용한 컨텍스트 포함**: 관련 ID, 사용자 정보, 요청 경로 등을 포함합니다.
2. **개인 정보 보호**: 비밀번호, 토큰, 개인 식별 정보 등은 로깅하지 않습니다.
3. **로그 수준 적절히 사용**: 모든 것을 INFO 레벨로 로깅하지 않고 적절한 레벨을 사용합니다.
4. **구조적 데이터 사용**: 문자열 포맷팅보다 구조적 데이터를 사용합니다.
5. **예외 스택 트레이스 포함**: 예외 로깅 시 스택 트레이스를 포함합니다.

```python
# 권장
logger.error("Payment failed", payment_id=payment.id, error=str(e))

# 권장하지 않음
logger.error(f"Payment {payment.id} failed: {e}")
```

### 예외 처리 모범 사례

1. **상세한 오류 메시지**: 오류의 원인과 해결 방법을 명확하게 설명합니다.
2. **적절한 HTTP 상태 코드 사용**: 각 예외에 가장 적합한 HTTP 상태 코드를 사용합니다.
3. **필요한 정보만 노출**: 클라이언트에게는 필요한 정보만 노출하고 내부 구현 세부사항은 숨깁니다.
4. **일관된 응답 구조**: 모든 오류 응답은 일관된 구조를 따릅니다.

```json
{
  "detail": "요청된 리소스를 찾을 수 없습니다",
  "code": "resource_not_found",
  "resource_type": "user",
  "resource_id": "123"
}
```

5. **예외는 예외적인 상황에만**: 일반적인 흐름 제어에는 예외를 사용하지 않습니다.

## 로깅 및 모니터링 통합

1. **로그 집계**: 로그는 ELK(Elasticsearch, Logstash, Kibana) 또는 유사한 시스템에 집계됩니다.
2. **알림 설정**: 특정 오류 발생 시 알림이 전송되도록 설정합니다.
3. **메트릭 수집**: 주요 성능 지표와 오류율을 모니터링합니다.

## 보안 고려사항

1. **민감한 정보 마스킹**: 비밀번호, 토큰 등 민감한 정보는 로그에서 마스킹합니다.
2. **사용자 식별 정보 제한**: 개인 식별 정보는 필요한 경우에만 최소한으로 로깅합니다.
3. **로그 액세스 제어**: 로그 접근은 인증된 관리자로 제한합니다.
