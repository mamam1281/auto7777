# 🎮 Casino-Club F2P 프로젝트

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Next.js-000000?style=flat-square&logo=next.js)](https://nextjs.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Cache](https://img.shields.io/badge/Cache-Redis-DC382D?style=flat-square&logo=redis)](https://redis.io/)
[![Message Broker](https://img.shields.io/badge/Message_Broker-Kafka-231F20?style=flat-square&logo=apache-kafka)](https://kafka.apache.org/)

Casino-Club F2P는 사용자 참여와 수익화를 극대화하기 위한 도파민 루프와 데이터 기반 개인화를 활용한 웹 기반 카지노 게임 플랫폼입니다.

## 🌟 핵심 기능

- **사용자 인증**: 초대 코드 기반 JWT 인증 시스템
- **게임 코어**: 슬롯 머신, 가챠, 룰렛 등 다양한 미니게임
- **프리미엄 경제**: 가상 화폐 및 상점 시스템
- **배틀패스 시스템**: 진행 기반 보상
- **데이터 기반 개인화**: 사용자 세분화 및 맞춤형 컨텐츠

## 🚀 시작하기

### 필수 요구사항

- Docker 및 Docker Compose 설치
- Git (저장소 클론용)
- Windows: PowerShell / Linux/Mac: Bash

### 빠른 설치

1. 저장소를 복제하고 프로젝트 디렉토리로 이동
2. Docker 환경 실행:

```powershell
# Windows에서
./docker-simple.ps1 start

# Linux/Mac에서
./docker-manage.sh start
```

3. 애플리케이션 접속:
   - 프론트엔드: http://localhost:3000
   - 백엔드 API: http://localhost:8000
   - API 문서: http://localhost:8000/docs

## 🐳 Docker 환경 관리

### Windows에서 (PowerShell)

```powershell
# 모든 컨테이너 시작
./docker-simple.ps1 start

# 컨테이너 상태 확인
./docker-simple.ps1 status

# 로그 보기
./docker-simple.ps1 logs        # 모든 로그
./docker-simple.ps1 backend     # 백엔드 로그만
./docker-simple.ps1 frontend    # 프론트엔드 로그만
./docker-simple.ps1 db          # 데이터베이스 로그만

# PostgreSQL 접속
./docker-simple.ps1 psql

# Redis CLI 접속
./docker-simple.ps1 redis-cli

# 컨테이너 bash 쉘 접속
./docker-simple.ps1 bash backend

# 모든 컨테이너 중지
./docker-simple.ps1 stop
```

### Linux/Mac에서 (Bash)

```bash
# 모든 컨테이너 시작
./docker-manage.sh start

# 컨테이너 상태 확인
./docker-manage.sh status

# 로그 보기
./docker-manage.sh logs        # 모든 로그
./docker-manage.sh logs backend # 백엔드 로그만

# PostgreSQL 접속
./docker-manage.sh psql

# Redis CLI 접속
./docker-manage.sh redis-cli

# 컨테이너 bash 쉘 접속
./docker-manage.sh bash backend

# 모든 컨테이너 중지
./docker-manage.sh stop
```

## 🏗️ 프로젝트 구조

```
cc-webapp/
├── backend/              # FastAPI 백엔드 애플리케이션
│   ├── app/              # 메인 애플리케이션 코드
│   │   ├── api/          # API 라우터
│   │   ├── core/         # 핵심 설정 및 유틸리티
│   │   ├── db/           # 데이터베이스 모델 및 세션
│   │   ├── models/       # Pydantic 모델 (스키마)
│   │   ├── services/     # 비즈니스 로직
│   │   └── main.py       # 애플리케이션 진입점
│   ├── alembic/          # 데이터베이스 마이그레이션
│   ├── tests/            # 백엔드 테스트
│   └── Dockerfile        # 백엔드 Docker 설정
├── frontend/             # Next.js 프론트엔드 애플리케이션
│   ├── app/              # 애플리케이션 라우트
│   ├── components/       # React 컴포넌트
│   ├── pages/            # Next.js 페이지
│   ├── public/           # 정적 자산
│   └── Dockerfile        # 프론트엔드 Docker 설정
├── docker-compose.yml    # 메인 Docker Compose 설정
└── docker-compose.override.yml # 개발 전용 오버라이드
```

## ⚙️ 환경 설정

애플리케이션은 환경 변수를 통해 구성됩니다. 기본값은 Docker Compose 파일에 설정되어 있지만, 프로젝트 루트에 `.env` 파일을 만들어 재정의할 수 있습니다:

```env
# 데이터베이스
DB_NAME=cc_webapp
DB_USER=cc_user
DB_PASSWORD=cc_password

# JWT 인증
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# 애플리케이션 설정
APP_ENV=development
DEBUG=true
BACKEND_PORT=8000
FRONTEND_PORT=3000

# 초기 사이버 토큰 양
INITIAL_CYBER_TOKENS=200
```

## 💻 개발 워크플로우

1. **백엔드 개발**:
   - FastAPI 프레임워크를 사용한 Python 코드
   - 백엔드 코드 변경 시 핫 리로드 (컨테이너 재시작 불필요)
   - 데이터베이스 스키마 변경 시 Alembic 마이그레이션 필요

2. **프론트엔드 개발**:
   - Next.js 및 React를 사용한 TypeScript/JavaScript 코드
   - Tailwind CSS를 통한 UI 스타일링, Framer Motion을 통한 애니메이션
   - 프론트엔드 코드 변경 시 핫 리로드

3. **데이터베이스 접근**:
   - PostgreSQL 접속: `./docker-simple.ps1 db`
   - 직접 연결: localhost:5432, 환경 변수의 자격 증명 사용

4. **테스트**:
   - 백엔드 테스트: pytest
   - 프론트엔드 테스트: Jest 및 React Testing Library

## 🔧 문제 해결

- **컨테이너가 시작되지 않음**: Docker 로그에서 오류 확인
- **데이터베이스 연결 문제**: PostgreSQL 컨테이너 실행 및 상태 확인
- **백엔드 API 오류**: 백엔드 로그에서 Python 예외 확인
- **프론트엔드 빌드 실패**: 프론트엔드 로그에서 컴파일 오류 확인

## 📚 추가 리소스

- [프로젝트 설정 가이드](./PROJECT_SETUP_GUIDE.md)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Next.js 문서](https://nextjs.org/docs)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
