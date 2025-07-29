"""
Kafka 연동 통합 테스트 (pytest)
- 토픽 생성, 메시지 발행/수신, 예외 처리 자동화
- dev/prod 환경 분리 (.env 연동)
"""
import os
import time
import pytest
from kafka.kafka_topics import create_topics
from kafka.kafka_producer import send_message
from kafka.kafka_consumer import get_kafka_consumer

TEST_TOPIC = "user_actions"

@pytest.fixture(scope="session", autouse=True)
def setup_topics():
    create_topics()
    time.sleep(2)  # 토픽 생성 대기

@pytest.mark.integration
def test_kafka_produce_consume():
    test_msg = {"user_id": 999, "action": "TEST", "ts": time.time()}
    send_message(TEST_TOPIC, test_msg)
    consumer = get_kafka_consumer(TEST_TOPIC)
    found = False
    start = time.time()
    for msg in consumer:
        if msg.value and "999" in msg.value:
            found = True
            break
        if time.time() - start > 10:
            break
    consumer.close()
    assert found, "Kafka 메시지 송수신 실패"
