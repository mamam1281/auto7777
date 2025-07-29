# Casino-Club F2P 데이터베이스 운영 매뉴얼

## 1. 개요

이 문서는 Casino-Club F2P 프로젝트의 데이터베이스 운영에 관한 매뉴얼입니다. 데이터베이스 관리, 백업, 복구, 모니터링, 성능 최적화, 트러블슈팅에 대한 지침을 포함합니다.

**문서 버전:** 1.0.0
**최종 업데이트:** 2025-07-29
**작성자:** Casino-Club F2P 개발팀

## 2. 데이터베이스 구성

### 2.1. 데이터베이스 정보

- **DBMS:** PostgreSQL 13
- **데이터베이스명:** cc_webapp
- **접속 정보:**
  - 개발 환경: localhost:5432
  - 스테이징 환경: stage-db.casino-club-f2p.com:5432
  - 운영 환경: db.casino-club-f2p.com:5432

### 2.2. 주요 테이블 구조

#### users 테이블
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    site_id VARCHAR(255) NOT NULL,
    nickname VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    password_hash VARCHAR(255),
    invite_code VARCHAR(50),
    created_at TIMESTAMP NOT NULL,
    rank VARCHAR(20) CHECK (rank IN ('STANDARD', 'PREMIUM', 'VIP'))
);

CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_rank ON users(rank);
CREATE INDEX idx_users_invite_code ON users(invite_code);
```

#### user_segments 테이블
```sql
CREATE TABLE user_segments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    rfm_group VARCHAR(50) CHECK (rfm_group IN ('Whale', 'High Engaged', 'Medium', 'Low/At-risk')),
    risk_profile VARCHAR(20) CHECK (risk_profile IN ('Low', 'Medium', 'High')),
    name VARCHAR(255)
);

CREATE INDEX idx_user_segments_user_id ON user_segments(user_id);
CREATE INDEX idx_user_segments_rfm_group ON user_segments(rfm_group);
CREATE INDEX idx_user_segments_risk_profile ON user_segments(risk_profile);
```

#### user_actions 테이블
```sql
CREATE TABLE user_actions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(50) CHECK (action_type IN ('LOGIN', 'SLOT_SPIN', 'GACHA_SPIN')),
    timestamp TIMESTAMP NOT NULL,
    value FLOAT
);

CREATE INDEX idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX idx_user_actions_action_type ON user_actions(action_type);
CREATE INDEX idx_user_actions_timestamp ON user_actions(timestamp);
CREATE INDEX idx_user_actions_user_action_type ON user_actions(user_id, action_type);
CREATE INDEX idx_user_actions_user_timestamp ON user_actions(user_id, timestamp);
```

## 3. 일상적인 데이터베이스 작업

### 3.1. 데이터베이스 접속

```bash
# 개발 환경
psql -h localhost -p 5432 -U cc_user -d cc_webapp

# 운영 환경
psql -h db.casino-club-f2p.com -p 5432 -U cc_user -d cc_webapp
```

### 3.2. 백업 및 복구

#### 백업 생성
자동 백업이 매일 02:00 AM에 실행됩니다. 수동 백업이 필요한 경우:

```bash
# 백업 스크립트 실행
/path/to/scripts/db_backup.sh
```

백업 파일은 `/var/backups/cc_webapp/`에 저장됩니다.

#### 데이터베이스 복구

```bash
# 복구 스크립트 실행 (백업 파일 경로 지정)
/path/to/scripts/db_restore.sh /var/backups/cc_webapp/cc_webapp_backup_20250729_120000.sql.gz
```

### 3.3. 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 스키마 마이그레이션을 관리합니다:

```bash
# 현재 마이그레이션 버전 확인
alembic current

# 최신 버전으로 마이그레이션
alembic upgrade head

# 특정 버전으로 마이그레이션
alembic upgrade <revision>

# 이전 버전으로 롤백
alembic downgrade <revision>
```

## 4. 모니터링 및 관리

### 4.1. 데이터베이스 모니터링

**주요 모니터링 지표:**
- 연결 수
- 캐시 히트율
- 디스크 사용량
- 쿼리 실행 시간
- 테이블 및 인덱스 크기

**모니터링 도구:**
- PostgreSQL 내장 통계 뷰 (pg_stat_activity, pg_stat_database)
- Grafana 대시보드 (http://monitoring.casino-club-f2p.com/grafana)
- Prometheus 메트릭 수집

### 4.2. 느린 쿼리 분석

느린 쿼리 로그는 `/var/log/postgresql/postgresql-slow.log`에 저장됩니다.

```sql
-- 현재 실행 중인 쿼리 확인
SELECT pid, age(clock_timestamp(), query_start), usename, query
FROM pg_stat_activity
WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%'
ORDER BY query_start desc;

