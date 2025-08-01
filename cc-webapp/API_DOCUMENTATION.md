# Casino-Club F2P API Documentation

이 문서는 Casino-Club F2P 시스템의 모든 API 엔드포인트를 정리한 것입니다. 프론트엔드와 백엔드 간의 API 일관성을 유지하기 위한 참조 문서로 활용하세요.

## 1. 인증 API (`## 5. 사용자 API (프론트엔드 구현)

### 잔액 관리
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/user/sync-balance` | POST | `{ balance: number }` | - | 프론트엔드에서 백엔드로 잔액 동기화 |

## 6. 데이터베이스 API 및 구성

### 데이터베이스 접근
Casino-Club F2P 프로젝트는 다음과 같은 데이터베이스 설정을 사용합니다:

1. **프로덕션 환경**: PostgreSQL (Docker 기반)
   - 환경변수를 통한 연결 설정:
     - `DB_HOST`: 데이터베이스 호스트 (기본값: localhost)
     - `DB_PORT`: 데이터베이스 포트 (기본값: 5432)
     - `DB_NAME`: 데이터베이스 이름 (기본값: cc_webapp)
     - `DB_USER`: 데이터베이스 사용자 (기본값: cc_user)
     - `DB_PASSWORD`: 데이터베이스 비밀번호 (기본값: cc_password)

2. **개발 환경**: SQLite (폴백 옵션)
   - 기본 경로: `./auth.db` 또는 `./fallback.db`

### 주요 데이터 모델

#### User 모델
- `id`: 사용자 고유 ID (PK)
- `site_id`: 사용자 사이트 ID (unique)
- `nickname`: 닉네임 (unique)
- `phone_number`: 전화번호 (unique)
- `email`: 이메일 (optional, unique)
- `password_hash`: 비밀번호 해시
- `invite_code`: 초대 코드
- `cyber_token_balance`: 사이버 토큰 잔액 (기본값: 200)
- `premium_gems`: 프리미엄 젬 (기본값: 0)
- `rank`: 사용자 등급 (STANDARD, VIP, PREMIUM)
- `vip_tier`: VIP 등급
- `experience_points`: 경험치
- `battlepass_level`: 배틀패스 레벨
- `created_at`: 계정 생성 시간
- `last_login_at`: 최근 로그인 시간

#### 연관 모델
- `LoginAttempt`: 로그인 시도 기록
- `RefreshToken`: 리프레시 토큰 관리
- `UserSession`: 사용자 세션 관리
- `SecurityEvent`: 보안 이벤트 로깅
- `UserAction`: 사용자 액션 기록
- `UserReward`: 사용자 보상 기록
- `GameSession`: 게임 세션 기록
- `UserActivity`: 사용자 활동 기록

### 데이터베이스 접근 방식
모든 API 엔드포인트는 FastAPI 의존성 주입을 통해 데이터베이스에 접근:

```python
def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## API 일관성 이슈:h`)

### 회원가입 및 로그인
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/api/auth/signup` | POST | `SignUpRequest` (site_id, nickname, phone_number, password, invite_code) | `TokenResponse` (access_token, refresh_token) | 초대 코드로 새 사용자 등록 |
| `/api/auth/login` | POST | `LoginRequest` (site_id, password) | `TokenResponse` (access_token, refresh_token) | 사용자 로그인 (시도 제한 포함) |
| `/api/auth/verify-invite` | POST | `{ code: string }` | `{ valid: boolean, message?: string }` | 초대 코드 유효성 검증 |
| `/api/auth/me` | GET | - | `UserInfo` (id, site_id, nickname, phone_number, cyber_token_balance, rank, last_login_at) | 현재 사용자 정보 조회 |
| `/api/auth/refresh` | POST | `RefreshTokenRequest` (refresh_token) | `TokenResponse` (access_token, refresh_token) | 액세스 토큰 갱신 |
| `/api/auth/logout` | POST | - | `{ message: string }` | 현재 세션 로그아웃 |
| `/api/auth/logout-all` | POST | - | `{ message: string }` | 모든 세션에서 로그아웃 |

### 프론트엔드 구현 코드
```typescript
export const authAPI = {
  login: (data: LoginRequest) => 
    apiClient.post<{ access_token: string; user: User }>('/api/auth/login', data),
  
  register: (data: SignUpRequest) => 
    apiClient.post<{ access_token: string; user: User }>('/api/auth/signup', data),
  
  getCurrentUser: () => 
    apiClient.get<User>('/api/auth/me'),
    
  checkInviteCode: (code: string) => 
    apiClient.post<{ valid: boolean; message?: string }>('/api/auth/verify-invite', { code }),
};
```

## 2. 관리자 API (`/admin`)

### 사용자 관리
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/admin/users` | GET | `skip?: number, limit?: number, search?: string` | `List[UserAdminResponse]` | 모든 사용자 목록 조회 (관리자 대시보드용) |
| `/admin/users/{user_id}` | GET | - | `UserDetailResponse` (id, site_id, nickname, phone_number, rank, cyber_token_balance, created_at, activities[], rewards[]) | 특정 사용자 상세 정보 조회 |
| `/admin/activities` | GET | `skip?: number, limit?: number` | `List[ActivityResponse]` | 최근 사용자 활동 내역 조회 |
| `/admin/users/{user_id}/reward` | POST | `GiveRewardRequest` (reward_type, amount, reason) | `RewardResponse` | 특정 사용자에게 보상 지급 |

