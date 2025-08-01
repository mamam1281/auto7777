# 게임 라우터 인증 시스템 통합 구현

## 개요

이 작업은 게임 API 엔드포인트들에 인증 시스템을 통합하여 보안을 강화하는 것이 목적입니다. JWT 토큰 기반 인증을 사용하여 모든 게임 API가 인증된 사용자만 접근할 수 있도록 구현하였습니다.

## 구현 내용

### 1. 기존 games.py 라우터 업데이트

- 기존의 하드코딩된 사용자 ID 제거
- `require_user` 의존성 주입을 통한 인증 시스템 통합
- 모든 게임 엔드포인트에 인증 적용 (슬롯, 룰렛, 가챠, 가위바위보)

### 2. 새로운 game_api_v2.py 라우터 구현

- 종합적인 게임 API 인터페이스 제공
- 인증 시스템 완전 통합
- 게임 세션 기록 기능 추가
- 상세한 API 문서화 
- 게임 통계 API 추가
- 향후 확장성을 고려한 구조 설계

### 3. main.py 통합

- 기존 games.py 라우터 유지 (기존 코드 호환성)
- 새로운 game_api_v2.py 라우터 추가 (향후 사용)
- 모든 게임 API에 인증 시스템 적용

## API 엔드포인트

### 기존 게임 API (인증 적용됨)

- **POST /api/games/slot/spin**: 슬롯 머신 스핀
- **POST /api/games/roulette/spin**: 경품 룰렛 스핀
- **GET /api/games/roulette/info**: 룰렛 정보 조회
- **POST /api/games/gacha/pull**: 가챠 뽑기
- **POST /api/games/rps/play**: 가위바위보 게임

### 새로운 게임 API V2 (인증 적용됨)

- **POST /api/games/slot/spin**: 슬롯 머신 스핀
- **POST /api/games/roulette/spin**: 경품 룰렛 스핀
- **GET /api/games/roulette/info**: 룰렛 정보 조회
- **POST /api/games/gacha/pull**: 가챠 뽑기
- **POST /api/games/rps/play**: 가위바위보 게임
- **GET /api/games/stats**: 게임 통계 조회 (신규)

## 인증 방법

1. `/api/auth/login` 엔드포인트로 로그인하여 JWT 토큰 획득
2. 모든 게임 API 요청 시 Authorization 헤더에 `Bearer {token}` 형태로 토큰 전송
3. 유효한 토큰이 없으면 401 Unauthorized 오류 반환

## 테스트 방법

1. 먼저 인증 API로 로그인하여 토큰 발급:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"site_id": "test_user", "password": "test_password"}'
```

2. 발급받은 토큰을 사용하여 게임 API 호출:

```bash
curl -X POST "http://localhost:8000/api/games/slot/spin" \
     -H "Authorization: Bearer {your_token}"
```

## 향후 개선사항

- 사용자별 게임 통계 저장 및 조회 기능 구현
- 토큰 리프레시 기능 통합
- 추가 게임 타입 지원 및 확장
- 게임 세션 로깅 시스템 완성
