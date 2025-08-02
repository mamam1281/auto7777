# Celery application configuration
import os
from celery import Celery

# Redis URL 설정
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Celery 앱 생성
celery_app = Celery(
    "casino_club",
    broker=redis_url,
    backend=redis_url,
    include=["app.tasks"]
)

# Celery 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "sample-task": {
            "task": "app.tasks.sample_task",
            "schedule": 30.0,  # 30초마다 실행
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks()
