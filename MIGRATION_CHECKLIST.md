# 🚀 **통합 마이그레이션 체크리스트 (최종 버전)**

## 📊 **현재 상태 분석**

### 🖥️ **개발 환경**
- ✅ **개발 OS**: Windows 10/11 + PowerShell
- ✅ **배포 OS**: Ubuntu 22.04 LTS (Vultr Singapore)
- ✅ **개발 DB**: SQLite (로컬 테스트용)
- ✅ **운영 DB**: PostgreSQL (서버 배포용)
- ✅ **환경 설정**: .env.development + .env.production 분리

### 🔧 **백엔드 상태**
- ✅ SQLAlchemy ORM 설정 완료
- ✅ User 모델 구조 존재 (nickname, phone_number as 사이트ID, invite_code)
- ✅ Alembic 마이그레이션 시스템 설정
- ✅ 인증 시스템 구현 (auth.py, admin.py)
- ✅ 회원가입/로그인 API 구현
- ✅ 관리자 기능 완성 (유저 관리, 보상 지급)

### 🎨 **프론트엔드 상태**
- ✅ 프론트엔드 인증 컴포넌트 (RegisterForm.tsx)
- ✅ **BottomNav UI 완성** ("내역" 메뉴 적용됨)
- ⚠️ **게임 UI 개선 필요** (현재: 심플한 버튼 → 목표: 화려한 게임 허브)
- ⚠️ **보상 시스템 UI 강화 필요** (카드 기반 보상 표시)

## 🎯 **최종 시스템 구조**
- **사이트ID + 닉네임 + 실제전화번호 + 비밀번호**로 회원가입
- **전화번호는 실제 번호 저장** (인증번호 발송 없음)
- **관리자는 3가지 요소로 유저 관리**
- **즉시 가입 완료** (복잡한 인증 과정 없음)

## ⚠️ **수정 필요 사항**
- ✅ **BottomNav 캐시 문제 해결** ("월렛" → "내역" 적용 완료)
- ❌ **게임 UI 현대화** (심플 버튼 → 화려한 게임 허브)
- ❌ **보상 시스템 UI 구현** (카드 기반 보상 표시)
- ❌ **User 모델에 site_id, password_hash 필드 추가**
- ❌ **SQLite → PostgreSQL 마이그레이션**
- ❌ **서버 환경 구축 (Vultr Singapore)**
- ❌ **auth.py 비밀번호 검증 로직 활성화**

---

## 🚀 **Phase 0: Windows 개발 환경 문제 해결** (예상 소요: 30분)

### 0.1 프론트엔드 캐시 클리어
- [ ] **Next.js 캐시 삭제**
  ```bash
  # 캐시 완전 삭제
  rm -rf .next
  rm -rf node_modules/.cache
  npm run dev
  ```
- [ ] **브라우저 캐시 삭제**
  - Ctrl + Shift + R (강력 새로고침)
  - 개발자도구 > Application > Storage > Clear storage
- [ ] **BottomNav 컴포넌트 재확인 및 수정**

## 🔥 Phase 1: Vultr 서버 구축 (예상 소요: 2-3시간)

### 1.1 계정 및 서버 생성
- [ ] **Vultr 계정 생성** 
  - 이메일 인증
  - 결제 정보 등록 ($100 크레딧 활용)
- [ ] **VPS 인스턴스 생성**
  - 위치: Singapore (SGP)
  - 플랜: Regular Performance (2CPU/4GB/80GB SSD) - $30.25/월
  - **OS 선택**: **Ubuntu 22.04 LTS** (파란색 체크된 것 선택)
  - 백업 활성화: +$6/월 (권장)

### 1.2 도메인 및 DNS 설정
- [ ] **도메인 구매** (Namecheap 추천: $12/년)
- [ ] **Cloudflare DNS 설정**
  - A 레코드: your-domain.com → VPS IP
  - CNAME: www → your-domain.com
  - DDoS 보호 활성화

### 1.3 기본 보안 설정
- [ ] **SSH 키 생성 및 등록**
  ```bash
  ssh-keygen -t ed25519 -C "casino-admin"
  # 공개키를 Vultr 패널에 등록
  ```
- [ ] **방화벽 설정**
  ```bash
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw allow 5432/tcp  # PostgreSQL (특정 IP만)
  sudo ufw enable
  ```
- [ ] **Fail2Ban 설치**
  ```bash
  sudo apt install fail2ban -y
  sudo systemctl enable fail2ban
  ```

---

## 🗄️ Phase 2: PostgreSQL 설치 및 설정 (예상 소요: 1-2시간)

