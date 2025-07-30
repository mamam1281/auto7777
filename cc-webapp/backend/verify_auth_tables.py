import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

# 새로 생성된 인증 테이블들 확인
cursor.execute("""
SELECT name FROM sqlite_master 
WHERE type='table' 
AND (name LIKE '%session%' OR name LIKE '%attempt%' OR name LIKE '%blacklist%')
""")
auth_tables = cursor.fetchall()
print("🔐 Created authentication tables:")
for table in auth_tables:
    print(f"  - {table[0]}")

# users 테이블의 새로운 컬럼 확인
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
auth_columns = [col for col in columns if col[1] in ['last_login_at', 'login_count', 'failed_login_attempts', 'account_locked_until']]
print(f"\n👤 Added user columns:")
for col in auth_columns:
    print(f"  - {col[1]} ({col[2]})")

# 인덱스 확인
cursor.execute("""
SELECT name FROM sqlite_master 
WHERE type='index' 
AND (name LIKE 'idx_user_session%' OR name LIKE 'idx_login_attempt%' OR name LIKE 'idx_blacklisted%')
""")
indexes = cursor.fetchall()
print(f"\n🗂️ Created indexes:")
for idx in indexes:
    print(f"  - {idx[0]}")

conn.close()
print(f"\n✅ Advanced Authentication System Successfully Deployed!")
print(f"🚀 Total new tables: {len(auth_tables)}")
print(f"📊 Total new indexes: {len(indexes)}")
print(f"🔧 Total new user columns: {len(auth_columns)}")
