"""
전역 예외 처리 핸들러
- 모든 예외를 일관된 형식으로 처리
- 예외 유형에 따른 적절한 HTTP 응답 제공
- 구조화된 로깅 통합
"""

import traceback
from typing import Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppBaseException
from app.core.logging import get_logger

# 로거 설정
logger = get_logger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    """
    FastAPI 앱에 전역 예외 핸들러 등록
    """
    
    # 사용자 정의 기본 예외
    @app.exception_handler(AppBaseException)
    async def app_base_exception_handler(request: Request, exc: AppBaseException) -> Response:
        logger.warning(
            "Application exception",
            exc_info=str(exc),
            status_code=exc.status_code,
            path=request.url.path,
            exception_type=exc.__class__.__name__
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "detail": exc.detail if exc.detail else None,
                "code": exc.__class__.__name__
            }
        )
    
    # 요청 유효성 검증 오류 (FastAPI)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
        logger.warning(
            "Request validation error",
            path=request.url.path,
            errors=[{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Request validation error",
                "detail": exc.errors(),
                "code": "RequestValidationError"
            }
        )
    
    # Pydantic 유효성 검증 오류
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> Response:
        logger.warning(
            "Data validation error",
            path=request.url.path,
            errors=exc.errors()
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Data validation error",
                "detail": exc.errors(),
                "code": "ValidationError"
            }
        )
    
    # SQLAlchemy 예외
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> Response:
        logger.error(
            "Database error",
            exc_info=str(exc),
            path=request.url.path,
            exception_type=exc.__class__.__name__
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Database operation failed",
                "code": "DatabaseError"
            }
        )
    
    # 기타 모든 예외
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> Response:
        logger.error(
            "Unhandled exception",
            exc_info=str(exc),
            traceback=traceback.format_exc(),
            path=request.url.path,
            exception_type=exc.__class__.__name__
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error occurred",
                "code": "InternalServerError"
            }
        )


def error_handling_middleware(app: FastAPI) -> Callable:
    """
    에러 처리 미들웨어 (요청/응답 로깅 포함)
    """
    @app.middleware("http")
    async def middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            # 미리 등록된 예외 핸들러에서 처리되지 않은 예외만 여기서 처리
            if isinstance(exc, AppBaseException):
                return JSONResponse(
                    status_code=exc.status_code,
                    content={
                        "message": exc.message,
                        "detail": exc.detail if hasattr(exc, "detail") and exc.detail else None,
                        "code": exc.__class__.__name__
                    }
                )
            
            logger.error(
                "Unhandled exception in middleware",
                exc_info=str(exc),
                traceback=traceback.format_exc(),
                path=request.url.path,
                method=request.method
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "An unexpected error occurred",
                    "code": "InternalServerError"
                }
            )
    
    return middleware
