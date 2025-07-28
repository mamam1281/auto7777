from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserAdminResponse(BaseModel):
    id: int
    site_id: str
    nickname: str
    phone_number: str
    created_at: datetime
    cyber_token_balance: int
    rank: str
    
    class Config:
        orm_mode = True

class ActivityResponse(BaseModel):
    id: int
    activity_type: str
    timestamp: datetime
    details: Optional[str] = None
    
    class Config:
        orm_mode = True

class UserDetailResponse(UserAdminResponse):
    activities: List[ActivityResponse]

class GiveRewardRequest(BaseModel):
    user_id: int
    amount: int
    reason: str

class RewardResponse(BaseModel):
    id: int
    user_id: int
    type: str
    amount: int
    created_at: datetime
    
    class Config:
        orm_mode = True
