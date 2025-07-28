#!/usr/bin/env python3
"""
Simple Test Backend for Admin Functionality Testing
"""
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import random

app = FastAPI(title="Test Backend for Admin Dashboard", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 임시 데이터베이스 (메모리 저장)
fake_users = [
    {
        "id": 1,
        "nickname": "TestAdmin",
        "email": "admin@test.com",
        "cyber_token_balance": 10000,
        "current_rank": "ADMIN",
        "is_verified": True,
        "is_active": True,
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-07-28T12:00:00Z"
    },
    {
        "id": 2,
        "nickname": "TestUser",
        "email": "user@test.com",
        "cyber_token_balance": 500,
        "current_rank": "BASIC",
        "is_verified": True,
        "is_active": True,
        "created_at": "2025-01-15T00:00:00Z",
        "last_login": "2025-07-28T11:30:00Z"
    },
    {
        "id": 3,
        "nickname": "VIPUser",
        "email": "vip@test.com",
        "cyber_token_balance": 5000,
        "current_rank": "VIP",
        "is_verified": True,
        "is_active": True,
        "created_at": "2025-02-01T00:00:00Z",
        "last_login": "2025-07-28T10:15:00Z"
    },
]

fake_activities = [
    {
        "id": 1,
        "user_id": 2,
        "user_nickname": "TestUser",
        "activity_type": "LOGIN",
        "details": "사용자가 로그인했습니다",
        "timestamp": "2025-07-28T11:30:00Z"
    },
    {
        "id": 2,
        "user_id": 3,
        "user_nickname": "VIPUser",
        "activity_type": "GAME_PLAY",
        "details": "슬롯 게임을 플레이했습니다",
        "timestamp": "2025-07-28T10:15:00Z"
    },
    {
        "id": 3,
        "user_id": 2,
        "user_nickname": "TestUser",
        "activity_type": "REWARD_RECEIVED",
        "details": "일일 보상을 받았습니다 (100 토큰)",
        "timestamp": "2025-07-28T09:00:00Z"
    },
]

# 인증 의존성
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token required")
    
    token = authorization.split(" ")[1]
    # 간단한 토큰 검증 (실제로는 JWT 디코딩 등을 사용)
    if token in ["test-admin-token-123", "test-user-token-456"]:
        return {"token": token}
    
    raise HTTPException(status_code=401, detail="Invalid token")

# 관리자 권한 확인
def get_admin_user(current_user = Depends(get_current_user)):
    if current_user["token"] != "test-admin-token-123":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# API 라우트들
@app.get("/")
async def read_root():
    return {
        "message": "Test Backend for Admin Dashboard", 
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/admin/users")
async def get_users(admin_user = Depends(get_admin_user)):
    return fake_users

@app.get("/api/admin/users/{user_id}")
async def get_user(user_id: int, admin_user = Depends(get_admin_user)):
    user = next((u for u in fake_users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/admin/users/{user_id}/activities")
async def get_user_activities(user_id: int, admin_user = Depends(get_admin_user)):
    user_activities = [a for a in fake_activities if a["user_id"] == user_id]
    return user_activities

@app.get("/api/admin/activities")
async def get_activities(limit: int = 10, admin_user = Depends(get_admin_user)):
    return fake_activities[:limit]

@app.post("/api/admin/users/{user_id}/give-reward")
async def give_reward(
    user_id: int, 
    reward_data: dict,
    admin_user = Depends(get_admin_user)
):
    user = next((u for u in fake_users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    token_amount = reward_data.get("token_amount", 0)
    reason = reward_data.get("reason", "관리자 지급")
    
    # 토큰 업데이트
    user["cyber_token_balance"] += token_amount
    
    # 활동 로그 추가
    new_activity = {
        "id": len(fake_activities) + 1,
        "user_id": user_id,
        "user_nickname": user["nickname"],
        "activity_type": "REWARD_RECEIVED",
        "details": f"{reason} ({token_amount} 토큰)",
        "timestamp": datetime.now().isoformat() + "Z"
    }
    fake_activities.insert(0, new_activity)
    
    return {"message": "Reward given successfully", "new_balance": user["cyber_token_balance"]}

if __name__ == "__main__":
    import uvicorn
    print("🎮 Casino-Club Test Backend 시작 중...")
    print("🚀 FastAPI 서버를 시작합니다...")
    print("🌐 API 문서: http://localhost:8000/docs")
    print("🛑 서버 중지: Ctrl+C를 눌러주세요")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
