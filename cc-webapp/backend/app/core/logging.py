"""
구조화된 로깅 설정 모듈
- structlog를 사용하여 JSON 형식의 구조화된 로그 생성
- 개발/운영 환경에 따른 로깅 설정
- 컨텍스트 정보 추가 지원
"""

import logging
import sys
import time
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor

# 기본 로그 레벨 설정
DEFAULT_LOG_LEVEL = logging.INFO

# 로그 프로세서 설정
processors: list[Processor] = [
    # 현재 로거의 이름을 로그에 추가
    structlog.stdlib.add_logger_name,
    # 로그 이벤트에 타임스탬프 추가
    structlog.processors.TimeStamper(fmt="iso"),
    # 로그 이벤트에서 예외 발생 시 추적정보 추가
    structlog.processors.ExceptionPrettyPrinter(),
    # 로그 컨텍스트를 구조화된 dict로 합침
    structlog.processors.StackInfoRenderer(),
    # 로그 레벨을 문자열로 추가
    structlog.stdlib.add_log_level,
    # stdlib의 로그 레벨에 따라 이벤트 필터링
    structlog.stdlib.filter_by_level,
]

# 개발 환경용 프로세서 (보기 좋게 출력)
dev_processors = processors + [
    # 개발 환경에서는 컬러 출력
    structlog.dev.ConsoleRenderer(colors=True)
]

# 운영 환경용 프로세서 (JSON 형식)
prod_processors = processors + [
    # 운영 환경에서는 JSON 형식으로 출력
    structlog.processors.dict_tracebacks,
    structlog.processors.JSONRenderer()
]

def setup_logging(
    level: int = DEFAULT_LOG_LEVEL,
    development_mode: bool = False,
    log_file: Optional[str] = None
) -> None:
    """
    애플리케이션 로깅 설정
    
    Args:
        level: 로그 레벨
        development_mode: 개발 모드 여부 (True면 컬러 콘솔 출력, False면 JSON 형식)
        log_file: 로그 파일 경로 (지정 시 파일에도 로깅)
    """
    # 선택된 프로세서
    selected_processors = dev_processors if development_mode else prod_processors
    
    # structlog 설정
    structlog.configure(
        processors=selected_processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # 표준 로깅 설정
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # 파일 로깅 추가 (지정된 경우)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
    
    # 루트 로거 설정
    logging.basicConfig(
        format="%(message)s",
        level=level,
        handlers=handlers,
    )
    
    # 다른 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    

def get_logger(name: str = "cc-webapp") -> structlog.stdlib.BoundLogger:
    """
    구조화된 로거 인스턴스 반환
    
    Args:
        name: 로거 이름
        
    Returns:
        structlog.stdlib.BoundLogger: 구조화된 로거
    """
    return structlog.get_logger(name)


class LoggingContextMiddleware:
    """
    FastAPI 요청에 로깅 컨텍스트를 추가하는 미들웨어
    """
    async def __call__(self, request, call_next):
        # 요청 시작 시간
        start_time = time.time()
        
        # 요청 ID 생성
        request_id = str(id(request))[:16]
        
        # 로깅 컨텍스트 설정
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if hasattr(request, 'client') and request.client else None,
        )
        
        # 응답 처리
        response = await call_next(request)
        
        # 응답 시간 계산 및 로깅
        process_time = time.time() - start_time
        structlog.contextvars.bind_contextvars(
            status_code=response.status_code,
            process_time=f"{process_time:.4f}s"
        )
        
        # 컨텍스트 정보로 로그 메시지 생성
        logger = get_logger("http")
        logger.info(
            "HTTP Request",
            response_time=process_time,
            status=response.status_code,
        )
        
        return response


# 간편하게 로거를 가져오기 위한 전역 변수
logger = get_logger()
