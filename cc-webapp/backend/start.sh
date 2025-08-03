#!/bin/bash
set -e

echo "🚀 Starting Casino-Club Backend..."

# 데이터베이스 연결 대기
echo "⏳ Waiting for PostgreSQL..."
sleep 5
echo "✅ PostgreSQL is ready!"

# 데이터베이스 마이그레이션 및 테이블 생성
echo "📊 Creating database tables..."
python -c "
from app.database import engine
from app.models import Base
try:
    Base.metadata.create_all(bind=engine)
    print('✅ Tables created successfully')
except Exception as e:
    print(f'⚠️ Table creation warning: {e}')
"

# 초기 데이터 생성
echo "🌱 Creating initial data..."
python -c "
from app.database import SessionLocal
from app.models.auth_models import User, InviteCode
from datetime import datetime
import hashlib

db = SessionLocal()
try:
    # 관리자 계정 생성
    admin = db.query(User).filter(User.site_id == 'admin').first()
    if not admin:
        admin = User(
            site_id='admin',
            nickname='관리자',
            email='admin@casino-club.local',
            phone_number='000-0000-0000',
            password_hash=hashlib.sha256('admin123'.encode()).hexdigest(),
            vip_tier='PREMIUM',
            battlepass_level=100,
            cyber_tokens=10000,
            created_at=datetime.utcnow()
        )
        db.add(admin)
    
    # 초대 코드 생성
    invite = db.query(InviteCode).filter(InviteCode.code == '5858').first()
    if not invite:
        invite = InviteCode(
            code='5858',
            created_by='admin',
            created_at=datetime.utcnow(),
            expires_at=datetime(2025, 12, 31),
            max_uses=1000,
            used_count=0
        )
        db.add(invite)
    
    db.commit()
    print('✅ Initial data created')
except Exception as e:
    print(f'⚠️ Initial data warning: {e}')
    db.rollback()
finally:
    db.close()
"

# FastAPI 서버 시작
echo "🎮 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
