import sqlite3

# alembic_version 테이블 업데이트
conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

# 현재 버전 확인
cursor.execute('SELECT * FROM alembic_version')
current = cursor.fetchall()
print(f"Current version: {current}")

# 유효한 마이그레이션 ID로 업데이트
cursor.execute('UPDATE alembic_version SET version_num = ?', ('dd73ef05465d',))
conn.commit()

# 업데이트 확인
cursor.execute('SELECT * FROM alembic_version')
updated = cursor.fetchall()
print(f"Updated version: {updated}")

conn.close()
print("✅ Alembic version updated successfully!")
