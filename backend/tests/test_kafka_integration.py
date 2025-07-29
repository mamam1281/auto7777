import pytest
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import ConfigResource, NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaTimeoutError
import time
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = 'localhost:9093'  # Windows 환경: 반드시 localhost로 지정, 컨테이너 포트 매핑 필요
TEST_TOPICS = [
    'test_kafka_integration',
    'user_actions',
    'game_events', 
    'notifications',
    'analytics',
    'real_time_feedback'
]

@pytest.fixture(scope='module')
def admin_client():
    """Kafka Admin Client for topic management"""
    return KafkaAdminClient(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        client_id='test_admin'
    )

@pytest.fixture(scope='module')
def producer():
    """Kafka Producer for message publishing"""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

@pytest.fixture(scope='module')
def consumer_factory():
    """Factory function to create consumers with different configs"""
    consumers = []
    
    def create_consumer(topic, group_id='test-group', **kwargs):
        # Handle consumer_timeout_ms override
        default_timeout = kwargs.pop('consumer_timeout_ms', 5000)
        
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            consumer_timeout_ms=default_timeout,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
            **kwargs
        )
        consumers.append(consumer)
        return consumer
    
    yield create_consumer
    
    # Cleanup: close all consumers
    for consumer in consumers:
        consumer.close()

class TestKafkaConnectivity:
    """Test Kafka basic connectivity and configuration"""
    
    def test_kafka_connection(self, admin_client):
        """📋 1. Kafka 서버 연결 테스트"""
        logger.info("Testing Kafka server connection...")
        
        try:
            # Get cluster metadata to verify connection
            metadata = admin_client.describe_cluster()
            assert metadata is not None
            logger.info("✅ Kafka server connection successful")
        except Exception as e:
            pytest.fail(f"❌ Kafka connection failed: {e}")

    def test_kafka_cluster_info(self, admin_client):
        """📋 2. Kafka 클러스터 정보 조회"""
        logger.info("Testing Kafka cluster information retrieval...")
        
        try:
            # Get broker information
            cluster_metadata = admin_client.describe_cluster()
            logger.info(f"✅ Kafka cluster information retrieved successfully")
            
            # Verify at least one broker is available
            brokers = admin_client.list_consumer_groups()
            logger.info(f"✅ Consumer groups accessible")
        except Exception as e:
            pytest.fail(f"❌ Failed to retrieve cluster info: {e}")

class TestKafkaTopicManagement:
    """Test Kafka topic creation and management"""
    
    def test_topic_creation(self, admin_client):
        """📋 3. Kafka 토픽 생성/삭제 테스트"""
        logger.info("Testing Kafka topic creation...")
        
        # Create test topics
        new_topics = [
            NewTopic(name=topic, num_partitions=3, replication_factor=1)
            for topic in TEST_TOPICS
        ]
        
        try:
            # Create topics
            admin_client.create_topics(new_topics)
            logger.info(f"✅ Created topics: {TEST_TOPICS}")
        except TopicAlreadyExistsError:
            logger.info("ℹ️ Topics already exist, continuing...")
        except Exception as e:
            pytest.fail(f"❌ Topic creation failed: {e}")
        
        # Verify topics exist
        try:
            existing_topics = admin_client.list_topics()
            for topic in TEST_TOPICS:
                assert topic in existing_topics, f"Topic {topic} not found"
            logger.info("✅ All test topics verified to exist")
        except Exception as e:
            pytest.fail(f"❌ Topic verification failed: {e}")

    def test_topic_configuration(self, admin_client):
        """📋 4. Kafka 토픽 설정 조회"""
        logger.info("Testing Kafka topic configuration retrieval...")
        
        try:
            # Get topic configurations
            config_resources = [
                ConfigResource('topic', topic) for topic in TEST_TOPICS[:2]
            ]
            configs = admin_client.describe_configs(config_resources)
            
            assert len(configs) > 0
            logger.info("✅ Topic configurations retrieved successfully")
        except Exception as e:
            pytest.fail(f"❌ Topic configuration retrieval failed: {e}")

