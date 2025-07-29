"""
Kafka 통합을 위한 Producer/Consumer 유틸리티
Casino-Club F2P 백엔드의 실시간 메시징 기능 구현
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaConfig:
    """Kafka 설정 관리"""
    BOOTSTRAP_SERVERS = 'localhost:9093'
    
    # Casino-Club F2P 전용 토픽들
    TOPICS = {
        'USER_ACTIONS': 'user_actions',
        'GAME_EVENTS': 'game_events',
        'NOTIFICATIONS': 'notifications',
        'ANALYTICS': 'analytics',
        'REAL_TIME_FEEDBACK': 'real_time_feedback',
        'CYBER_TOKENS': 'cyber_tokens',
        'BATTLE_PASS': 'battle_pass',
        'ADULT_CONTENT': 'adult_content',
        'VIP_EVENTS': 'vip_events'
    }

class CasinoClustersKafkaProducer:
    """Casino-Club F2P용 Kafka Producer"""
    
    def __init__(self, bootstrap_servers: str = KafkaConfig.BOOTSTRAP_SERVERS):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._connect()
    
    def _connect(self):
        """Kafka Producer 연결"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                acks='all',  # 모든 replica 확인
                retries=3,   # 재시도 횟수
                batch_size=16384,  # 배치 크기
                linger_ms=10,      # 배치 대기 시간
                compression_type='gzip'  # 압축
            )
            logger.info("✅ Kafka Producer 연결 성공")
        except Exception as e:
            logger.error(f"❌ Kafka Producer 연결 실패: {e}")
            raise
    
    async def send_user_action(self, user_id: str, action_type: str, action_data: Dict[str, Any]):
        """사용자 액션 메시지 전송"""
        message = {
            'user_id': user_id,
            'action_type': action_type,
            'action_data': action_data,
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': action_data.get('session_id'),
            'source': 'casino_club_webapp'
        }
        
        try:
            future = self.producer.send(KafkaConfig.TOPICS['USER_ACTIONS'], message)
            record_metadata = future.get(timeout=10)
            logger.info(f"✅ 사용자 액션 전송 성공: {action_type} for {user_id}")
            return record_metadata
        except Exception as e:
            logger.error(f"❌ 사용자 액션 전송 실패: {e}")
            raise
    
    async def send_game_event(self, user_id: str, game_id: str, event_type: str, event_data: Dict[str, Any]):
        """게임 이벤트 메시지 전송"""
        message = {
            'user_id': user_id,
            'game_id': game_id,
            'event_type': event_type,
            'event_data': event_data,
            'timestamp': datetime.utcnow().isoformat(),
            'server_time': datetime.utcnow().timestamp()
        }
        
        try:
            future = self.producer.send(KafkaConfig.TOPICS['GAME_EVENTS'], message)
            record_metadata = future.get(timeout=10)
            logger.info(f"✅ 게임 이벤트 전송 성공: {event_type} in {game_id}")
            return record_metadata
        except Exception as e:
            logger.error(f"❌ 게임 이벤트 전송 실패: {e}")
            raise
    
    async def send_notification(self, user_id: str, notification_type: str, message: str, extra_data: Optional[Dict] = None):
        """알림 메시지 전송"""
        notification = {
            'user_id': user_id,
            'notification_type': notification_type,
            'message': message,
            'extra_data': extra_data or {},
            'timestamp': datetime.utcnow().isoformat(),
            'priority': 'normal',
            'read': False
        }
        
        try:
            future = self.producer.send(KafkaConfig.TOPICS['NOTIFICATIONS'], notification)
            record_metadata = future.get(timeout=10)
            logger.info(f"✅ 알림 전송 성공: {notification_type} to {user_id}")
            return record_metadata
        except Exception as e:
            logger.error(f"❌ 알림 전송 실패: {e}")
            raise
    
    async def send_analytics_event(self, event_type: str, analytics_data: Dict[str, Any]):
        """분석 이벤트 전송"""
        message = {
            'event_type': event_type,
            'analytics_data': analytics_data,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'casino_club_backend'
        }
        
        try:
            future = self.producer.send(KafkaConfig.TOPICS['ANALYTICS'], message)
            record_metadata = future.get(timeout=10)
            logger.info(f"✅ 분석 이벤트 전송 성공: {event_type}")
            return record_metadata
        except Exception as e:
            logger.error(f"❌ 분석 이벤트 전송 실패: {e}")
            raise
    
    async def send_real_time_feedback(self, user_id: str, feedback_type: str, feedback_data: Dict[str, Any]):
        """실시간 피드백 전송 (도파민 트리거용)"""
        message = {
            'user_id': user_id,
            'feedback_type': feedback_type,
            'feedback_data': feedback_data,
            'timestamp': datetime.utcnow().isoformat(),
            'trigger_immediate': True
        }
        
        try:
            future = self.producer.send(KafkaConfig.TOPICS['REAL_TIME_FEEDBACK'], message)
            record_metadata = future.get(timeout=10)
            logger.info(f"✅ 실시간 피드백 전송 성공: {feedback_type} to {user_id}")
            return record_metadata
        except Exception as e:
            logger.error(f"❌ 실시간 피드백 전송 실패: {e}")
            raise
    
    def close(self):
        """Producer 연결 종료"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("✅ Kafka Producer 연결 종료")

class CasinoClustersKafkaConsumer:
    """Casino-Club F2P용 Kafka Consumer"""
    
    def __init__(self, topics: List[str], group_id: str, bootstrap_servers: str = KafkaConfig.BOOTSTRAP_SERVERS):
        self.topics = topics
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self.running = False
        self._connect()
    
    def _connect(self):
        """Kafka Consumer 연결"""
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='latest',  # 최신 메시지부터
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                consumer_timeout_ms=1000  # 1초 타임아웃
            )
            logger.info(f"✅ Kafka Consumer 연결 성공: {self.group_id}")
        except Exception as e:
            logger.error(f"❌ Kafka Consumer 연결 실패: {e}")
            raise
    
    async def start_consuming(self, message_handler: callable):
        """메시지 소비 시작"""
        self.running = True
        logger.info(f"🚀 Consumer 시작: {self.group_id} for topics {self.topics}")
        
        try:
            while self.running:
                # 논블로킹 방식으로 메시지 폴링
                try:
                    message_batch = self.consumer.poll(timeout_ms=1000)
                    
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            try:
                                await message_handler(message)
                            except Exception as e:
                                logger.error(f"❌ 메시지 처리 실패: {e}")
                    
                    # 약간의 대기
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"❌ 메시지 폴링 실패: {e}")
                    await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"❌ Consumer 실행 중 오류: {e}")
        finally:
            logger.info(f"🛑 Consumer 종료: {self.group_id}")
    
    def stop(self):
        """Consumer 중지"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info(f"✅ Kafka Consumer 연결 종료: {self.group_id}")

