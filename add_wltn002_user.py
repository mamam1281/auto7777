#!/usr/bin/env python3

from app.database import get_db
from sqlalchemy import text

def add_wltn002_user():
    db = next(get_db())
    
    # 먼저 해당 사용자가 이미 있는지 확인
    check_query = text("SELECT id, site_id, nickname FROM users WHERE site_id = :site_id")
    existing = db.execute(check_query, {"site_id": "WLTN002"}).fetchone()
    
    if existing:
        print(f"WLTN002 사용자가 이미 존재합니다: {existing}")
        return existing[0]  # user_id 반환
    
    # WLTN002 사용자 추가
    insert_query = text("""
    INSERT INTO users (site_id, nickname, phone_number, password_hash, cyber_token_balance, rank, created_at, updated_at)
    VALUES (:site_id, :nickname, :phone_number, :password_hash, :cyber_token_balance, :rank, datetime('now'), datetime('now'))
    """)
    
    try:
        result = db.execute(insert_query, {
            "site_id": "WLTN002",
            "nickname": " 지수002", 
            "phone_number": "1234",
            "password_hash": "hashed_password",
            "cyber_token_balance": 200,
            "rank": "STANDARD"
        })
        db.commit()
        
        print('WLTN002 사용자 추가 완료')
        
        # 추가된 사용자 확인
        new_user = db.execute(check_query, {"site_id": "WLTN002"}).fetchone()
        print('추가된 사용자:', new_user)
        return new_user[0] if new_user else None
        
    except Exception as e:
        print('에러:', e)
        db.rollback()
        return None

if __name__ == "__main__":
    user_id = add_wltn002_user()
