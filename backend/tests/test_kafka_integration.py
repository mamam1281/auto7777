import pytest
from kafka import KafkaProducer, KafkaConsumer
import time

KAFKA_BOOTSTRAP_SERVERS = 'localhost:9093'  # docker-compose 환경에 맞게 수정 필요
TEST_TOPIC = 'test_kafka_integration'

@pytest.fixture(scope='module')
def producer():
    return KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

@pytest.fixture(scope='module')
def consumer():
    consumer = KafkaConsumer(
        TEST_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='test-group',
        consumer_timeout_ms=5000
    )
    yield consumer
    consumer.close()

def test_kafka_produce_consume(producer, consumer):
    test_message = b'hello-kafka-test'
    # 메시지 발행
    producer.send(TEST_TOPIC, test_message)
    producer.flush()
    time.sleep(1)  # 메시지 전파 대기
    # 메시지 수신
    received = False
    for msg in consumer:
        if msg.value == test_message:
            received = True
            break
    assert received, 'Kafka 메시지 송수신 실패'
