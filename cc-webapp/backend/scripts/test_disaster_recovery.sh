#!/bin/bash

# Casino-Club F2P 데이터베이스 재해 복구 시나리오 테스트 스크립트
# 작성일: 2025-07-29

# 환경 변수 설정
DB_NAME="cc_webapp_test"
DB_USER="cc_user"
DB_HOST="localhost"
DB_PORT="5432"
TEST_DIR="/tmp/cc_disaster_recovery_test"
DATE=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${TEST_DIR}/dr_test_log_${DATE}.log"

# 테스트 디렉토리 생성
mkdir -p ${TEST_DIR}

echo "===============================================" | tee -a ${LOG_FILE}
echo "재해 복구 시나리오 테스트 시작: $(date)" | tee -a ${LOG_FILE}

# 1. 테스트 데이터베이스 생성
echo "1. 테스트 데이터베이스 생성 중..." | tee -a ${LOG_FILE}
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};" >> ${LOG_FILE} 2>&1
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d postgres -c "CREATE DATABASE ${DB_NAME};" >> ${LOG_FILE} 2>&1

if [ $? -ne 0 ]; then
    echo "테스트 데이터베이스 생성 실패" | tee -a ${LOG_FILE}
    exit 1
fi

# 2. 스키마 및 샘플 데이터 생성
echo "2. 스키마 및 샘플 데이터 생성 중..." | tee -a ${LOG_FILE}
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c "
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

CREATE TABLE user_segments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    rfm_group VARCHAR(50) CHECK (rfm_group IN ('Whale', 'High Engaged', 'Medium', 'Low/At-risk')),
    risk_profile VARCHAR(20) CHECK (risk_profile IN ('Low', 'Medium', 'High')),
    name VARCHAR(255)
);

CREATE INDEX idx_user_segments_user_id ON user_segments(user_id);
CREATE INDEX idx_user_segments_rfm_group ON user_segments(rfm_group);

INSERT INTO users (site_id, nickname, phone_number, password_hash, invite_code, created_at, rank)
VALUES
('site_1', 'user1', '010-1111-1111', 'hash1', 'ABC111', NOW(), 'STANDARD'),
('site_2', 'user2', '010-2222-2222', 'hash2', 'ABC222', NOW(), 'PREMIUM'),
('site_3', 'user3', '010-3333-3333', 'hash3', 'ABC333', NOW(), 'VIP');

INSERT INTO user_segments (user_id, rfm_group, risk_profile, name)
VALUES
(1, 'Medium', 'Low', 'segment_user1'),
(2, 'High Engaged', 'Medium', 'segment_user2'),
(3, 'Whale', 'High', 'segment_user3');
" >> ${LOG_FILE} 2>&1

if [ $? -ne 0 ]; then
    echo "스키마 및 샘플 데이터 생성 실패" | tee -a ${LOG_FILE}
    exit 1
fi

# 3. 백업 생성
echo "3. 백업 생성 중..." | tee -a ${LOG_FILE}
BACKUP_FILE="${TEST_DIR}/${DB_NAME}_backup_${DATE}.sql"
pg_dump -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -F c -b -v -f ${BACKUP_FILE} ${DB_NAME} >> ${LOG_FILE} 2>&1

if [ $? -ne 0 ]; then
    echo "백업 생성 실패" | tee -a ${LOG_FILE}
    exit 1
fi

# 4. 재해 시나리오: 데이터베이스 훼손 시뮬레이션
echo "4. 데이터베이스 훼손 시뮬레이션 중..." | tee -a ${LOG_FILE}
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c "
DELETE FROM user_segments;
DELETE FROM users;
" >> ${LOG_FILE} 2>&1

# 훼손 확인
USER_COUNT=$(psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -t -c "SELECT COUNT(*) FROM users;")
if [ "$USER_COUNT" -ne 0 ]; then
    echo "데이터베이스 훼손 시뮬레이션 실패: 사용자 테이블에 여전히 데이터가 있습니다" | tee -a ${LOG_FILE}
    exit 1
fi
echo "데이터베이스 훼손 성공: 모든 데이터가 삭제되었습니다" | tee -a ${LOG_FILE}

# 5. 복구 수행
echo "5. 백업에서 복구 수행 중..." | tee -a ${LOG_FILE}
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d postgres -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '${DB_NAME}'
  AND pid <> pg_backend_pid();" >> ${LOG_FILE} 2>&1
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};" >> ${LOG_FILE} 2>&1
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d postgres -c "CREATE DATABASE ${DB_NAME};" >> ${LOG_FILE} 2>&1

pg_restore -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -v ${BACKUP_FILE} >> ${LOG_FILE} 2>&1
if [ $? -ne 0 ]; then
    echo "데이터베이스 복구 실패" | tee -a ${LOG_FILE}
    exit 1
fi

# 6. 복구 검증
echo "6. 복구 결과 검증 중..." | tee -a ${LOG_FILE}
USER_COUNT=$(psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -t -c "SELECT COUNT(*) FROM users;")
SEGMENT_COUNT=$(psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -t -c "SELECT COUNT(*) FROM user_segments;")

if [ "$USER_COUNT" -eq 3 ] && [ "$SEGMENT_COUNT" -eq 3 ]; then
    echo "복구 성공: 모든 데이터가 정상적으로 복구되었습니다!" | tee -a ${LOG_FILE}
    echo "- 사용자 수: $USER_COUNT (예상: 3)" | tee -a ${LOG_FILE}
    echo "- 세그먼트 수: $SEGMENT_COUNT (예상: 3)" | tee -a ${LOG_FILE}
else
    echo "복구 실패: 데이터가 정상적으로 복구되지 않았습니다" | tee -a ${LOG_FILE}
    echo "- 사용자 수: $USER_COUNT (예상: 3)" | tee -a ${LOG_FILE}
    echo "- 세그먼트 수: $SEGMENT_COUNT (예상: 3)" | tee -a ${LOG_FILE}
    exit 1
fi

# 7. 정리
echo "7. 테스트 정리 중..." | tee -a ${LOG_FILE}
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};" >> ${LOG_FILE} 2>&1

echo "재해 복구 시나리오 테스트 완료: $(date)" | tee -a ${LOG_FILE}
echo "결과: 성공" | tee -a ${LOG_FILE}
echo "===============================================" | tee -a ${LOG_FILE}

# 로그 파일 위치 안내
echo "로그 파일: ${LOG_FILE}"
