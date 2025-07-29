#!/bin/bash

# Casino-Club F2P 데이터베이스 복구 스크립트
# 작성일: 2025-07-29

# 사용법 안내
if [ $# -lt 1 ]; then
    echo "사용법: $0 <백업파일경로>"
    echo "예: $0 /var/backups/cc_webapp/cc_webapp_backup_20250729_120000.sql.gz"
    exit 1
fi

# 환경 변수 설정
DB_NAME="cc_webapp"
DB_USER="cc_user"
DB_HOST="localhost"
DB_PORT="5432"
RESTORE_LOG_DIR="/var/logs/cc_webapp"
DATE=$(date +"%Y%m%d_%H%M%S")
RESTORE_LOG="${RESTORE_LOG_DIR}/restore_log_${DATE}.log"
BACKUP_FILE=$1

# 로그 디렉토리 생성
mkdir -p ${RESTORE_LOG_DIR}

echo "===============================================" >> ${RESTORE_LOG}
echo "복구 시작: $(date)" >> ${RESTORE_LOG}
echo "복구 파일: ${BACKUP_FILE}" >> ${RESTORE_LOG}

# 백업 파일 존재 확인
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "오류: 백업 파일이 존재하지 않습니다: ${BACKUP_FILE}" >> ${RESTORE_LOG}
    echo "복구 실패: 백업 파일이 존재하지 않습니다."
    exit 1
fi

# 사용자 확인
read -p "경고: 기존 데이터베이스의 모든 데이터가 삭제됩니다. 계속 진행하시겠습니까? (y/n): " CONFIRM
if [[ "${CONFIRM}" != "y" ]]; then
    echo "복구 작업이 사용자에 의해 취소되었습니다." >> ${RESTORE_LOG}
    echo "복구 작업이 취소되었습니다."
    exit 0
fi

# 압축 파일 여부 확인 및 압축 해제
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    TEMP_FILE="/tmp/cc_webapp_restore_temp_${DATE}.sql"
    echo "압축 파일 해제 중..." >> ${RESTORE_LOG}
    gunzip -c ${BACKUP_FILE} > ${TEMP_FILE}
    RESTORE_SOURCE=${TEMP_FILE}
else
    RESTORE_SOURCE=${BACKUP_FILE}
fi

# 기존 연결 종료
echo "기존 활성 연결 종료 중..." >> ${RESTORE_LOG}
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d postgres -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '${DB_NAME}'
  AND pid <> pg_backend_pid();" >> ${RESTORE_LOG} 2>&1

# 데이터베이스 삭제 및 재생성
echo "데이터베이스 재생성 중..." >> ${RESTORE_LOG}
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};" >> ${RESTORE_LOG} 2>&1
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d postgres -c "CREATE DATABASE ${DB_NAME};" >> ${RESTORE_LOG} 2>&1

# 데이터베이스 복구
echo "백업 파일에서 데이터 복구 중..." >> ${RESTORE_LOG}
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    pg_restore -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -v ${RESTORE_SOURCE} >> ${RESTORE_LOG} 2>&1
    RESTORE_STATUS=$?
    rm ${TEMP_FILE}  # 임시 파일 삭제
else
    pg_restore -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -v ${RESTORE_SOURCE} >> ${RESTORE_LOG} 2>&1
    RESTORE_STATUS=$?
fi

# 복구 상태 확인
if [ ${RESTORE_STATUS} -eq 0 ]; then
    echo "데이터베이스 복구 성공: ${DB_NAME}" >> ${RESTORE_LOG}
    echo "데이터베이스 복구가 성공적으로 완료되었습니다!"
else
    echo "데이터베이스 복구 실패: ${DB_NAME}" >> ${RESTORE_LOG}
    echo "데이터베이스 복구 중 오류가 발생했습니다. 로그 파일을 확인하세요: ${RESTORE_LOG}"
fi

echo "복구 종료: $(date)" >> ${RESTORE_LOG}
echo "===============================================" >> ${RESTORE_LOG}
