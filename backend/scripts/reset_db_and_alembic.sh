#!/bin/bash
# 파일명: reset_db_and_alembic.sh
# Casino-Club F2P 프로젝트 - DB 테이블 정리 및 Alembic 마이그레이션 초기화 스크립트
# 사용 전 반드시 백업을 진행하세요!

# 환경 변수 설정
DB_NAME="cc_webapp"
DB_USER="cc_user"
DB_HOST="localhost"
DB_PORT="5432"
ALEMBIC_DIR="../app/migrations"

# 1. 기존 테이블 전체 삭제 (PostgreSQL)
echo "[1] 모든 테이블 삭제 중..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DO $$ DECLARE r RECORD; BEGIN FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE'; END LOOP; END $$;"

# 2. Alembic 마이그레이션 히스토리 초기화
echo "[2] Alembic 마이그레이션 디렉토리 초기화 중..."
rm -rf $ALEMBIC_DIR/versions/*

# 3. 새로운 마이그레이션 생성 및 적용
echo "[3] 새로운 마이그레이션 생성 및 적용..."
cd ../app
alembic revision --autogenerate -m "init"
alembic upgrade head

# 4. 완료 안내
echo "DB 테이블 정리 및 Alembic 마이그레이션 초기화가 완료되었습니다."