class KafkaTopicManager:
    """Kafka 토픽 관리"""
    
    def __init__(self, bootstrap_servers: str = KafkaConfig.BOOTSTRAP_SERVERS):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            client_id='cc_topic_manager'
        )
    
    async def create_topics(self, num_partitions: int = 3, replication_factor: int = 1):
        """필요한 토픽들 생성"""
        new_topics = [
            NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor
            )
            for topic_name in KafkaConfig.TOPICS.values()
        ]
        
        try:
            self.admin_client.create_topics(new_topics, validate_only=False)
            logger.info(f"✅ 토픽 생성 성공: {list(KafkaConfig.TOPICS.values())}")
        except TopicAlreadyExistsError:
            logger.info("ℹ️ 토픽들이 이미 존재합니다")
        except Exception as e:
            logger.error(f"❌ 토픽 생성 실패: {e}")
            raise
    
    async def list_topics(self):
        """토픽 목록 조회"""
        try:
            topics = self.admin_client.list_topics()
            logger.info(f"📋 존재하는 토픽들: {topics}")
            return topics
        except Exception as e:
            logger.error(f"❌ 토픽 목록 조회 실패: {e}")
            raise

# 사용 예시 및 샘플 핸들러들

async def user_action_handler(message):
    """사용자 액션 메시지 처리 핸들러"""
    data = message.value
    user_id = data.get('user_id')
    action_type = data.get('action_type')
    
    logger.info(f"🎮 사용자 액션 처리: {action_type} by {user_id}")
    
    # 액션 타입별 처리 로직
    if action_type == 'SLOT_SPIN':
        # 슬롯 스핀 처리
        await process_slot_spin(data)
    elif action_type == 'GACHA_OPEN':
        # 가챠 오픈 처리
        await process_gacha_open(data)
    elif action_type == 'CYBER_TOKEN_EARN':
        # 사이버 토큰 획득 처리
        await process_cyber_token_earn(data)

async def process_slot_spin(action_data):
    """슬롯 스핀 처리"""
    # 게임 로직 실행
    # 결과에 따른 리워드 지급
    # 실시간 피드백 전송
    logger.info("🎰 슬롯 스핀 처리 완료")

async def process_gacha_open(action_data):
    """가챠 오픈 처리"""
    # 가챠 로직 실행
    # 아이템 지급
    # 도파민 트리거 전송
    logger.info("📦 가챠 오픈 처리 완료")

async def process_cyber_token_earn(action_data):
    """사이버 토큰 획득 처리"""
    # 토큰 잔액 업데이트
    # 본사 사이트 연동
    # 알림 전송
    logger.info("🪙 사이버 토큰 획득 처리 완료")

async def notification_handler(message):
    """알림 메시지 처리 핸들러"""
    data = message.value
    user_id = data.get('user_id')
    notification_type = data.get('notification_type')
    
    logger.info(f"🔔 알림 처리: {notification_type} to {user_id}")
    
    # WebSocket을 통한 실시간 알림 전송
    # 푸시 알림 전송
    # 이메일 알림 (필요시)

async def analytics_handler(message):
    """분석 이벤트 처리 핸들러"""
    data = message.value
    event_type = data.get('event_type')
    
    logger.info(f"📊 분석 이벤트 처리: {event_type}")
    
    # 데이터베이스에 분석 데이터 저장
    # ClickHouse/Druid로 OLAP 데이터 전송
    # 실시간 대시보드 업데이트

async def real_time_feedback_handler(message):
    """실시간 피드백 처리 핸들러"""
    data = message.value
    user_id = data.get('user_id')
    feedback_type = data.get('feedback_type')
    
    logger.info(f"⚡ 실시간 피드백 처리: {feedback_type} to {user_id}")
    
    # WebSocket을 통한 즉시 피드백 전송
    # UI 애니메이션 트리거
    # 사운드 이펙트 재생

# FastAPI 통합용 의존성
def get_kafka_producer() -> CasinoClustersKafkaProducer:
    """FastAPI 의존성: Kafka Producer"""
    return CasinoClustersKafkaProducer()

def get_kafka_topic_manager() -> KafkaTopicManager:
    """FastAPI 의존성: Kafka Topic Manager"""
    return KafkaTopicManager()
