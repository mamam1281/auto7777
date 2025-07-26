# Casino-Club F2P 프로젝트

## 🎮 프로젝트 개요

Casino-Club F2P는 단순한 초대코드 기반 인증과 랭크 시스템을 갖춘 웹 기반 게임 플랫폼입니다. Clean Architecture 원칙에 따라 설계되었으며, FastAPI 백엔드와 Next.js 프론트엔드로 구성되어 있습니다.

## 🛠️ 주요 기능

- **단순한 인증 시스템**: 초대코드 + 닉네임만으로 즉시 가입
- **랭크 기반 권한 제어**: VIP/PREMIUM/STANDARD 3단계 시스템
- **확률 기반 게임**: 슬롯머신, 룰렛, 가위바위보 등 확률형 게임
- **가챠 시스템**: Variable-Ratio 보상 시스템
- **세그먼테이션**: RFM 분석 기반 사용자 세그먼테이션

## 🚀 시작하기

### 요구 사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- SQLite (기본 내장)

### 설치 및 실행

1. **프로젝트 초기화**

   ```bash
   python setup_project.py
   ```

   이 스크립트는 다음과 같은 작업을 수행합니다:
   - 필요한 패키지 설치
   - 데이터베이스 초기화
   - 고정 초대코드 생성 (5882, 6969, 6974)

2. **서버 실행**

   ```bash
   python run_server.py
   ```

   서버가 시작되면 다음 주소로 접근할 수 있습니다:
   - API 문서: http://localhost:8000/docs
   - 백엔드 서버: http://localhost:8000

3. **VSCode에서 실행 (권장)**

   VSCode에서는 `.vscode/tasks.json`에 정의된 태스크를 사용할 수 있습니다:
   - `Setup Casino-Club F2P`: 프로젝트 초기화 (Ctrl+Shift+B)
   - `Run Casino-Club F2P Server`: 서버 실행

## 📝 API 사용 예시

### 1. 초대코드 유효성 검사

```bash
curl -X GET "http://localhost:8000/api/auth/check-invite/5882"
```

### 2. 회원가입

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"invite_code": "5882", "nickname": "테스터1"}'
```

### 3. 초대코드 목록 조회

```bash
curl -X GET "http://localhost:8000/api/auth/invite-codes"
```

## 🧪 테스트 실행

```bash
cd cc-webapp/backend
pytest tests/
```

## 📦 프로젝트 구조

```
cc-webapp/
├── backend/           # FastAPI 백엔드
│   ├── app/           # 메인 어플리케이션
│   │   ├── auth/      # 인증 관련 코드
│   │   ├── models/    # 데이터베이스 모델
│   │   ├── routers/   # API 엔드포인트
│   │   ├── schemas/   # Pydantic 스키마
│   │   ├── services/  # 비즈니스 로직
│   │   └── main.py    # FastAPI 앱 설정
│   └── tests/         # 테스트 코드
└── frontend/          # Next.js 프론트엔드
```

## 📄 라이센스

Copyright (c) 2025

## 👥 기여하기

이슈와 풀 리퀘스트는 언제나 환영합니다!