### 권한 필요
- 모든 관리자 API는 `require_admin_user` 의존성을 통해 인증된 관리자 사용자만 접근 가능
- `"rank"` 속성이 `"ADMIN"` 또는 `"PREMIUM"`인 사용자만 접근 가능

## 3. 게임 API (`/games` 프론트엔드, `/api/games` 백엔드)

### 슬롯머신
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/games/slot/spin` | POST | `{ bet_amount: number }` | `SlotSpinResponse` (result, tokens_change, balance, streak, animation) | 베팅 금액으로 슬롯머신 스핀 |

### 경품 룰렛
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/api/games/roulette/spin` | POST | - | `PrizeRouletteSpinResponse` (success, prize, message, spins_left, cooldown_expires) | 경품 룰렛 스핀 |
| `/api/games/roulette/info` | GET | - | `PrizeRouletteInfoResponse` (spins_left, prizes, max_daily_spins) | 룰렛 정보 및 상품 조회 |

### 가챠 시스템
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/api/games/gacha/pull` | POST | `GachaPullRequest` (count) | `GachaPullResponse` (results, tokens_change, balance) | 가챠 뽑기 (횟수 지정) |
| `/gacha/pull` | POST | `{ user_id: number }` | `GachaPullResponseItem` (type, amount?, stage?, badge_name?, message?) | 대체 가챠 뽑기 엔드포인트 |
| `/gacha/config` | GET | - | `GachaConfig` (rarity_table, reward_pool) | 가챠 설정 조회 |
| `/gacha/config` | PUT | `GachaConfig` (rarity_table, reward_pool) | `GachaConfig` | 가챠 설정 업데이트 |

### 가위바위보
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/api/games/rps/play` | POST | `RPSPlayRequest` (choice, bet_amount) | `RPSPlayResponse` (user_choice, computer_choice, result, tokens_change, balance) | 가위바위보 게임 플레이 |

### 프론트엔드 구현 코드
```typescript
export const gameAPI = {
  getGames: () => 
    apiClient.get<GameResponse[]>('/games/'),
  
  playGame: (data: GamePlayRequest) => 
    apiClient.post('/games/play', data),
    
  // 슬롯 머신 스핀 API
  spinSlot: (betAmount: number = 2) => 
    apiClient.post<SlotSpinResponse>('/games/slot/spin', { bet_amount: betAmount }),
  
  // 잔액 동기화 API (프론트엔드 → 백엔드)
  syncBalance: (balance: number) => 
    apiClient.post('/user/sync-balance', { balance }),
    
  // 슬롯 머신 임의 스핀 API (프론트엔드 로직 사용)
  mockSpinSlot: (betAmount: number, reels: string[], result: any) => {
    // 프론트엔드 로직 기반 응답 생성
    // 백엔드와 동일한 인터페이스를 유지하지만 실제로는 프론트엔드 로직 사용
    const response: SlotSpinResponse = {
      result: result.isWin ? (result.type === 'jackpot' ? 'jackpot' : 'win') : 'lose',
      tokens_change: result.isWin ? result.payout - betAmount : -betAmount,
      balance: 0, // 클라이언트에서 업데이트
      streak: result.isWin ? 0 : 1, // 임시값, 클라이언트에서 관리
      animation: result.isWin ? 
        (result.type === 'jackpot' ? 'jackpot' : 'win') : 
        (Math.random() < 0.8 ? 'near_miss' : 'lose')
    };
    
    return Promise.resolve({ data: response });
  }
};
```

## 3. 성인 콘텐츠 API (`/adult-content` 프론트엔드, `/v1/adult` 백엔드)

### 콘텐츠 갤러리 및 상세 정보
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/adult-content/gallery` | GET | - | `{ items: AdultContentGalleryItem[] }` | 성인 콘텐츠 갤러리 조회 |
| `/v1/adult/gallery` | GET | - | `AdultContentGalleryResponse` (items) | 백엔드 성인 콘텐츠 갤러리 |
| `/v1/adult/content/preview` | GET | - | `{ items: [] }` | 콘텐츠 갤러리 미리보기 |
| `/v1/adult/{content_id}` | GET | - | `AdultContentDetail` | 콘텐츠 상세 정보 |
| `/v1/adult/{content_id}/preview` | GET | - | `ContentPreviewResponse` | 콘텐츠 미리보기 |

### 콘텐츠 잠금해제
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/adult-content/unlock` | POST | `ContentUnlockRequest` (content_id, stage_to_unlock) | `ContentUnlockResponse` | 콘텐츠 스테이지 잠금해제 |
| `/v1/adult/unlock` | POST | `ContentUnlockRequestNew` (content_id, stage_to_unlock) | `ContentUnlockResponse` | 백엔드 콘텐츠 잠금해제 |
| `/v1/adult/content/unlock` | POST | `{ stage: number, tokens_to_spend: number }` | `{ success: boolean, stage: number, content_url: string }` | 토큰으로 잠금해제 |
| `/v1/adult/unlock/history` | GET | - | `UnlockHistoryResponse` | 잠금해제 이력 조회 |
| `/v1/adult/my-unlocks` | GET | - | `UnlockHistoryResponse` | 사용자 잠금해제 이력 |
| `/v1/adult/upgrade-access` | POST | `AccessUpgradeRequest` | `AccessUpgradeResponse` | 임시 접근 권한 업그레이드 |