-- 특정 쿼리 강제 종료
SELECT pg_cancel_backend(<pid>);
```

### 4.3. 인덱스 관리

```sql
-- 인덱스 사용 현황 확인
SELECT 
    idstat.relname AS table_name,
    indexrelname AS index_name,
    idstat.idx_scan AS index_scans_count,
    pg_size_pretty(pg_relation_size(idstat.relid)) AS table_size,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    n_tup_upd + n_tup_ins + n_tup_del as writes,
    n_tup_ins as inserts
FROM pg_stat_user_indexes AS idstat
JOIN pg_stat_user_tables AS tabstat ON idstat.relid = tabstat.relid
ORDER BY idstat.idx_scan DESC;

-- 테이블 재구성 및 인덱스 리빌드
VACUUM FULL ANALYZE <table_name>;
REINDEX TABLE <table_name>;
```

## 5. 트러블슈팅

### 5.1. 일반적인 문제 해결

#### 연결 문제
- 방화벽 설정 확인
- pg_hba.conf 파일의 접근 제어 설정 확인
- PostgreSQL 서비스 상태 확인: `systemctl status postgresql`

#### 디스크 공간 부족
- 로그 파일 정리: `find /var/log/postgresql -name "*.log" -mtime +7 -exec rm {} \;`
- 불필요한 백업 파일 정리
- VACUUM FULL 실행으로 디스크 공간 확보

#### 성능 저하
- 인덱스 확인 및 최적화
- 쿼리 튜닝
- PostgreSQL 설정 조정 (shared_buffers, work_mem, effective_cache_size)

### 5.2. 긴급 상황 대응

#### 서비스 중단 시
1. 로그 파일 확인: `/var/log/postgresql/postgresql.log`
2. 데이터베이스 서비스 재시작: `systemctl restart postgresql`
3. 연결 및 기본 쿼리 테스트
4. 상황 기록 및 근본 원인 분석

#### 데이터 손상 시
1. 즉시 백업에서 복구: `/path/to/scripts/db_restore.sh <최신백업파일경로>`
2. 데이터 일관성 검증
3. 애플리케이션 서비스 재시작

## 6. 성능 최적화

### 6.1. 인덱스 전략

사용자 ID, 생성 시간, 액션 타입 등 자주 조회되는 컬럼에 적절한 인덱스를 유지합니다:

- 단일 컬럼 인덱스: 간단한 WHERE 절에 사용
- 복합 인덱스: 여러 조건이 함께 사용되는 경우 (예: user_id + action_type)
- 부분 인덱스: 특정 조건에 해당하는 행만 인덱싱 (예: 활성 사용자만)

### 6.2. 주요 쿼리 최적화

자주 실행되는 쿼리에 대해 `EXPLAIN ANALYZE`를 사용하여 실행 계획을 분석하고 최적화합니다:

```sql
EXPLAIN ANALYZE 
SELECT * FROM user_actions 
WHERE user_id = 123 AND action_type = 'LOGIN' 
ORDER BY timestamp DESC 
LIMIT 10;
```

### 6.3. 파티셔닝 전략

대용량 테이블(user_actions)에 대해 시간 기반 파티셔닝을 적용하여 성능을 향상시킵니다:

```sql
-- 예시: 월별 파티셔닝
CREATE TABLE user_actions (
    id SERIAL,
    user_id INTEGER,
    action_type VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    value FLOAT
) PARTITION BY RANGE (timestamp);

-- 월별 파티션 생성
CREATE TABLE user_actions_y2025m07 PARTITION OF user_actions
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE user_actions_y2025m08 PARTITION OF user_actions
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
```

## 7. 참조 정보

### 7.1. 데이터베이스 접속 정보

| 환경 | 호스트 | 포트 | 사용자 | 데이터베이스 |
|-----|-------|-----|-------|-----------|
| 개발 | localhost | 5432 | cc_user | cc_webapp |
| 스테이징 | stage-db.casino-club-f2p.com | 5432 | cc_user | cc_webapp |
| 운영 | db.casino-club-f2p.com | 5432 | cc_user | cc_webapp |

### 7.2. 유용한 명령어

```bash
# 데이터베이스 크기 확인
psql -c "SELECT pg_size_pretty(pg_database_size('cc_webapp'));"

# 테이블 크기 확인
psql -c "SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC;"

# 락 상태 확인
psql -c "SELECT locktype, relation::regclass, mode, pid FROM pg_locks WHERE NOT GRANTED;"

# 활성 연결 확인
psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
```

## 8. 변경 이력

| 날짜 | 버전 | 설명 | 담당자 |
|-----|-----|-----|------|
| 2025-07-29 | 1.0.0 | 초기 문서 작성 | 개발자 JIMIN |