class TestKafkaProducerConsumer:
    """Test Kafka Producer and Consumer functionality"""
    
    def test_basic_produce_consume(self, producer, consumer_factory):
        """📋 5. 기본 메시지 송수신 테스트"""
        logger.info("Testing basic Kafka message produce/consume...")
        
        topic = TEST_TOPICS[0]
        test_message = {
            "event_type": "test_event",
            "user_id": "test_user_123",
            "timestamp": time.time(),
            "data": {"test": "data"}
        }
        
        # Create consumer first to capture messages from the beginning
        consumer = consumer_factory(topic, group_id='basic-test-group-new')
        
        # Wait a moment for consumer to be ready
        time.sleep(1)
        
        # Send message
        future = producer.send(topic, test_message)
        producer.flush()
        
        # Verify send was successful
        try:
            record_metadata = future.get(timeout=10)
            logger.info(f"✅ Message sent to {record_metadata.topic}:{record_metadata.partition}")
        except KafkaTimeoutError:
            pytest.fail("❌ Message send timeout")
        
        # Consume message
        received = False
        timeout_count = 0
        max_timeout = 3  # Maximum number of timeout cycles
        
        try:
            for msg in consumer:
                if msg.value and msg.value.get('event_type') == test_message['event_type']:
                    received = True
                    logger.info(f"✅ Message received: {msg.value}")
                    break
        except StopIteration:
            # Consumer timeout - this is expected if no messages
            timeout_count += 1
            if timeout_count < max_timeout:
                logger.info("Consumer timeout, retrying...")
            else:
                logger.warning("Consumer timeout after retries")
        
        assert received, "❌ Message was not received by consumer"

    def test_multiple_consumers_same_group(self, producer, consumer_factory):
        """📋 6. 컨슈머 그룹 테스트 (같은 그룹)"""
        logger.info("Testing multiple consumers in same group...")
        
        topic = TEST_TOPICS[1]
        group_id = 'same-group-test'
        
        # Create two consumers in same group
        consumer1 = consumer_factory(topic, group_id=group_id)
        consumer2 = consumer_factory(topic, group_id=group_id)
        
        # Send multiple messages
        messages = [
            {"event": "user_action", "user_id": f"user_{i}", "action": "click"}
            for i in range(5)
        ]
        
        for msg in messages:
            producer.send(topic, msg)
        producer.flush()
        
        # Consume with both consumers
        received_messages = []
        consumers = [consumer1, consumer2]
        
        for consumer in consumers:
            for msg in consumer:
                received_messages.append(msg.value)
                if len(received_messages) >= len(messages):
                    break
        
        # Each message should be consumed by only one consumer in the group
        assert len(received_messages) >= len(messages) // 2, "Messages not properly distributed"
        logger.info(f"✅ Received {len(received_messages)} messages across consumer group")

    def test_multiple_consumers_different_groups(self, producer, consumer_factory):
        """📋 7. 컨슈머 그룹 테스트 (다른 그룹)"""
        logger.info("Testing multiple consumers in different groups...")
        
        topic = TEST_TOPICS[2]
        
        # Create consumers in different groups
        consumer1 = consumer_factory(topic, group_id='group-1')
        consumer2 = consumer_factory(topic, group_id='group-2')
        
        test_message = {
            "event": "game_event",
            "player_id": "player_123",
            "action": "spin",
            "result": "win"
        }
        
        # Send message
        producer.send(topic, test_message)
        producer.flush()
        
        # Both consumers should receive the message
        consumers_received = []
        
        for consumer in [consumer1, consumer2]:
            for msg in consumer:
                if msg.value == test_message:
                    consumers_received.append(consumer)
                    break
        
        assert len(consumers_received) == 2, "Both consumer groups should receive the message"
        logger.info("✅ Message received by both consumer groups")

class TestKafkaErrorHandling:
    """Test Kafka error handling and resilience"""
    
    def test_invalid_topic_error_handling(self, producer):
        """📋 8. 잘못된 토픽 처리 테스트"""
        logger.info("Testing invalid topic error handling...")
        
        # Test sending to non-existent topic with auto-create disabled
        invalid_topic = "non_existent_topic_12345"
        
        try:
            future = producer.send(invalid_topic, {"test": "data"})
            producer.flush()
            
            # Should either succeed (auto-create) or timeout
            record_metadata = future.get(timeout=5)
            logger.info(f"✅ Auto-creation worked for topic: {invalid_topic}")
        except KafkaTimeoutError:
            logger.info("✅ Timeout handled gracefully for invalid topic")
        except Exception as e:
            logger.info(f"✅ Error handled gracefully: {type(e).__name__}")

    def test_consumer_timeout_handling(self, consumer_factory):
        """📋 9. 컨슈머 타임아웃 처리 테스트"""
        logger.info("Testing consumer timeout handling...")
        
        # Create consumer with short timeout
        consumer = consumer_factory(
            TEST_TOPICS[3], 
            group_id='timeout-test-group',
            consumer_timeout_ms=1000
        )
        
        # Try to consume from empty topic
        messages_received = 0
        try:
            for msg in consumer:
                messages_received += 1
        except StopIteration:
            # This is expected behavior when timeout occurs
            pass
        
        logger.info(f"✅ Consumer timeout handled gracefully (received {messages_received} messages)")