### 2.1 PostgreSQL 설치
- [ ] **시스템 업데이트**
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```
- [ ] **PostgreSQL 설치**
  ```bash
  sudo apt install postgresql postgresql-contrib -y
  sudo systemctl enable postgresql
  ```

### 2.2 데이터베이스 설정
- [ ] **데이터베이스 및 사용자 생성**
  ```bash
  sudo -u postgres psql
  CREATE USER casino_admin WITH PASSWORD 'secure_password_here';
  CREATE DATABASE casino_db OWNER casino_admin;
  GRANT ALL PRIVILEGES ON DATABASE casino_db TO casino_admin;
  \q
  ```
- [ ] **원격 접속 설정**
  ```bash
  # /etc/postgresql/14/main/postgresql.conf
  listen_addresses = 'localhost,YOUR_APP_SERVER_IP'
  
  # /etc/postgresql/14/main/pg_hba.conf
  host casino_db casino_admin YOUR_APP_SERVER_IP/32 md5
  ```

### 2.3 SSL 및 보안 설정
- [ ] **SSL 인증서 생성**
  ```bash
  sudo openssl req -new -x509 -days 365 -nodes -text \
    -out /etc/ssl/certs/server.crt \
    -keyout /etc/ssl/private/server.key
  ```
- [ ] **PostgreSQL SSL 활성화**
  ```bash
  # postgresql.conf
  ssl = on
  ssl_cert_file = '/etc/ssl/certs/server.crt'
  ssl_key_file = '/etc/ssl/private/server.key'
  ```

---

## 🔄 **Phase 3: 데이터베이스 모델 수정** (예상 소요: 1-2시간)

### 3.1 User 모델 확장 (핵심 작업)
- [ ] **site_id와 password_hash 필드 추가**
  ```python
  class User(Base):
      __tablename__ = "users"
      
      id = Column(Integer, primary_key=True, index=True)
      site_id = Column(String(50), unique=True, nullable=False, index=True)  # 새로 추가
      nickname = Column(String(50), unique=True, nullable=False)
      phone_number = Column(String(20), unique=True, nullable=False, index=True)  # 실제 전화번호
      password_hash = Column(String(100), nullable=False)  # 새로 추가
      invite_code = Column(String(6), nullable=False, index=True)
      cyber_token_balance = Column(Integer, default=200)
      created_at = Column(DateTime, default=datetime.utcnow)
      rank = Column(String(20), default="STANDARD", nullable=False)
  ```

### 3.2 마이그레이션 생성 및 실행
- [ ] **Alembic 마이그레이션 생성**
  ```bash
  cd cc-webapp/backend
  alembic revision --autogenerate -m "add_site_id_and_password_hash"
  ```
- [ ] **마이그레이션 실행**
  ```bash
  alembic upgrade head
  ```

### 3.3 기존 데이터 이전 (선택사항)
- [ ] **기존 SQLite 데이터 백업**
- [ ] **PostgreSQL로 데이터 이전 스크립트 작성**

---

## 🔧 **Phase 4: 백엔드 API 완성** (예상 소요: 2-3시간)

### 4.1 auth.py 수정 완료 확인
- [ ] **SignUpRequest 모델 확인**
  ```python
  class SignUpRequest(BaseModel):
      site_id: str           # 로그인용 고유 ID
      nickname: str          # 닉네임
      phone_number: str      # 실제 전화번호
      password: str          # 비밀번호
      invite_code: str       # 초대코드
  ```

- [ ] **LoginRequest 모델 확인**
  ```python
  class LoginRequest(BaseModel):
      site_id: str          # 사이트ID로 로그인
      password: str         # 비밀번호
  ```

### 4.2 회원가입 로직 수정
- [ ] **signup API 수정**
  ```python
  @router.post("/signup", response_model=TokenResponse)
  async def signup(data: SignUpRequest, db: Session = Depends(get_db)):
      # 1. 사이트ID 중복 검사
      # 2. 닉네임 중복 검사
      # 3. 실제 전화번호 중복 검사
      # 4. 초대코드 검증
      # 5. 비밀번호 해싱
      # 6. User 테이블에 즉시 저장 (site_id, password_hash 포함)
      # 7. JWT 토큰 발급
  ```

### 4.3 로그인 로직 수정
- [ ] **login API에서 비밀번호 검증 활성화**
  ```python
  @router.post("/login", response_model=TokenResponse)
  async def login(data: LoginRequest, db: Session = Depends(get_db)):
      # 1. 사이트ID로 사용자 조회
      # 2. 비밀번호 해시 검증 (현재 주석 처리된 부분 활성화)
      # 3. JWT 토큰 발급
  ```

### 4.4 관리자 API 확인
- [ ] **admin.py 기능 확인**
  - ✅ 유저 검색 (사이트ID, 닉네임, 전화번호)
  - ✅ 보상 지급 (토큰, 상품권, 아이템)
  - ✅ 보상 통계 조회
  - ✅ 유저 활동 내역 조회

### 4.5 환경 변수 설정
- [ ] **production.env 파일 생성**
  ```bash
  DATABASE_URL=postgresql://casino_admin:password@localhost:5432/casino_db
  JWT_SECRET_KEY=your_super_secret_jwt_key_here
  ENVIRONMENT=production
  ```

---

## 🎨 **Phase 5: 프론트엔드 수정** (예상 소요: 2-3시간)

### 5.1 회원가입 폼 수정
- [ ] **RegisterForm.tsx 수정**
  ```typescript
  interface RegisterFormData {
    site_id: string;        // 로그인용 고유 ID (새로 추가)
    nickname: string;       // 닉네임
    phone_number: string;   // 실제 전화번호
    password: string;       // 비밀번호 (새로 추가)
    invite_code: string;    // 초대코드
  }
  ```

### 5.2 로그인 폼 수정
- [ ] **LoginForm.tsx 수정**
  ```typescript
  interface LoginFormData {
    site_id: string;        // 사이트ID로 로그인 (변경)
    password: string;       // 비밀번호 (변경)
  }
  ```

### 5.3 입력 검증 추가
- [ ] **사이트ID 유효성 검사** (영문+숫자, 4-20자)
- [ ] **비밀번호 유효성 검사** (8자 이상, 특수문자 포함)
- [ ] **전화번호 형식 검증** (010-XXXX-XXXX)

### 5.4 UI/UX 개선
- [ ] **BottomNav 확인** ("내역" 메뉴 이미 적용됨)
- [ ] **관리자 대시보드 구현**
  - 유저 검색 기능
  - 보상 지급 폼
  - 통계 대시보드

---

## 🚀 Phase 6: 배포 및 테스트 (예상 소요: 2-3시간)

### 6.1 백엔드 배포
- [ ] **Nginx 설치 및 설정**
  ```bash
  sudo apt install nginx -y
  # 리버스 프록시 설정
  ```
- [ ] **SSL 인증서 발급** (Let's Encrypt)
  ```bash
  sudo apt install certbot python3-certbot-nginx -y
  sudo certbot --nginx -d your-domain.com
  ```
- [ ] **시스템 서비스 등록**
  ```bash
  # FastAPI 서비스를 systemd로 등록
  ```

### 6.2 프론트엔드 배포
- [ ] **Next.js 빌드 및 배포**
- [ ] **환경 변수 설정**

### 6.3 통합 테스트
- [ ] **회원가입 플로우 테스트**
  1. 사이트ID 입력
  2. 전화번호 입력
  3. 인증번호 발송/확인
  4. 닉네임 입력
  5. 가입 완료
- [ ] **로그인 테스트**
- [ ] **데이터베이스 연결 테스트**

---

## 📊 Phase 7: 모니터링 및 백업 설정 (예상 소요: 1-2시간)

### 7.1 백업 시스템 구축
- [ ] **자동 PostgreSQL 백업**
  ```bash
  # 일일 백업 스크립트 작성
  # crontab 등록
  ```
- [ ] **Vultr 스냅샷 백업 활성화**

### 7.2 모니터링 설정
- [ ] **시스템 모니터링** (htop, iostat)
- [ ] **PostgreSQL 모니터링**
- [ ] **로그 관리** (logrotate)

---

## 💰 **예상 총 비용 및 일정**

### 비용 (월별)
- **Vultr Singapore VPS**: $30.25/월 (2CPU/4GB/80GB)
- **도메인**: $1/월 (연간 $12)
- **백업**: $6/월 (VPS 백업 서비스)
- **SSL**: $0 (Let's Encrypt 무료)
- **총액: 약 $37/월**

### 일정
- **전체 작업 시간**: **10-15시간**
- **1-2일 집중 작업**으로 완료 가능

## 🎯 **우선순위 작업 순서**
1. **Vultr 서버 생성** (2-3시간)
2. **PostgreSQL 설치 및 설정** (1-2시간)
3. **User 모델에 site_id, password_hash 추가** (1시간)
4. **auth.py 비밀번호 검증 활성화** (1시간)
5. **프론트엔드 폼 수정** (2-3시간)
6. **관리자 대시보드 구현** (2-3시간)
7. **통합 테스트 및 배포** (2-3시간)

## 🛡️ **보안 및 규제 회피**
- **정부 간섭 회피도**: B+ (75/100)
- **법적 보호**: 싱가포르 법원 명령 필요
- **시간 벌기**: 6개월~2년 법적 절차
- **추가 보안**: Cloudflare + 다중 도메인

---

## 📋 **교차 검증 결과**

### ✅ **일치하는 부분**
- 사이트ID + 닉네임 + 실제전화번호 + 비밀번호 구조
- 전화번호 인증 없음 (즉시 가입)
- 관리자 3요소 검색 기능
- Vultr Singapore 서버
- PostgreSQL 데이터베이스

### 🔄 **통합된 개선사항**
- User 모델 필드 추가 (site_id, password_hash)
- auth.py 비밀번호 검증 로직 활성화
- 관리자 보상 지급 기능 완성
- 프론트엔드 폼 구조 단순화

### ⚡ **최적화된 작업 순서**
1. 서버 환경부터 구축 (안정적 기반)
2. 데이터베이스 모델 수정
3. 백엔드 API 완성
4. 프론트엔드 적용
5. 통합 테스트

**다음 단계: Vultr 계정 생성부터 시작하시겠습니까?** 🚀
