#!/bin/bash

# Casino-Club F2P 데이터베이스 백업 스크립트
# 작성일: 2025-07-29

# 환경 변수 설정
DB_NAME="cc_webapp"
DB_USER="cc_user"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="/var/backups/cc_webapp"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/cc_webapp_backup_${DATE}.sql"
LOG_FILE="${BACKUP_DIR}/backup_log_${DATE}.log"

# 백업 디렉토리 생성
mkdir -p ${BACKUP_DIR}

echo "===============================================" >> ${LOG_FILE}
echo "백업 시작: $(date)" >> ${LOG_FILE}

# 전체 데이터베이스 백업
pg_dump -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -F c -b -v -f ${BACKUP_FILE} ${DB_NAME} >> ${LOG_FILE} 2>&1

# 백업 파일 압축
gzip ${BACKUP_FILE}

# 백업 성공 여부 확인
if [ $? -eq 0 ]; then
    echo "백업 성공: ${BACKUP_FILE}.gz" >> ${LOG_FILE}
    
    # 7일 이상 지난 백업 파일 삭제
    find ${BACKUP_DIR} -name "cc_webapp_backup_*.sql.gz" -type f -mtime +7 -delete
    echo "7일 이상 지난 백업 파일 삭제 완료" >> ${LOG_FILE}
else
    echo "백업 실패: ${BACKUP_FILE}" >> ${LOG_FILE}
    # 알림 발송 (운영 환경에서 구현)
    # mail -s "Casino-Club F2P 백업 실패 알림" admin@example.com < ${LOG_FILE}
fi

echo "백업 종료: $(date)" >> ${LOG_FILE}
echo "===============================================" >> ${LOG_FILE}

# 권한 설정
chmod 600 ${BACKUP_FILE}.gz
