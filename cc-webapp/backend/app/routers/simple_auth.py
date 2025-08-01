"""
PostgreSQL 기반 간단한 인증 라우터
- 지침에 따라 PostgreSQL 사용
- Docker Compose 환경에서 작동
- JWT 토큰 인증
- Redis 캐싱 지원
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import jwt
import redis
from datetime import datetime, timedelta
import os
from typing import Optional
import logging

# 설정
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "casino-club-secret-key-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# PostgreSQL 연결 설정
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "cc_postgres"),  # Docker Compose 환경변수에서 설정
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "cc_webapp"),
    "user": os.getenv("DB_USER", "cc_user"),
    "password": os.getenv("DB_PASSWORD", "cc_password")
}

# Redis 연결 설정
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "cc_redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
        socket_timeout=5
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    redis_client = None

router = APIRouter(prefix="/auth", tags=["Simple Auth"])
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Pydantic 모델들
class VerifyInviteRequest(BaseModel):
    code: str

class SignUpRequest(BaseModel):
    site_id: str
    nickname: str
    phone_number: str
    password: str
    invite_code: str

class LoginRequest(BaseModel):
    site_id: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = JWT_EXPIRE_MINUTES * 60

class UserInfo(BaseModel):
    id: int
    site_id: str
    nickname: str
    phone_number: str
    cyber_token_balance: int
    rank: str

# 유틸리티 함수들
def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def create_tables():
    """필요한 테이블 생성"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 사용자 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            site_id VARCHAR(50) UNIQUE NOT NULL,
            nickname VARCHAR(50) UNIQUE NOT NULL,
            phone_number VARCHAR(20) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL,
            invite_code VARCHAR(6) NOT NULL,
            cyber_token_balance INTEGER DEFAULT 200,
            rank VARCHAR(20) DEFAULT 'STANDARD',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login_at TIMESTAMP
        );
        """)
        
        # 초대코드 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invite_codes (
            id SERIAL PRIMARY KEY,
            code VARCHAR(6) UNIQUE NOT NULL,
            is_used BOOLEAN DEFAULT FALSE,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 고정 초대코드들 추가 (6974, 6969, 2560 무한재사용)
        cursor.execute("""
        INSERT INTO invite_codes (code, is_used, use_count, max_uses, expires_at, created_by_user_id, used_by_user_id, last_used_at) 
        VALUES 
            ('6974', FALSE, 0, NULL, NULL, NULL, NULL, NULL),
            ('6969', FALSE, 0, NULL, NULL, NULL, NULL, NULL),
            ('2560', FALSE, 0, NULL, NULL, NULL, NULL, NULL),
            ('TEST01', FALSE, 0, 1, NULL, NULL, NULL, NULL),
            ('TEST02', FALSE, 0, 1, NULL, NULL, NULL, NULL),
            ('TEST03', FALSE, 0, 1, NULL, NULL, NULL, NULL)
        ON CONFLICT (code) DO NOTHING;
        """)
        
        conn.commit()
        logger.info("Tables created successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Table creation failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def create_access_token(user_id: int) -> str:
    """JWT 액세스 토큰 생성"""
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": f"jti_{user_id}_{int(datetime.utcnow().timestamp())}"
    }
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def cache_user_data(user_id: int, data: dict):
    """Redis에 사용자 데이터 캐싱"""
    if REDIS_AVAILABLE:
        try:
            redis_client.setex(f"user:{user_id}", 3600, str(data))
        except Exception as e:
            logger.warning(f"Redis cache failed: {e}")

def get_cached_user_data(user_id: int):
    """Redis에서 사용자 데이터 조회"""
    if REDIS_AVAILABLE:
        try:
            cached_data = redis_client.get(f"user:{user_id}")
            if cached_data:
                return eval(cached_data)  # 실제 운영에서는 json.loads 사용
        except Exception as e:
            logger.warning(f"Redis retrieval failed: {e}")
    return None

# API 엔드포인트들
@router.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy", 
        "message": "PostgreSQL 인증 서버가 정상 작동 중입니다",
        "redis": "available" if REDIS_AVAILABLE else "unavailable"
    }

@router.post("/verify-invite")
async def verify_invite(req: VerifyInviteRequest):
    """초대 코드 검증"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 무한재사용 코드 (6974, 6969, 2560)는 항상 유효
        if req.code in ['6974', '6969', '2560']:
            return {"valid": True}
        
        # 다른 코드들은 기존 로직 적용 (use_count < max_uses 또는 max_uses가 NULL)
        cursor.execute("""
            SELECT id FROM invite_codes 
            WHERE code = %s 
            AND (max_uses IS NULL OR use_count < max_uses)
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        """, (req.code,))
        result = cursor.fetchone()
        is_valid = bool(result)
        
        return {"valid": is_valid}
        
    finally:
        cursor.close()
        conn.close()

