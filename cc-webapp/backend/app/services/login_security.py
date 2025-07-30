"""
로그인 시도 제한 및 보안 서비스
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user_session import LoginAttempt
from ..models.user import User


class LoginSecurityService:
    def __init__(self):
        self.max_attempts_per_ip = 10  # IP당 최대 시도 횟수 (1시간)
        self.max_attempts_per_account = 5  # 계정당 최대 시도 횟수 (1시간)
        self.lockout_duration_minutes = 60  # 계정 잠금 시간 (분)
        self.attempt_window_minutes = 60  # 시도 카운트 윈도우 (분)
    
    def record_login_attempt(self, site_id: str, ip_address: str, success: bool, 
                           failure_reason: Optional[str], user_agent: Optional[str], db: Session):
        """로그인 시도 기록"""
        attempt = LoginAttempt(
            site_id=site_id,
            ip_address=ip_address,
            success=success,
            failure_reason=failure_reason,
            user_agent=user_agent
        )
        db.add(attempt)
        db.commit()
    
    def check_ip_attempts(self, ip_address: str, db: Session) -> bool:
        """IP 주소별 로그인 시도 횟수 확인"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.attempt_window_minutes)
        
        failed_attempts = db.query(LoginAttempt).filter(
            LoginAttempt.ip_address == ip_address,
            LoginAttempt.success == False,
            LoginAttempt.attempted_at >= cutoff_time
        ).count()
        
        return failed_attempts < self.max_attempts_per_ip
    
    def check_account_attempts(self, site_id: str, db: Session) -> bool:
        """계정별 로그인 시도 횟수 확인"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.attempt_window_minutes)
        
        failed_attempts = db.query(LoginAttempt).filter(
            LoginAttempt.site_id == site_id,
            LoginAttempt.success == False,
            LoginAttempt.attempted_at >= cutoff_time
        ).count()
        
        return failed_attempts < self.max_attempts_per_account
    
    def lock_account(self, user: User, db: Session):
        """계정 잠금"""
        user.account_locked_until = datetime.utcnow() + timedelta(minutes=self.lockout_duration_minutes)
        user.failed_login_attempts += 1
        db.commit()
    
    def is_account_locked(self, user: User) -> bool:
        """계정 잠금 상태 확인"""
        if user.account_locked_until is None:
            return False
        
        return datetime.utcnow() < user.account_locked_until
    
    def unlock_account(self, user: User, db: Session):
        """계정 잠금 해제"""
        user.account_locked_until = None
        user.failed_login_attempts = 0
        db.commit()
    
    def validate_login_attempt(self, site_id: str, ip_address: str, db: Session):
        """로그인 시도 전 검증"""
        # IP 기반 제한 확인
        if not self.check_ip_attempts(ip_address, db):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts from this IP. Try again in {self.attempt_window_minutes} minutes."
            )
        
        # 계정 기반 제한 확인
        if not self.check_account_attempts(site_id, db):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts for this account. Try again in {self.attempt_window_minutes} minutes."
            )
        
        # 사용자 계정 잠금 상태 확인
        user = db.query(User).filter(User.site_id == site_id).first()
        if user and self.is_account_locked(user):
            remaining_time = (user.account_locked_until - datetime.utcnow()).total_seconds() / 60
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account is locked. Try again in {int(remaining_time)} minutes."
            )
    
    def update_login_success(self, user: User, db: Session):
        """로그인 성공 시 업데이트"""
        user.last_login_at = datetime.utcnow()
        user.login_count += 1
        user.failed_login_attempts = 0
        user.account_locked_until = None
        db.commit()
    
    def update_login_failure(self, user: User, db: Session):
        """로그인 실패 시 업데이트"""
        user.failed_login_attempts += 1
        
        # 계정 잠금 임계값 확인
        if user.failed_login_attempts >= self.max_attempts_per_account:
            self.lock_account(user, db)
        else:
            db.commit()


# 전역 인스턴스
login_security = LoginSecurityService()