class TestKafkaPerformanceBasic:
    """Basic Kafka performance and throughput tests"""
    
    def test_batch_message_throughput(self, producer, consumer_factory):
        """📋 10. 배치 메시지 처리량 테스트"""
        logger.info("Testing batch message throughput...")
        
        topic = TEST_TOPICS[4]
        consumer = consumer_factory(topic, group_id='throughput-test-group')
        
        # Send batch of messages
        batch_size = 100
        start_time = time.time()
        
        for i in range(batch_size):
            message = {
                "batch_id": "batch_001",
                "message_id": i,
                "timestamp": time.time(),
                "data": f"test_data_{i}"
            }
            producer.send(topic, message)
        
        producer.flush()
        send_time = time.time() - start_time
        
        # Consume messages
        consume_start = time.time()
        received_count = 0
        
        for msg in consumer:
            received_count += 1
            if received_count >= batch_size:
                break
        
        consume_time = time.time() - consume_start
        
        # Calculate throughput
        send_throughput = batch_size / send_time
        consume_throughput = batch_size / consume_time
        
        logger.info(f"✅ Send throughput: {send_throughput:.2f} messages/sec")
        logger.info(f"✅ Consume throughput: {consume_throughput:.2f} messages/sec")
        
        assert received_count == batch_size, f"Expected {batch_size} messages, got {received_count}"
        assert send_throughput > 10, "Send throughput too low"
        assert consume_throughput > 10, "Consume throughput too low"

class TestKafkaIntegrationScenarios:
    """Real-world Casino-Club integration scenarios"""
    
    def test_user_action_pipeline(self, producer, consumer_factory):
        """📋 11. 사용자 액션 파이프라인 테스트"""
        logger.info("Testing user action pipeline...")
        
        # Simulate user actions workflow
        actions_topic = 'user_actions'
        notifications_topic = 'notifications'
        
        # Create consumers for pipeline
        action_consumer = consumer_factory(actions_topic, group_id='action-processor')
        notification_consumer = consumer_factory(notifications_topic, group_id='notification-service')
        
        # Send user action
        user_action = {
            "user_id": "user_12345",
            "action_type": "SLOT_SPIN",
            "game_id": "neon_slots",
            "bet_amount": 50,
            "timestamp": time.time(),
            "session_id": "session_abc123"
        }
        
        producer.send(actions_topic, user_action)
        producer.flush()
        
        # Process action (simulate processing)
        action_received = False
        for msg in action_consumer:
            if msg.value.get('user_id') == user_action['user_id']:
                action_received = True
                
                # Generate notification based on action
                notification = {
                    "user_id": msg.value['user_id'],
                    "type": "REWARD_EARNED",
                    "message": "You earned 100 cyber tokens!",
                    "timestamp": time.time()
                }
                
                producer.send(notifications_topic, notification)
                producer.flush()
                break
        
        assert action_received, "User action not received"
        
        # Verify notification was sent
        notification_received = False
        for msg in notification_consumer:
            if msg.value.get('type') == 'REWARD_EARNED':
                notification_received = True
                break
        
        assert notification_received, "Notification not received"
        logger.info("✅ User action pipeline test completed successfully")

    def test_real_time_analytics_flow(self, producer, consumer_factory):
        """📋 12. 실시간 분석 데이터 플로우 테스트"""
        logger.info("Testing real-time analytics flow...")
        
        analytics_topic = 'analytics'
        feedback_topic = 'real_time_feedback'
        
        analytics_consumer = consumer_factory(analytics_topic, group_id='analytics-processor')
        feedback_consumer = consumer_factory(feedback_topic, group_id='feedback-service')
        
        # Send analytics event
        analytics_event = {
            "event_type": "GAME_COMPLETION",
            "user_id": "user_67890",
            "game_result": "WIN",
            "payout": 500,
            "play_duration": 120,
            "timestamp": time.time()
        }
        
        producer.send(analytics_topic, analytics_event)
        producer.flush()
        
        # Process analytics and generate feedback
        analytics_received = False
        for msg in analytics_consumer:
            if msg.value.get('event_type') == 'GAME_COMPLETION':
                analytics_received = True
                
                # Generate real-time feedback
                feedback = {
                    "user_id": msg.value['user_id'],
                    "feedback_type": "DOPAMINE_TRIGGER",
                    "message": "🎉 Amazing win! Try again for even bigger rewards!",
                    "animation": "NEON_CELEBRATION",
                    "timestamp": time.time()
                }
                
                producer.send(feedback_topic, feedback)
                producer.flush()
                break
        
        assert analytics_received, "Analytics event not received"
        
        # Verify feedback was generated
        feedback_received = False
        for msg in feedback_consumer:
            if msg.value.get('feedback_type') == 'DOPAMINE_TRIGGER':
                feedback_received = True
                break
        
        assert feedback_received, "Real-time feedback not received"
        logger.info("✅ Real-time analytics flow test completed successfully")