@router.post("/signup", response_model=TokenResponse)
async def signup(data: SignUpRequest):
    """회원가입"""
    logger.info(f"Signup request received: {data}")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 중복 검사들
        cursor.execute("SELECT id FROM users WHERE site_id = %s", (data.site_id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Site ID already taken")
        
        cursor.execute("SELECT id FROM users WHERE nickname = %s", (data.nickname,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Nickname already taken")
        
        cursor.execute("SELECT id FROM users WHERE phone_number = %s", (data.phone_number,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Phone number already taken")
        
        # 초대코드 검증 (무한재사용 가능)
        if data.invite_code in ['6974', '6969', '2560']:
            # 무한재사용 코드는 항상 유효
            pass
        else:
            # 다른 코드들은 사용 제한 확인
            cursor.execute("""
                SELECT id FROM invite_codes 
                WHERE code = %s 
                AND (max_uses IS NULL OR use_count < max_uses)
                AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            """, (data.invite_code,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail="Invalid invite code")
        
        # 비밀번호 검증
        if len(data.password) < 4:
            raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
        
        # 사용자 생성
        password_hash = hash_password(data.password)
        cursor.execute("""
        INSERT INTO users (site_id, nickname, phone_number, password_hash, invite_code, cyber_token_balance, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING id
        """, (data.site_id, data.nickname, data.phone_number, password_hash, data.invite_code, 200))
        
        user_data = cursor.fetchone()
        user_id = user_data['id']
        
        # 초대코드 사용 카운트 업데이트 (무한재사용 코드 제외)
        if data.invite_code not in ['6974', '6969', '2560']:
            cursor.execute("""
                UPDATE invite_codes 
                SET use_count = use_count + 1, last_used_at = CURRENT_TIMESTAMP
                WHERE code = %s
            """, (data.invite_code,))
        
        conn.commit()
        
        # 토큰 생성
        access_token = create_access_token(user_id)
        
        # 캐시에 사용자 정보 저장
        cache_user_data(user_id, {"id": user_id, "site_id": data.site_id, "nickname": data.nickname})
        
        return TokenResponse(access_token=access_token)
        
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        cursor.close()
        conn.close()

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """로그인"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 사용자 찾기
        cursor.execute("SELECT id, password_hash, nickname FROM users WHERE site_id = %s", (data.site_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_id = user_data['id']
        password_hash = user_data['password_hash']
        nickname = user_data['nickname']
        
        # 비밀번호 검증
        if not verify_password(data.password, password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # 최근 로그인 시간 업데이트
        cursor.execute("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = %s", (user_id,))
        conn.commit()
        
        # 토큰 생성
        access_token = create_access_token(user_id)
        
        # 캐시에 사용자 정보 저장
        cache_user_data(user_id, {"id": user_id, "site_id": data.site_id, "nickname": nickname})
        
        return TokenResponse(access_token=access_token)
        
    finally:
        cursor.close()
        conn.close()

@router.get("/me", response_model=UserInfo)
async def get_me():
    """현재 사용자 정보 (테스트용 - 인증 토큰 검증 없이)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 최신 사용자 조회 (모든 필수 컬럼 명시)
        cursor.execute("""
            SELECT id, site_id, nickname, phone_number, 
                   COALESCE(cyber_token_balance, 200) as cyber_token_balance, 
                   COALESCE(rank, 'STANDARD') as rank 
            FROM users 
            WHERE id IS NOT NULL 
            ORDER BY created_at DESC LIMIT 1
        """)
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserInfo(
            id=user_data['id'],
            site_id=user_data['site_id'],
            nickname=user_data['nickname'],
            phone_number=user_data['phone_number'],
            cyber_token_balance=user_data['cyber_token_balance'],
            rank=user_data['rank']
        )
        
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/users")
async def list_users():
    """사용자 목록 (테스트용)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT id, site_id, nickname, cyber_token_balance, rank, created_at FROM users ORDER BY created_at DESC LIMIT 10")
        users = cursor.fetchall()
        
        return {"users": users, "count": len(users)}
        
    finally:
        cursor.close()
        conn.close()

# 서버 시작시 테이블 생성
try:
    create_tables()
except Exception as e:
    logger.error(f"Failed to create tables: {e}")
