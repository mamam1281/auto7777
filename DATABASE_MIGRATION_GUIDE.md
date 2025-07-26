# 🗄️ Casino-Club F2P 데이터베이스 마이그레이션 체크리스트

## 📋 현재 데이터베이스 상태 분석

- [x] **이전 데이터베이스**: SQLite
- [x] **현재 데이터베이스**: PostgreSQL (마이그레이션 완료)
- [x] **Docker 컨테이너**: PostgreSQL 및 Redis 실행 중
- [ ] **Redis 캐싱 설정 필요** (스트리크, 세션 관리용)

---

## 🔄 데이터베이스 마이그레이션 단계

### 1️⃣ Docker를 사용한 데이터베이스 환경 구성

- [x] **PostgreSQL 컨테이너 설정**
  - [x] docker-compose.yml 파일 생성
  - [x] 환경 변수 설정 (사용자, 비밀번호, DB 이름)
  - [x] 볼륨 설정 (데이터 영속성)
  
- [x] **Redis 컨테이너 설정** 
  - [x] docker-compose.yml에 Redis 서비스 추가
  - [x] 캐시 설정 구성
  - [x] 영구 저장소 설정 (필요시)

- [x] **컨테이너 실행 및 네트워크 설정**
  - [x] 컨테이너 간 네트워크 구성
  - [x] 포트 노출 설정 (5432, 6379)

### 2️⃣ PostgreSQL 데이터베이스 초기화

- [x] **데이터베이스 및 사용자 생성**
  - [x] cc_webapp 데이터베이스 생성
  - [x] cc_user 계정 생성 및 권한 부여
  - [x] Docker 컨테이너 내부에서 보안 설정

- [x] **스키마 생성**
  - [x] 기존 SQLite 스키마 분석
  - [x] PostgreSQL 호환 스키마로 변환
  - [x] 인덱스 및 제약 조건 설정

### 3️⃣ 데이터 마이그레이션

- [x] **마이그레이션 스크립트 작성**
  - [x] SQLite에서 데이터 추출 (export_sqlite_data.py)
  - [x] 데이터 형식 변환 (필요시)
  - [x] PostgreSQL로 데이터 삽입 (import_to_postgres.py)

- [x] **데이터 마이그레이션 실행**
  - [x] 사용자 데이터 마이그레이션 (2개 레코드)
  - [x] 초대 코드 마이그레이션 (8개 레코드)
  - [x] 기타 테이블 스키마 생성

### 4️⃣ 백엔드 애플리케이션 연결 설정

- [x] **데이터베이스 연결 설정 업데이트**
  - [x] SQLAlchemy 설정 변경 (update_database_config.py)
  - [x] 환경 변수 설정 (DATABASE_URL)
  - [x] 연결 구성 업데이트 완료

- [x] **Redis 연결 설정**
  - [x] Redis 컨테이너 구성
  - [ ] 세션 및 캐시 관리 설정
  - [ ] 환경 변수 설정 (REDIS_URL)

### 5️⃣ 테스트 및 검증

- [x] **연결 테스트**
  - [x] 백엔드에서 PostgreSQL 연결 확인
  - [ ] Redis 연결 및 캐싱 검증

- [ ] **CRUD 작업 테스트**
  - [ ] 사용자 데이터 조회/저장/수정/삭제 테스트
  - [ ] 게임 데이터 및 관련 로직 검증

- [ ] **성능 테스트**
  - [ ] 쿼리 실행 시간 측정
  - [ ] 인덱스 효율성 검증

### 6️⃣ 프로덕션 준비

- [ ] **백업 전략 구현**
  - [ ] 정기 백업 스크립트 작성
  - [ ] 복구 절차 문서화

- [ ] **모니터링 설정**
  - [ ] 데이터베이스 성능 모니터링
  - [ ] 알림 설정 (공간 부족, 성능 저하 등)

---

## 📝 세부 실행 명령어

### PostgreSQL 및 Redis 컨테이너 설정

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    container_name: ccf2p-postgres
    restart: always
    environment:
      POSTGRES_USER: ccf2p_user
      POSTGRES_PASSWORD: secure_password_here  # 실제 배포 시 변경 필요
      POSTGRES_DB: ccf2p
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ccf2p-network
      
  redis:
    image: redis:6
    container_name: ccf2p-redis
    restart: always
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - ccf2p-network

