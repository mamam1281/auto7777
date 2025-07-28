# Casino-Club F2P 실행 가이드

## 📋 고정 환경 변수 설정

프로젝트 경로가 고정되어 있어 별도 환경변수 설정 없이 바로 실행 가능합니다.

**고정 경로:**
- PROJECT_ROOT: `c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp`
- BACKEND_PATH: `c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp\backend`
- FRONTEND_PATH: `c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp\frontend`

## 🚀 실행 명령어 (Windows)

### 🔥 원클릭 실행 (추천)

**전체 메뉴 실행:**
```cmd
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
start-all.bat
```

**PowerShell 버전:**
```powershell
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
.\start-all.ps1
```

### 🔧 개별 실행

**백엔드만 실행:**
```cmd
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
start-backend.bat
```

**프론트엔드만 실행:**
```cmd
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
start-frontend.bat
```

**개발 도구:**
```cmd
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
dev-tools.bat
```

### 🎯 PowerShell 실행 (고급)

**PowerShell 실행 정책 설정 (최초 1회):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**백엔드 실행:**
```powershell
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
.\start-backend.ps1
```

**프론트엔드 실행:**
```powershell
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
.\start-frontend.ps1
```

## 📊 접속 URL

- **프론트엔드**: http://localhost:3000
- **관리자 페이지**: http://localhost:3000/admin
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 🔑 기본 계정

**관리자 계정:**
- 사용자명: `admin`
- 비밀번호: `admin123`

## 🛠️ 개발 도구 명령어

### 백엔드 도구
```cmd
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp\backend
call venv\Scripts\activate.bat
pytest                    # 테스트 실행
python create_admin.py     # 관리자 계정 생성
```

### 프론트엔드 도구
```cmd
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp\frontend
npm test                   # 테스트 실행
npm run lint              # 린트 검사
npm run type-check        # 타입 체크
npm run build             # 빌드 테스트
```

## 🔄 수동 설치 명령어

### 백엔드 수동 설치
```cmd
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp\backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python create_admin.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 수동 설치
```cmd
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp\frontend
npm install
npm run dev
```

## ⚡ 빠른 시작 (3단계)

1. **스크립트 실행:**
   ```cmd
   cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
   start-all.bat
   ```

2. **메뉴에서 "3" 선택** (전체 실행)

3. **브라우저에서 접속:**
   - http://localhost:3000 (메인 사이트)
   - http://localhost:3000/admin (관리자, admin/admin123)

## 🐳 Docker 실행 (선택사항)

```cmd
cd c:\Users\bdbd\Downloads\250724\auto7777\cc-webapp
docker-compose up --build
```

모든 스크립트는 고정 경로로 설정되어 있어 추가 환경변수 설정 없이 바로 실행 가능합니다!
