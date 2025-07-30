"""
백그라운드 작업: 토큰 정리 및 세션 관리
"""
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..auth.advanced_jwt_handler import jwt_handler
from ..models.user_session import LoginAttempt

logger = logging.getLogger(__name__)


class TokenCleanupService:
    """토큰 정리 서비스"""
    
    @staticmethod
    def cleanup_expired_tokens():
        """만료된 토큰 및 세션 정리"""
        db = SessionLocal()
        try:
            jwt_handler.cleanup_expired_tokens(db)
            logger.info("Expired tokens cleaned up successfully")
        except Exception as e:
            logger.error(f"Token cleanup failed: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def cleanup_old_login_attempts():
        """오래된 로그인 시도 기록 정리 (30일 이상)"""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            deleted_count = db.query(LoginAttempt).filter(
                LoginAttempt.attempted_at < cutoff_date
            ).delete()
            db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old login attempts")
        except Exception as e:
            logger.error(f"Login attempts cleanup failed: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def generate_security_report():
        """보안 리포트 생성"""
        db = SessionLocal()
        try:
            from datetime import timedelta
            
            # 최근 24시간 통계
            last_24h = datetime.utcnow() - timedelta(hours=24)
            
            total_attempts = db.query(LoginAttempt).filter(
                LoginAttempt.attempted_at >= last_24h
            ).count()
            
            failed_attempts = db.query(LoginAttempt).filter(
                LoginAttempt.attempted_at >= last_24h,
                LoginAttempt.success == False
            ).count()
            
            success_rate = ((total_attempts - failed_attempts) / total_attempts * 100) if total_attempts > 0 else 0
            
            logger.info(f"Security Report (24h): Total attempts: {total_attempts}, "
                       f"Failed: {failed_attempts}, Success rate: {success_rate:.1f}%")
            
        except Exception as e:
            logger.error(f"Security report generation failed: {str(e)}")
        finally:
            db.close()


# 스케줄러에서 사용할 함수들
def scheduled_token_cleanup():
    """스케줄된 토큰 정리"""
    TokenCleanupService.cleanup_expired_tokens()

def scheduled_login_attempts_cleanup():
    """스케줄된 로그인 시도 정리"""
    TokenCleanupService.cleanup_old_login_attempts()

def scheduled_security_report():
    """스케줄된 보안 리포트"""
    TokenCleanupService.generate_security_report()
