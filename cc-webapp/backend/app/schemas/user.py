# 파일 위치: c:\Users\bdbd\Downloads\auto202506-a-main\auto202506-a-main\cc-webapp\backend\app\schemas\user.py
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    site_id: str
    nickname: str
    phone_number: str

class UserCreate(UserBase):
    password: str
    invite_code: str

# Add UserRegister schema for registration endpoints
class UserRegister(BaseModel):
    site_id: str
    nickname: str
    phone_number: str
    password: str
    invite_code: str

class UserLogin(BaseModel):
    site_id: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

# Add UserResponse for API responses
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    site_id: str
    nickname: str
    phone_number: str
    invite_code: str
    cyber_token_balance: int
    created_at: datetime
    rank: str

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    invite_code: str
    cyber_token_balance: int
    created_at: datetime
    rank: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    rank: Optional[str] = None