### VIP 및 플래시 오퍼
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/adult-content/flash-offers` | GET | - | `{ offers: FlashOfferResponseItem[] }` | 플래시 오퍼 조회 |
| `/v1/adult/vip/info` | GET | - | `{ vip_status: string, expires_at: string }` | VIP 정보 조회 |
| `/v1/adult/flash-offers/active` | GET | - | `{ offers: [] }` | 활성화된 플래시 오퍼 조회 |
| `/v1/adult/flash-offers/purchase` | POST | `{ offer_id: number }` | `{ success: boolean, offer_id: number }` | 플래시 오퍼 구매 |

### 프론트엔드 구현 코드
```typescript
export const adultContentAPI = {
  getGallery: () => 
    apiClient.get<{ items: AdultContentGalleryItem[] }>('/adult-content/gallery'),
  
  unlockContent: (data: ContentUnlockRequest) => 
    apiClient.post<ContentUnlockResponse>('/adult-content/unlock', data),
  
  getFlashOffers: () => 
    apiClient.get<{ offers: FlashOfferResponseItem[] }>('/adult-content/flash-offers'),
};
```

## 4. 사용자 API (프론트엔드 구현)

### 잔액 관리
| 엔드포인트 | 메서드 | 요청 | 응답 | 설명 |
|---------|--------|---------|----------|-------------|
| `/user/sync-balance` | POST | `{ balance: number }` | - | 프론트엔드에서 백엔드로 잔액 동기화 |

## API 일관성 이슈:

1. **경로 불일치**:
   - 프론트엔드는 `/adult-content/*` 사용, 백엔드는 `/v1/adult/*` 사용
   - 일부 엔드포인트는 살짝 다른 경로로 중복 구현됨
   - 프론트엔드는 `/games/*`, 백엔드는 `/api/games/*` 경로 사용

2. **함수명 불일치**:
   - 프론트엔드 코드에서 `apiClient.getMe()`가 참조되지만 실제 구현은 `authAPI.getCurrentUser()`

## 인증 흐름:

1. 사용자가 초대 코드로 `/api/auth/signup`을 통해 회원가입
2. 사용자가 `/api/auth/login`을 통해 로그인하여 JWT 토큰 수신
3. 프론트엔드는 요청 시 Bearer 인증으로 토큰 포함
4. 액세스 토큰 만료 시 `/api/auth/refresh`로 토큰 갱신
5. 사용자 정보는 `/api/auth/me`를 통해 조회

## 핵심 모델:

### User
```typescript
export interface User {
  id: number;
  email: string;
  nickname?: string;
  cyber_token_balance: number;
  segment_label: string;
  created_at: string;
}
```

### SlotSpinResponse
```typescript
export interface SlotSpinResponse {
  result: string;        // 'win', 'lose', 'jackpot'
  tokens_change: number; // 보상 또는 차감된 토큰 수 (음수면 차감, 양수면 보상)
  balance: number;       // 업데이트 후 잔액
  streak: number;        // 연속 패배 횟수
  animation: string;     // 'win', 'lose', 'jackpot', 'force_win', 'near_miss' 등의 애니메이션 타입
}
```

### AdultContentGalleryItem
```typescript
export interface AdultContentGalleryItem {
  id: number;
  name: string;
  title: string;
  description: string;
  thumbnail_url: string;
  preview_url: string;
  content_type: string;
  stage_required: string;
  highest_unlocked_stage?: string;
  is_unlocked: boolean;
}
```

### 요청 타입
```typescript
export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignUpRequest {
  site_id: string;
  nickname: string;
  phone_number: string;
  password: string;
  invite_code: string;
}

export interface ContentUnlockRequest {
  content_id: number;
  stage_to_unlock: number;
}
```

## Docker 배포 요구사항:

애플리케이션은 docker-compose로 구성되어야 하며, 세 가지 주요 컴포넌트로 구성됩니다:
1. 백엔드 API 서버 (FastAPI + Python)
2. 프론트엔드 웹 앱 서버 (Next.js)
3. 데이터베이스 서버 (PostgreSQL)

## 주요 데이터베이스 테이블:
- users (사용자)
- user_segments (사용자 세그먼트)
- user_actions (사용자 행동)
- user_rewards (사용자 보상)
- gacha_log (가챠 로그)
- shop_transactions (상점 거래)
- battlepass_status (배틀패스 상태)
- invite_codes (초대 코드)

이 API 문서를 활용하여 모든 엔드포인트를 검증하고 프론트엔드와 백엔드 구현 간의 일관성을 유지하세요.
