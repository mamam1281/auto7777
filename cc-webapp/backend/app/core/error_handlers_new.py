"""
에러 핸들링 및 예외 처리
Casino-Club F2P 백엔드 에러 관리 시스템
"""
import logging
import traceback
from typing import Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY
import json

from .logging import log_error, get_logger

# 커스텀 예외 클래스들
class CasinoClubException(Exception):
    """Casino Club 기본 예외 클래스"""
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class GameServiceException(CasinoClubException):
    """게임 서비스 관련 예외"""
    def __init__(self, message: str, error_code: str = "GAME_ERROR"):
        super().__init__(message, error_code, 400)


class TokenServiceException(CasinoClubException):
    """토큰 서비스 관련 예외"""
    def __init__(self, message: str, error_code: str = "TOKEN_ERROR"):
        super().__init__(message, error_code, 400)


class GachaServiceException(CasinoClubException):
    """가챠 서비스 관련 예외"""
    def __init__(self, message: str, error_code: str = "GACHA_ERROR"):
        super().__init__(message, error_code, 400)


class UserServiceException(CasinoClubException):
    """사용자 서비스 관련 예외"""
    def __init__(self, message: str, error_code: str = "USER_ERROR"):
        super().__init__(message, error_code, 400)


class AuthenticationException(CasinoClubException):
    """인증 관련 예외"""
    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        super().__init__(message, error_code, 401)


class AuthorizationException(CasinoClubException):
    """권한 관련 예외"""
    def __init__(self, message: str, error_code: str = "PERMISSION_ERROR"):
        super().__init__(message, error_code, 403)


class InsufficientTokensException(TokenServiceException):
    """토큰 부족 예외"""
    def __init__(self, required: int, available: int):
        message = f"토큰이 부족합니다. 필요: {required}, 보유: {available}"
        super().__init__(message, "INSUFFICIENT_TOKENS")


class InvalidGachaPullException(GachaServiceException):
    """잘못된 가챠 뽑기 예외"""
    def __init__(self, reason: str):
        message = f"가챠 뽑기 실패: {reason}"
        super().__init__(message, "INVALID_GACHA_PULL")


# 에러 핸들링 미들웨어
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    전역 에러 핸들링 미들웨어
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("error_handler")

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            return await self.handle_exception(request, e)

    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """예외 처리 및 응답 생성"""
        
        # CasinoClub 커스텀 예외 처리
        if isinstance(exc, CasinoClubException):
            log_error(exc, {
                "request_path": str(request.url),
                "request_method": request.method,
                "error_code": exc.error_code
            })
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": exc.message,
                    "error_code": exc.error_code
                }
            )
        
        # HTTP 예외 처리
        elif isinstance(exc, HTTPException):
            log_error(exc, {
                "request_path": str(request.url),
                "request_method": request.method,
                "status_code": exc.status_code
            })
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": exc.detail,
                    "error_code": "HTTP_ERROR"
                }
            )
        
        # 밸리데이션 에러 처리
        elif isinstance(exc, RequestValidationError):
            log_error(exc, {
                "request_path": str(request.url),
                "request_method": request.method,
                "validation_errors": exc.errors()
            })
            
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": "요청 데이터가 올바르지 않습니다.",
                    "error_code": "VALIDATION_ERROR",
                    "errors": exc.errors()
                }
            )
        
        # 일반 예외 처리
        else:
            log_error(exc, {
                "request_path": str(request.url),
                "request_method": request.method,
                "traceback": traceback.format_exc()
            })
            
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "서버 내부 오류가 발생했습니다.",
                    "error_code": "INTERNAL_ERROR"
                }
            )


# 에러 핸들러 함수들
async def casino_club_exception_handler(request: Request, exc: CasinoClubException):
    """CasinoClub 커스텀 예외 핸들러"""
    log_error(exc, {
        "request_path": str(request.url),
        "request_method": request.method,
        "error_code": exc.error_code
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 핸들러"""
    log_error(exc, {
        "request_path": str(request.url),
        "request_method": request.method,
        "status_code": exc.status_code
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "HTTP_ERROR"
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """밸리데이션 예외 핸들러"""
    log_error(exc, {
        "request_path": str(request.url),
        "request_method": request.method,
        "validation_errors": exc.errors()
    })
    
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "요청 데이터가 올바르지 않습니다.",
            "error_code": "VALIDATION_ERROR",
            "errors": exc.errors()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러"""
    log_error(exc, {
        "request_path": str(request.url),
        "request_method": request.method,
        "traceback": traceback.format_exc()
    })
    
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "서버 내부 오류가 발생했습니다.",
            "error_code": "INTERNAL_ERROR"
        }
    )


def add_exception_handlers(app):
    """FastAPI 앱에 예외 핸들러 추가"""
    app.add_exception_handler(CasinoClubException, casino_club_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)


# 미들웨어 별칭 (하위 호환)
error_handling_middleware = ErrorHandlingMiddleware


# 편의 함수들
def raise_token_error(message: str, error_code: str = "TOKEN_ERROR"):
    """토큰 관련 에러 발생"""
    raise TokenServiceException(message, error_code)


def raise_game_error(message: str, error_code: str = "GAME_ERROR"):
    """게임 관련 에러 발생"""
    raise GameServiceException(message, error_code)


def raise_gacha_error(message: str, error_code: str = "GACHA_ERROR"):
    """가챠 관련 에러 발생"""
    raise GachaServiceException(message, error_code)


def raise_user_error(message: str, error_code: str = "USER_ERROR"):
    """사용자 관련 에러 발생"""
    raise UserServiceException(message, error_code)


def raise_auth_error(message: str = "인증이 필요합니다"):
    """인증 에러 발생"""
    raise AuthenticationException(message)


def raise_permission_error(message: str = "권한이 없습니다."):
    """권한 에러 발생"""
    raise AuthorizationException(message)


# 검증 함수들
def validate_token_amount(required: int, available: int):
    """토큰 양량 검증"""
    if available < required:
        raise InsufficientTokensException(required, available)


def validate_user_permission(user_rank: str, required_rank: str):
    """사용자 권한 검증"""
    rank_hierarchy = {"STANDARD": 1, "VIP": 2, "PREMIUM": 3}
    user_level = rank_hierarchy.get(user_rank, 0)
    required_level = rank_hierarchy.get(required_rank, 1)
    
    if user_level < required_level:
        raise AuthorizationException(f"{required_rank} 이상의 등급이 필요합니다. 현재 등급: {user_rank}")


# 데이터 변환 함수들
def safe_int_conversion(value: Any, default: int = 0, field_name: str = "숫자") -> int:
    """안전한 정수 변환"""
    try:
        return int(value)
    except (ValueError, TypeError):
        raise CasinoClubException(
            f"{field_name}이 올바른 숫자 형식이 아닙니다.",
            "INVALID_NUMBER_FORMAT"
        )
    except Exception:
        return default


def safe_float_conversion(value: Any, default: float = 0.0, field_name: str = "숫자") -> float:
    """안전한 실수 변환"""
    try:
        return float(value)
    except (ValueError, TypeError):
        raise CasinoClubException(
            f"{field_name}이 올바른 숫자 형식이 아닙니다.",
            "INVALID_NUMBER_FORMAT"
        )
    except Exception:
        return default
