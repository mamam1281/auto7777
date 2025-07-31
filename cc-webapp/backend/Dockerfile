FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치 (postgresql-client, wget 추가)
RUN apt-get update && apt-get install -y gcc libpq-dev postgresql-client wget && rm -rf /var/lib/apt/lists/*

# 의존성 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 실행 권한 부여
RUN chmod +x db_auto_init.py

# 포트 노출
EXPOSE 8000

# 데이터베이스 초기화 및 서버 실행 스크립트 생성
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Casino-Club Backend..."\n\
echo "📋 Database Auto-Initialization"\n\
python db_auto_init.py\n\
echo "🌟 Starting FastAPI Server..."\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload' > /app/start.sh

RUN chmod +x /app/start.sh

# 자동 마이그레이션 후 서버 실행
CMD ["/app/start.sh"]
