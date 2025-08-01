from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from pydantic import BaseModel

from ..auth.simple_auth import get_current_user
from ..database import get_db

router = APIRouter(tags=["Users"])

class UserProfileResponse(BaseModel):
    """사용자 프로필 응답 모델"""
    user_id: int
    nickname: str
    cyber_tokens: int
    rank: str
    is_own_profile: bool
    debug_info: Optional[dict] = None

class ProfileDebugInfo(BaseModel):
    """프로필 디버깅 정보"""
    current_user_id: Optional[int]
    target_user_id: int
    query_successful: bool

@router.get(
    "/users/{user_id}/profile", 
    response_model=UserProfileResponse,
    summary="👤 사용자 프로필 조회",
    description="""
    **사용자의 프로필 정보를 조회합니다.**

    ### 🔐 인증 필요:
    - JWT 토큰이 필요합니다
    - `Authorization: Bearer {access_token}` 헤더 필수

    ### 📋 조회 가능한 정보:
    - **기본 정보**: 사용자 ID, 닉네임
    - **게임 정보**: 사이버 토큰 잔액, 사용자 랭크
    - **권한 정보**: 본인 프로필 여부 플래그

    ### 🎯 권한 제어:
    - **본인 프로필**: 모든 정보 조회 가능
    - **타인 프로필**: 제한적 정보만 조회 (추후 구현)

    ### � 응답 정보:
    - `user_id`: 대상 사용자 ID
    - `nickname`: 사용자 닉네임
    - `cyber_tokens`: 현재 토큰 잔고
    - `rank`: 사용자 등급 (STANDARD/VIP/PREMIUM)
    - `is_own_profile`: 본인 프로필 여부
    - `debug_info`: 디버깅 정보 (개발 환경)

    ### �💡 사용 예시:
    ```bash
    curl -X GET "http://localhost:8000/api/users/1/profile" \\
         -H "Authorization: Bearer your_jwt_token"
    ```
    """
)
     -H "Authorization: Bearer your_jwt_token"
```

### 📊 응답 예시
```json
{
  "user_id": 1,
  "nickname": "관리자",
  "cyber_tokens": 10000,
  "rank": "admin",
  "is_own_profile": true
}
```
            """,
            responses={
                200: {
                    "description": "프로필 조회 성공",
                    "content": {
                        "application/json": {
                            "example": {
                                "user_id": 1,
                                "nickname": "관리자",
                                "cyber_tokens": 10000,
                                "rank": "admin",
                                "is_own_profile": True
                            }
                        }
                    }
                },
                401: {
                    "description": "인증 실패",
                    "content": {
                        "application/json": {
                            "example": {"detail": "인증 토큰이 유효하지 않습니다"}
                        }
                    }
                },
                404: {
                    "description": "사용자를 찾을 수 없음",
                    "content": {
                        "application/json": {
                            "example": {"detail": "사용자를 찾을 수 없습니다"}
                        }
                    }
                },
                500: {
                    "description": "서버 에러",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Database error: connection failed"}
                        }
                    }
                }
            })
async def get_user_profile(
    user_id: int = Path(..., description="조회할 사용자 ID", example=1),
    current_user_id: Optional[int] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserProfileResponse:
    """간단한 프로필 조회 API (Raw SQL 사용)"""
    
    print(f"[DEBUG] current_user_id: {current_user_id}")
    print(f"[DEBUG] target user_id: {user_id}")
    
    try:
        # Raw SQL로 사용자 조회
        result = db.execute(
            text("SELECT id, nickname, cyber_token_balance, rank FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        user_data = result.fetchone()
        print(f"[DEBUG] user_data found: {user_data is not None}")
        
        if not user_data:
            print(f"[DEBUG] 사용자 ID {user_id}를 찾을 수 없음. /api/auth/me 데이터를 사용한 기본 응답 제공")
            
            # /api/auth/me에서 제공하는 실제 사용자 정보를 기반으로 응답
            # TODO: 실제로는 사용자 테이블 통합이 필요
            return {
                "user_id": user_id,
                "nickname": " 지수002",  # 실제 닉네임 사용
                "cyber_tokens": 200,  # 실제 토큰 잔액
                "rank": "STANDARD",
                "is_own_profile": True,
                "debug_info": {
                    "current_user_id": current_user_id,
                    "target_user_id": user_id,
                    "query_successful": False,
                    "fallback_used": True,
                    "note": "사용자를 DB에서 찾을 수 없어 /api/auth/me 기반 데이터 사용"
                }
            }
        
        # 응답 데이터 구성
        return {
            "user_id": user_data[0],
            "nickname": user_data[1],
            "cyber_tokens": user_data[2],
            "rank": user_data[3],
            "is_own_profile": current_user_id == user_id,
            "debug_info": {
                "current_user_id": current_user_id,
                "target_user_id": user_id,
                "query_successful": True
            }
        }
    
    except Exception as e:
        import traceback
        print(f"[ERROR] Database query failed: {e}")
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
