# 파일 위치: c:\Users\bdbd\Downloads\auto202506-a-main\auto202506-a-main\cc-webapp\backend\app\schemas\invite_code.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class InviteCodeBase(BaseModel):
    code: str
    
class InviteCodeCreate(InviteCodeBase):
    created_by_user_id: Optional[int] = None

class InviteCode(InviteCodeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_used: bool
    created_at: datetime
    used_at: Optional[datetime] = None
    created_by_user_id: Optional[int] = None
    used_by_user_id: Optional[int] = None

# Add InviteCodeResponse for API responses
class InviteCodeResponse(BaseModel):
    code: str
    is_used: bool
    created_at: datetime
    used_at: Optional[datetime] = None

# Add InviteCodeList for listing multiple invite codes
class InviteCodeList(BaseModel):
    invite_codes: List[InviteCodeResponse]