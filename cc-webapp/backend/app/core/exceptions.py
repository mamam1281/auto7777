"""
사용자 정의 예외 클래스 모듈
- 애플리케이션 전체에서 사용되는 표준화된 예외 클래스 정의
- HTTP 상태 코드와 오류 응답 형식 표준화
"""

from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, status


class AppBaseException(Exception):
    """
    애플리케이션 기본 예외 클래스
    모든 비즈니스 로직 예외의 기본 클래스
    """
    default_message = "An unexpected error occurred"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        detail: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    ):
        self.message = message or self.default_message
        self.status_code = status_code or self.status_code
        self.detail = detail
        
        super().__init__(self.message)
    
    def to_http_exception(self) -> HTTPException:
        """
        HTTPException으로 변환
        """
        return HTTPException(
            status_code=self.status_code,
            detail={
                "message": self.message,
                "detail": self.detail
            } if self.detail else self.message
        )


# 인증 관련 예외
class AuthenticationException(AppBaseException):
    """인증 실패 예외"""
    default_message = "Authentication failed"
    status_code = status.HTTP_401_UNAUTHORIZED


class NotAuthorizedException(AppBaseException):
    """권한 없음 예외"""
    default_message = "Not authorized to perform this action"
    status_code = status.HTTP_403_FORBIDDEN


class InvalidCredentialsException(AuthenticationException):
    """잘못된 인증 정보 예외"""
    default_message = "Invalid authentication credentials"


class InvalidTokenException(AuthenticationException):
    """잘못된 토큰 예외"""
    default_message = "Invalid or expired token"


class InviteCodeException(AuthenticationException):
    """초대 코드 관련 예외"""
    default_message = "Invalid invite code"


# 리소스 관련 예외
class ResourceNotFoundException(AppBaseException):
    """리소스를 찾을 수 없는 예외"""
    default_message = "Requested resource not found"
    status_code = status.HTTP_404_NOT_FOUND
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[Any] = None,
        message: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None
    ):
        resource_msg = f"{resource_type}"
        if resource_id is not None:
            resource_msg += f" with id '{resource_id}'"
        
        super().__init__(
            message=message or f"{resource_msg} not found",
            status_code=self.status_code,
            detail=detail or {"resource_type": resource_type, "resource_id": resource_id}
        )


class ResourceAlreadyExistsException(AppBaseException):
    """리소스가 이미 존재하는 예외"""
    default_message = "Resource already exists"
    status_code = status.HTTP_409_CONFLICT


class InvalidRequestException(AppBaseException):
    """잘못된 요청 예외"""
    default_message = "Invalid request data"
    status_code = status.HTTP_400_BAD_REQUEST


# 비즈니스 로직 예외
class BusinessRuleException(AppBaseException):
    """비즈니스 규칙 위반 예외"""
    default_message = "Business rule violation"
    status_code = status.HTTP_400_BAD_REQUEST


class InsufficientFundsException(BusinessRuleException):
    """잔액 부족 예외"""
    default_message = "Insufficient funds for this operation"


class DailyLimitExceededException(BusinessRuleException):
    """일일 한도 초과 예외"""
    default_message = "Daily limit exceeded for this operation"


class InvalidGameStateException(BusinessRuleException):
    """유효하지 않은 게임 상태 예외"""
    default_message = "Invalid game state for this operation"


# 시스템 관련 예외
class ExternalServiceException(AppBaseException):
    """외부 서비스 연동 실패 예외"""
    default_message = "External service error"
    status_code = status.HTTP_502_BAD_GATEWAY
    
    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message or f"Error communicating with {service_name}",
            status_code=status_code or self.status_code,
            detail=detail or {"service": service_name}
        )


class DatabaseException(AppBaseException):
    """데이터베이스 관련 예외"""
    default_message = "Database operation failed"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class CacheException(AppBaseException):
    """캐시 관련 예외"""
    default_message = "Cache operation failed"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
