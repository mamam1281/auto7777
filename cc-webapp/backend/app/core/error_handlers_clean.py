"""
Error handling and exception management for Casino-Club F2P backend
Clean English version to avoid Unicode issues
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

try:
    from .logging import log_error, get_logger
except ImportError:
    # Fallback if logging module is not available
    def log_error(exc, context=None):
        logging.error(f"Error: {exc}")
    
    def get_logger(name):
        return logging.getLogger(name)


# Custom Exception Classes
class CasinoClubException(Exception):
    """Base Casino Club exception class"""
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class GameServiceException(CasinoClubException):
    """Game service related exceptions"""
    def __init__(self, message: str, error_code: str = "GAME_ERROR"):
        super().__init__(message, error_code, 400)


class TokenServiceException(CasinoClubException):
    """Token service related exceptions"""
    def __init__(self, message: str, error_code: str = "TOKEN_ERROR"):
        super().__init__(message, error_code, 400)


class GachaServiceException(CasinoClubException):
    """Gacha service related exceptions"""
    def __init__(self, message: str, error_code: str = "GACHA_ERROR"):
        super().__init__(message, error_code, 400)


class UserServiceException(CasinoClubException):
    """User service related exceptions"""
    def __init__(self, message: str, error_code: str = "USER_ERROR"):
        super().__init__(message, error_code, 400)


class AuthenticationException(CasinoClubException):
    """Authentication related exceptions"""
    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        super().__init__(message, error_code, 401)


class AuthorizationException(CasinoClubException):
    """Authorization related exceptions"""
    def __init__(self, message: str, error_code: str = "PERMISSION_ERROR"):
        super().__init__(message, error_code, 403)


class InsufficientTokensException(TokenServiceException):
    """Insufficient tokens exception"""
    def __init__(self, required: int, available: int):
        message = f"Insufficient tokens. Required: {required}, Available: {available}"
        super().__init__(message, "INSUFFICIENT_TOKENS")


class InvalidGachaPullException(GachaServiceException):
    """Invalid gacha pull exception"""
    def __init__(self, reason: str):
        message = f"Invalid gacha pull: {reason}"
        super().__init__(message, "INVALID_GACHA_PULL")


# Error Handling Middleware
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware
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
        """Handle exceptions and create appropriate responses"""
        
        # CasinoClub custom exception handling
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
        
        # HTTP exception handling
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
        
        # Validation error handling
        elif isinstance(exc, RequestValidationError):
            log_error(exc, {
                "request_path": str(request.url),
                "request_method": request.method,
                "validation_errors": exc.errors()
            })
            
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": "Request data validation failed.",
                    "error_code": "VALIDATION_ERROR",
                    "errors": exc.errors()
                }
            )
        
        # General exception handling
        else:
            log_error(exc, {
                "request_path": str(request.url),
                "request_method": request.method,
                "traceback": traceback.format_exc()
            })
            
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "An internal server error occurred.",
                    "error_code": "INTERNAL_ERROR"
                }
            )


# Exception Handler Functions
async def casino_club_exception_handler(request: Request, exc: CasinoClubException):
    """CasinoClub custom exception handler"""
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
    """HTTP exception handler"""
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
    """Validation exception handler"""
    log_error(exc, {
        "request_path": str(request.url),
        "request_method": request.method,
        "validation_errors": exc.errors()
    })
    
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request data validation failed.",
            "error_code": "VALIDATION_ERROR",
            "errors": exc.errors()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    log_error(exc, {
        "request_path": str(request.url),
        "request_method": request.method,
        "traceback": traceback.format_exc()
    })
    
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred.",
            "error_code": "INTERNAL_ERROR"
        }
    )


def add_exception_handlers(app):
    """Add exception handlers to FastAPI app"""
    app.add_exception_handler(CasinoClubException, casino_club_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)


# Middleware alias (for backward compatibility)
error_handling_middleware = ErrorHandlingMiddleware


# Convenience functions
def raise_token_error(message: str, error_code: str = "TOKEN_ERROR"):
    """Raise token related error"""
    raise TokenServiceException(message, error_code)


def raise_game_error(message: str, error_code: str = "GAME_ERROR"):
    """Raise game related error"""
    raise GameServiceException(message, error_code)


def raise_gacha_error(message: str, error_code: str = "GACHA_ERROR"):
    """Raise gacha related error"""
    raise GachaServiceException(message, error_code)


def raise_user_error(message: str, error_code: str = "USER_ERROR"):
    """Raise user related error"""
    raise UserServiceException(message, error_code)


def raise_auth_error(message: str = "Authentication required"):
    """Raise authentication error"""
    raise AuthenticationException(message)


def raise_permission_error(message: str = "Permission denied"):
    """Raise permission error"""
    raise AuthorizationException(message)


# Validation functions
def validate_token_amount(required: int, available: int):
    """Validate token amount"""
    if available < required:
        raise InsufficientTokensException(required, available)


def validate_user_permission(user_rank: str, required_rank: str):
    """Validate user permission"""
    rank_hierarchy = {"STANDARD": 1, "VIP": 2, "PREMIUM": 3}
    user_level = rank_hierarchy.get(user_rank, 0)
    required_level = rank_hierarchy.get(required_rank, 1)
    
    if user_level < required_level:
        raise AuthorizationException(f"{required_rank} rank or higher required. Current rank: {user_rank}")


# Data conversion utility functions
def safe_int_conversion(value: Any, default: int = 0, field_name: str = "number") -> int:
    """Safe integer conversion"""
    try:
        return int(value)
    except (ValueError, TypeError):
        raise CasinoClubException(
            f"{field_name} must be a valid integer format.",
            "INVALID_NUMBER_FORMAT"
        )
    except Exception:
        return default


def safe_float_conversion(value: Any, default: float = 0.0, field_name: str = "number") -> float:
    """Safe float conversion"""
    try:
        return float(value)
    except (ValueError, TypeError):
        raise CasinoClubException(
            f"{field_name} must be a valid number format.",
            "INVALID_NUMBER_FORMAT"
        )
    except Exception:
        return default