networks:
  ccf2p-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### 데이터베이스 초기화 및 마이그레이션

```bash
# PostgreSQL 컨테이너 접속
docker exec -it ccf2p-postgres bash

# psql로 연결
psql -U ccf2p_user -d ccf2p

# 테이블 생성은 Alembic 마이그레이션으로 대체

# SQLite -> PostgreSQL 마이그레이션 스크립트
# migrate_sqlite_to_postgres.py
import sqlite3
import psycopg2
import os

def migrate_sqlite_to_postgres(sqlite_file, pg_conn_string):
    """SQLite 데이터베이스에서 PostgreSQL로 데이터 마이그레이션"""
    print(f"마이그레이션 시작: {sqlite_file} -> PostgreSQL")
    
    # SQLite 연결
    sqlite_conn = sqlite3.connect(sqlite_file)
    sqlite_cursor = sqlite_conn.cursor()
    
    # PostgreSQL 연결
    pg_conn = psycopg2.connect(pg_conn_string)
    pg_cursor = pg_conn.cursor()
    
    # 테이블 목록 가져오기
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in sqlite_cursor.fetchall() 
              if table[0] != 'sqlite_sequence' and not table[0].startswith('sqlite_')]
    
    print(f"마이그레이션할 테이블: {', '.join(tables)}")
    
    for table in tables:
        # 테이블 스키마 및 데이터 추출
        sqlite_cursor.execute(f"PRAGMA table_info({table});")
        columns = sqlite_cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # 데이터 가져오기
        sqlite_cursor.execute(f"SELECT * FROM {table};")
        rows = sqlite_cursor.fetchall()
        
        if rows:
            # 데이터 삽입 준비
            placeholders = ','.join(['%s'] * len(column_names))
            columns_str = ','.join(column_names)
            
            # 데이터 삽입
            insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
            pg_cursor.executemany(insert_query, rows)
            print(f"  테이블 '{table}': {len(rows)}개 레코드 마이그레이션 완료")
        else:
            print(f"  테이블 '{table}': 데이터 없음")
    
    # 변경사항 저장
    pg_conn.commit()
    
    # 연결 종료
    sqlite_cursor.close()
    sqlite_conn.close()
    pg_cursor.close()
    pg_conn.close()
    
    print("마이그레이션 완료")
```

### 백엔드 연결 설정

```python
# .env 파일 예시
DATABASE_URL=postgresql://ccf2p_user:secure_password_here@postgres:5432/ccf2p
REDIS_URL=redis://redis:6379/0
JWT_SECRET=super_secure_jwt_secret_key_change_in_production

# SQLAlchemy 설정 예시
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis 설정 예시
import redis
import os

REDIS_URL = os.environ.get("REDIS_URL")
redis_client = redis.from_url(REDIS_URL)
```

---

## 📊 현재 진행 상황 및 다음 단계

- [x] **1. Docker 환경 구성** - docker-compose.yml 구성 완료 및 컨테이너 실행
- [x] **2. PostgreSQL 및 Redis 설정** - Docker 컨테이너에서 실행 중
- [x] **3. 스키마 마이그레이션** - 스키마 생성 및 구성 완료
- [x] **4. 데이터 마이그레이션** - SQLite 데이터를 PostgreSQL로 성공적으로 마이그레이션
- [x] **5. 백엔드 연결 설정 업데이트** - 모든 설정 파일 업데이트 완료
- [ ] **6. 테스트 및 검증** - 실제 애플리케이션 테스트 필요

---

## 📎 참고 사항

- PostgreSQL 성능 최적화를 위한 설정 검토 필요
- 프로덕션 환경 배포 시 비밀번호 등 중요 정보 보안 관리 필요
- 정기적인 데이터베이스 백업 계획 수립 필요
- 현재 마이그레이션된 데이터: 사용자 2개, 초대 코드 8개
- 연결 정보: postgresql://cc_user:cc_password@localhost/cc_webapp
