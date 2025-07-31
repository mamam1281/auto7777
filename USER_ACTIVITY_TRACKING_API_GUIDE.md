# 🎯 사용자 행적 추적 API 가이드

## 📋 개요
사용자의 게임 데이터, 토큰 거래 내역, 보상 이력 등 모든 활동을 추적하고 관리하기 위한 API 시스템 설계 가이드입니다.

## 🗄️ 데이터베이스 스키마 설계

### 1. 사용자 활동 로그 테이블
```sql
CREATE TABLE user_activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    activity_type VARCHAR(50) NOT NULL, -- 'game', 'token', 'reward', 'login', 'mission'
    activity_subtype VARCHAR(50), -- 'win', 'lose', 'charge', 'spend', 'claim', 'complete'
    activity_data JSONB, -- 상세 데이터 (게임 결과, 토큰 양, 보상 내용 등)
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    session_id VARCHAR(255),
    
    INDEX idx_user_activity (user_id, created_at),
    INDEX idx_activity_type (activity_type, created_at)
);
```

### 2. 토큰 거래 내역 테이블
```sql
CREATE TABLE token_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    transaction_type VARCHAR(20) NOT NULL, -- 'charge', 'spend', 'reward', 'refund'
    amount INTEGER NOT NULL, -- 변동 토큰 수
    balance_before INTEGER NOT NULL, -- 거래 전 잔액
    balance_after INTEGER NOT NULL, -- 거래 후 잔액
    description TEXT, -- 거래 설명
    game_session_id VARCHAR(255), -- 게임 세션 연결
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_transactions (user_id, created_at),
    INDEX idx_transaction_type (transaction_type, created_at)
);
```

### 3. 게임 세션 테이블
```sql
CREATE TABLE game_sessions (
    id VARCHAR(255) PRIMARY KEY, -- UUID
    user_id INTEGER NOT NULL REFERENCES users(id),
    game_type VARCHAR(50) NOT NULL, -- 'slot', 'poker', 'blackjack' 등
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    total_bet INTEGER DEFAULT 0,
    total_win INTEGER DEFAULT 0,
    net_result INTEGER DEFAULT 0, -- 순 손익
    session_data JSONB, -- 게임별 상세 데이터
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'abandoned'
    
    INDEX idx_user_games (user_id, start_time),
    INDEX idx_game_type (game_type, start_time)
);
```

### 4. 보상 지급 내역 테이블
```sql
CREATE TABLE reward_claims (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    reward_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'achievement', 'promotion'
    reward_name VARCHAR(100) NOT NULL,
    reward_data JSONB, -- 보상 상세 내용
    tokens_awarded INTEGER DEFAULT 0,
    claimed_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    
    INDEX idx_user_rewards (user_id, claimed_at),
    INDEX idx_reward_type (reward_type, claimed_at)
);
```

### 5. 미션 완료 내역 테이블
```sql
CREATE TABLE mission_completions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    mission_id VARCHAR(100) NOT NULL,
    mission_name VARCHAR(200) NOT NULL,
    completion_data JSONB, -- 완료 조건 상세
    tokens_earned INTEGER DEFAULT 0,
    completed_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, mission_id),
    INDEX idx_user_missions (user_id, completed_at)
);
```

## 🔗 API 엔드포인트 설계

### 1. 활동 로그 기록 API
```python
@router.post("/users/{user_id}/activity")
async def log_user_activity(
    user_id: int,
    activity: UserActivityRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """사용자 활동 로그 기록"""
    activity_log = UserActivityLog(
        user_id=user_id,
        activity_type=activity.type,
        activity_subtype=activity.subtype,
        activity_data=activity.data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        session_id=activity.session_id
    )
    db.add(activity_log)
    db.commit()
    return {"status": "logged"}
```

### 2. 사용자 활동 조회 API
```python
@router.get("/users/{user_id}/activity")
async def get_user_activity(
    user_id: int,
    activity_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> UserActivityResponse:
    """사용자 활동 내역 조회"""
    query = db.query(UserActivityLog).filter(
        UserActivityLog.user_id == user_id
    )
    
    if activity_type:
        query = query.filter(UserActivityLog.activity_type == activity_type)
    
    activities = query.order_by(
        UserActivityLog.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return UserActivityResponse(
        activities=[format_activity(a) for a in activities],
        total_count=query.count()
    )
```

### 3. 토큰 거래 내역 API
```python
@router.get("/users/{user_id}/token-history")
async def get_token_history(
    user_id: int,
    transaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
) -> TokenHistoryResponse:
    """토큰 거래 내역 조회"""
    query = db.query(TokenTransaction).filter(
        TokenTransaction.user_id == user_id
    )
    
    if transaction_type:
        query = query.filter(TokenTransaction.transaction_type == transaction_type)
    
    if start_date:
        query = query.filter(TokenTransaction.created_at >= start_date)
    
    if end_date:
        query = query.filter(TokenTransaction.created_at <= end_date)
    
    transactions = query.order_by(
        TokenTransaction.created_at.desc()
    ).all()
    
    return TokenHistoryResponse(
        transactions=[format_transaction(t) for t in transactions],
        summary=calculate_token_summary(transactions)
    )
```

