FROM python:3.9-slim

# 시스템 패키지 업데이트 및 PostgreSQL 클라이언트 설치
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

# entrypoint 스크립트 실행 권한 부여
RUN chmod +x /app/entrypoint.sh

# 엔트리포인트 설정
ENTRYPOINT ["/app/entrypoint.sh"]