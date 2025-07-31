"""
간단한 FastAPI 테스트 서버 - SQLAlchemy 없이
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import bcrypt
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os

app = FastAPI(
    title="Casino Club Auth API",
    description="간소화된 인증 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT 설정
JWT_SECRET_KEY = "casino-club-secret-key-2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

# 데이터베이스 경로
DB_PATH = "auth.db"

# Pydantic 모델들
class LoginRequest(BaseModel):
    site_id: str
    password: str

class SignUpRequest(BaseModel):
    site_id: str
    nickname: str
    phone_number: str
    password: str
    invite_code: str

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

class VerifyInviteRequest(BaseModel):
    code: str

# 유틸리티 함수들
def get_db_connection():
    """데이터베이스 연결"""
    return sqlite3.connect(DB_PATH)

def create_access_token(user_id: int) -> str:
    """JWT 액세스 토큰 생성"""
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# API 엔드포인트들
@app.get("/health")
async def health_check():
    """헬스체크"""
    return {"status": "healthy", "message": "인증 서버가 정상 작동 중입니다"}

@app.post("/api/auth/verify-invite")
async def verify_invite(req: VerifyInviteRequest):
    """초대 코드 검증"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM invite_codes WHERE code = ? AND is_used = 0", (req.code,))
    result = cursor.fetchone()
    conn.close()
    
    is_valid = bool(result)
    return {"valid": is_valid}

@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(data: SignUpRequest):
    """회원가입"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 중복 검사들
        cursor.execute("SELECT id FROM users WHERE site_id = ?", (data.site_id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Site ID already taken")
        
        cursor.execute("SELECT id FROM users WHERE nickname = ?", (data.nickname,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Nickname already taken")
        
        cursor.execute("SELECT id FROM users WHERE phone_number = ?", (data.phone_number,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Phone number already taken")
        
        # 초대코드 검증
        cursor.execute("SELECT id FROM invite_codes WHERE code = ?", (data.invite_code,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Invalid invite code")
        
        # 비밀번호 검증
        if len(data.password) < 4:
            raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
        
        # 사용자 생성
        password_hash = hash_password(data.password)
        cursor.execute("""
        INSERT INTO users (site_id, nickname, phone_number, password_hash, invite_code, cyber_token_balance)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (data.site_id, data.nickname, data.phone_number, password_hash, data.invite_code, 200))
        
        user_id = cursor.lastrowid
        
        # 초대코드 사용 처리
        cursor.execute("UPDATE invite_codes SET is_used = 1, used_at = CURRENT_TIMESTAMP WHERE code = ?", (data.invite_code,))
        
        conn.commit()
        
        # 토큰 생성
        access_token = create_access_token(user_id)
        
        return TokenResponse(access_token=access_token)
        
    except HTTPException:
        conn.rollback()
        raise
    finally:
        conn.close()

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """로그인"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 사용자 찾기
        cursor.execute("SELECT id, password_hash FROM users WHERE site_id = ?", (data.site_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_id, password_hash = user_data
        
        # 비밀번호 검증
        if not verify_password(data.password, password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # 최근 로그인 시간 업데이트
        cursor.execute("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()
        
        # 토큰 생성
        access_token = create_access_token(user_id)
        
        return TokenResponse(access_token=access_token)
        
    finally:
        conn.close()

@app.get("/api/auth/me", response_model=UserInfo)
async def get_me():
    """현재 사용자 정보 (인증 토큰 검증 없이 테스트용)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 첫 번째 사용자 반환 (테스트용)
        cursor.execute("SELECT id, site_id, nickname, phone_number, cyber_token_balance, rank FROM users LIMIT 1")
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id, site_id, nickname, phone_number, cyber_token_balance, rank = user_data
        
        return UserInfo(
            id=user_id,
            site_id=site_id,
            nickname=nickname,
            phone_number=phone_number,
            cyber_token_balance=cyber_token_balance,
            rank=rank
        )
        
    finally:
        conn.close()

@app.get("/api/auth/users")
async def list_users():
    """사용자 목록 (테스트용)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, site_id, nickname, cyber_token_balance, rank FROM users")
        users = cursor.fetchall()
        
        return {
            "users": [
                {
                    "id": user[0],
                    "site_id": user[1],
                    "nickname": user[2],
                    "cyber_token_balance": user[3],
                    "rank": user[4]
                }
                for user in users
            ],
            "total": len(users)
        }
        
    finally:
        conn.close()

@app.get("/api/auth/invite-codes")
async def list_invite_codes():
    """초대 코드 목록 (테스트용)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT code, is_used, created_at FROM invite_codes")
        codes = cursor.fetchall()
        
        return {
            "invite_codes": [
                {
                    "code": code[0],
                    "is_used": bool(code[1]),
                    "created_at": code[2]
                }
                for code in codes
            ],
            "total": len(codes)
        }
        
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