### 4. 게임 통계 API
```python
@router.get("/users/{user_id}/game-stats")
async def get_game_stats(
    user_id: int,
    game_type: Optional[str] = None,
    period: str = "week", # 'day', 'week', 'month', 'all'
    db: Session = Depends(get_db)
) -> GameStatsResponse:
    """게임 통계 조회"""
    start_date = calculate_period_start(period)
    
    query = db.query(GameSession).filter(
        GameSession.user_id == user_id,
        GameSession.start_time >= start_date
    )
    
    if game_type:
        query = query.filter(GameSession.game_type == game_type)
    
    sessions = query.all()
    
    return GameStatsResponse(
        total_sessions=len(sessions),
        total_bet=sum(s.total_bet for s in sessions),
        total_win=sum(s.total_win for s in sessions),
        net_result=sum(s.net_result for s in sessions),
        win_rate=calculate_win_rate(sessions),
        favorite_game=get_most_played_game(sessions),
        play_time=calculate_total_play_time(sessions)
    )
```

### 5. 보상 내역 API
```python
@router.get("/users/{user_id}/rewards")
async def get_reward_history(
    user_id: int,
    reward_type: Optional[str] = None,
    db: Session = Depends(get_db)
) -> RewardHistoryResponse:
    """보상 지급 내역 조회"""
    query = db.query(RewardClaim).filter(
        RewardClaim.user_id == user_id
    )
    
    if reward_type:
        query = query.filter(RewardClaim.reward_type == reward_type)
    
    rewards = query.order_by(
        RewardClaim.claimed_at.desc()
    ).all()
    
    return RewardHistoryResponse(
        rewards=[format_reward(r) for r in rewards],
        total_tokens_earned=sum(r.tokens_awarded for r in rewards)
    )
```

## 📊 데이터 모델 (Pydantic)

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class UserActivityRequest(BaseModel):
    type: str # 'game', 'token', 'reward', 'login', 'mission'
    subtype: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class ActivityLogResponse(BaseModel):
    id: int
    activity_type: str
    activity_subtype: Optional[str]
    activity_data: Optional[Dict[str, Any]]
    created_at: datetime
    
class UserActivityResponse(BaseModel):
    activities: List[ActivityLogResponse]
    total_count: int

class TokenTransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: int
    balance_before: int
    balance_after: int
    description: Optional[str]
    created_at: datetime

class TokenSummary(BaseModel):
    total_charged: int
    total_spent: int
    total_earned: int
    current_balance: int

class TokenHistoryResponse(BaseModel):
    transactions: List[TokenTransactionResponse]
    summary: TokenSummary

class GameStatsResponse(BaseModel):
    total_sessions: int
    total_bet: int
    total_win: int
    net_result: int
    win_rate: float
    favorite_game: Optional[str]
    play_time_minutes: int

class RewardResponse(BaseModel):
    id: int
    reward_type: str
    reward_name: str
    tokens_awarded: int
    claimed_at: datetime

class RewardHistoryResponse(BaseModel):
    rewards: List[RewardResponse]
    total_tokens_earned: int
```

## 🎮 게임별 활동 추적 예시

### 슬롯 게임 활동 로깅
```python
async def log_slot_game_activity(user_id: int, game_result: dict):
    activity_data = {
        "game_type": "slot",
        "bet_amount": game_result["bet"],
        "win_amount": game_result["win"],
        "symbols": game_result["symbols"],
        "bonus_triggered": game_result.get("bonus", False),
        "jackpot": game_result.get("jackpot", False)
    }
    
    await log_activity(
        user_id=user_id,
        activity_type="game",
        activity_subtype="slot_spin",
        activity_data=activity_data
    )
```

### 토큰 충전 활동 로깅
```python
async def log_token_charge(user_id: int, amount: int, payment_method: str):
    # 토큰 거래 테이블에 기록
    await create_token_transaction(
        user_id=user_id,
        transaction_type="charge",
        amount=amount,
        description=f"토큰 충전 ({payment_method})"
    )
    
    # 활동 로그에도 기록
    await log_activity(
        user_id=user_id,
        activity_type="token",
        activity_subtype="charge",
        activity_data={
            "amount": amount,
            "payment_method": payment_method
        }
    )
```

## 🔍 분석 및 리포팅

### 사용자 패턴 분석 쿼리
```sql
-- 사용자별 게임 선호도 분석
SELECT 
    u.nickname,
    gs.game_type,
    COUNT(*) as session_count,
    AVG(gs.total_bet) as avg_bet,
    AVG(gs.net_result) as avg_result
FROM users u
JOIN game_sessions gs ON u.id = gs.user_id
WHERE gs.start_time >= NOW() - INTERVAL '30 days'
GROUP BY u.id, u.nickname, gs.game_type
ORDER BY session_count DESC;

-- 일별 활성 사용자 및 수익
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as active_users,
    SUM(CASE WHEN transaction_type = 'charge' THEN amount ELSE 0 END) as total_charged,
    SUM(CASE WHEN transaction_type = 'spend' THEN amount ELSE 0 END) as total_spent
FROM token_transactions
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

## 🚀 구현 우선순위

1. **1단계**: 기본 활동 로깅
   - 로그인/로그아웃
   - 게임 시작/종료
   - 토큰 거래

2. **2단계**: 상세 게임 데이터
   - 게임별 세부 결과
   - 미션 완료 추적
   - 보상 지급 내역

3. **3단계**: 분석 및 리포팅
   - 사용자 행동 패턴 분석
   - 수익성 분석
   - 이상 행위 탐지

## 🔐 보안 고려사항

- 개인정보보호: IP 주소 등 민감 정보 암호화
- 데이터 보존 정책: 일정 기간 후 자동 삭제
- 접근 권한: 관리자만 전체 데이터 접근 가능
- 로그 무결성: 변조 방지를 위한 해시 검증

이 가이드를 바탕으로 사용자의 모든 활동을 체계적으로 추적하고 분석할 수 있는 시스템을 구축할 수 있습니다.
