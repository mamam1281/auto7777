"""
Kafka 통합 API 엔드포인트
Casino-Club F2P 백엔드의 실시간 메시징 API
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from app.core.kafka_client import (
    CasinoClustersKafkaProducer,
    CasinoClustersKafkaConsumer,
    KafkaTopicManager,
    get_kafka_producer,
    get_kafka_topic_manager,
    KafkaConfig
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/kafka", tags=["Kafka Integration"])

# Pydantic 모델들
class UserActionRequest(BaseModel):
    user_id: str
    action_type: str
    action_data: Dict[str, Any]
    session_id: Optional[str] = None

class GameEventRequest(BaseModel):
    user_id: str
    game_id: str
    event_type: str
    event_data: Dict[str, Any]

class NotificationRequest(BaseModel):
    user_id: str
    notification_type: str
    message: str
    extra_data: Optional[Dict[str, Any]] = None

class AnalyticsEventRequest(BaseModel):
    event_type: str
    analytics_data: Dict[str, Any]

class RealTimeFeedbackRequest(BaseModel):
    user_id: str
    feedback_type: str
    feedback_data: Dict[str, Any]

class TopicCreationRequest(BaseModel):
    num_partitions: int = 3
    replication_factor: int = 1

# API 엔드포인트들

@router.post("/topics/create")
async def create_topics(
    request: TopicCreationRequest,
    topic_manager: KafkaTopicManager = Depends(get_kafka_topic_manager)
):
    """필요한 Kafka 토픽들 생성"""
    try:
        await topic_manager.create_topics(
            num_partitions=request.num_partitions,
            replication_factor=request.replication_factor
        )
        return {
            "status": "success",
            "message": "토픽 생성 완료",
            "topics": list(KafkaConfig.TOPICS.values())
        }
    except Exception as e:
        logger.error(f"토픽 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"토픽 생성 실패: {str(e)}")

@router.get("/topics/list")
async def list_topics(
    topic_manager: KafkaTopicManager = Depends(get_kafka_topic_manager)
):
    """존재하는 토픽 목록 조회"""
    try:
        topics = await topic_manager.list_topics()
        return {
            "status": "success",
            "topics": topics,
            "configured_topics": KafkaConfig.TOPICS
        }
    except Exception as e:
        logger.error(f"토픽 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"토픽 조회 실패: {str(e)}")

@router.post("/messages/user-action")
async def send_user_action(
    request: UserActionRequest,
    producer: CasinoClustersKafkaProducer = Depends(get_kafka_producer)
):
    """사용자 액션 메시지 전송"""
    try:
        # session_id가 있으면 action_data에 추가
        if request.session_id:
            request.action_data['session_id'] = request.session_id
        
        record_metadata = await producer.send_user_action(
            user_id=request.user_id,
            action_type=request.action_type,
            action_data=request.action_data
        )
        
        return {
            "status": "success",
            "message": "사용자 액션 전송 완료",
            "topic": record_metadata.topic,
            "partition": record_metadata.partition,
            "offset": record_metadata.offset
        }
    except Exception as e:
        logger.error(f"사용자 액션 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=f"메시지 전송 실패: {str(e)}")

@router.post("/messages/game-event")
async def send_game_event(
    request: GameEventRequest,
    producer: CasinoClustersKafkaProducer = Depends(get_kafka_producer)
):
    """게임 이벤트 메시지 전송"""
    try:
        record_metadata = await producer.send_game_event(
            user_id=request.user_id,
            game_id=request.game_id,
            event_type=request.event_type,
            event_data=request.event_data
        )
        
        return {
            "status": "success",
            "message": "게임 이벤트 전송 완료",
            "topic": record_metadata.topic,
            "partition": record_metadata.partition,
            "offset": record_metadata.offset
        }
    except Exception as e:
        logger.error(f"게임 이벤트 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=f"메시지 전송 실패: {str(e)}")

@router.post("/messages/notification")
async def send_notification(
    request: NotificationRequest,
    producer: CasinoClustersKafkaProducer = Depends(get_kafka_producer)
):
    """알림 메시지 전송"""
    try:
        record_metadata = await producer.send_notification(
            user_id=request.user_id,
            notification_type=request.notification_type,
            message=request.message,
            extra_data=request.extra_data
        )
        
        return {
            "status": "success",
            "message": "알림 전송 완료",
            "topic": record_metadata.topic,
            "partition": record_metadata.partition,
            "offset": record_metadata.offset
        }
    except Exception as e:
        logger.error(f"알림 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=f"메시지 전송 실패: {str(e)}")

@router.post("/messages/analytics")
async def send_analytics_event(
    request: AnalyticsEventRequest,
    producer: CasinoClustersKafkaProducer = Depends(get_kafka_producer)
):
    """분석 이벤트 전송"""
    try:
        record_metadata = await producer.send_analytics_event(
            event_type=request.event_type,
            analytics_data=request.analytics_data
        )
        
        return {
            "status": "success",
            "message": "분석 이벤트 전송 완료",
            "topic": record_metadata.topic,
            "partition": record_metadata.partition,
            "offset": record_metadata.offset
        }
    except Exception as e:
        logger.error(f"분석 이벤트 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=f"메시지 전송 실패: {str(e)}")

@router.post("/messages/real-time-feedback")
async def send_real_time_feedback(
    request: RealTimeFeedbackRequest,
    producer: CasinoClustersKafkaProducer = Depends(get_kafka_producer)
):
    """실시간 피드백 전송 (도파민 트리거)"""
    try:
        record_metadata = await producer.send_real_time_feedback(
            user_id=request.user_id,
            feedback_type=request.feedback_type,
            feedback_data=request.feedback_data
        )
        
        return {
            "status": "success",
            "message": "실시간 피드백 전송 완료",
            "topic": record_metadata.topic,
            "partition": record_metadata.partition,
            "offset": record_metadata.offset
        }
    except Exception as e:
        logger.error(f"실시간 피드백 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=f"메시지 전송 실패: {str(e)}")

# 실제 게임 시나리오 API들

@router.post("/game/slot-spin")
async def slot_spin_action(
    user_id: str,
    game_id: str,
    bet_amount: int,
    session_id: str,
    producer: CasinoClustersKafkaProducer = Depends(get_kafka_producer)
):
    """슬롯 스핀 액션 (통합 예시)"""
    try:
        # 1. 사용자 액션 기록
        await producer.send_user_action(
            user_id=user_id,
            action_type="SLOT_SPIN",
            action_data={
                "game_id": game_id,
                "bet_amount": bet_amount,
                "session_id": session_id
            }
        )
        
        # 2. 게임 이벤트 기록
        await producer.send_game_event(
            user_id=user_id,
            game_id=game_id,
            event_type="SPIN_START",
            event_data={
                "bet_amount": bet_amount,
                "spin_type": "regular"
            }
        )
        
        # 3. 분석 이벤트 전송
        await producer.send_analytics_event(
            event_type="GAME_ENGAGEMENT",
            analytics_data={
                "user_id": user_id,
                "game_id": game_id,
                "action": "slot_spin",
                "bet_amount": bet_amount,
                "engagement_type": "active_play"
            }
        )
        
        return {
            "status": "success",
            "message": "슬롯 스핀 액션 처리 완료",
            "user_id": user_id,
            "game_id": game_id,
            "bet_amount": bet_amount
        }
    except Exception as e:
        logger.error(f"슬롯 스핀 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"슬롯 스핀 실패: {str(e)}")

@router.post("/game/gacha-open")
async def gacha_open_action(
    user_id: str,
    gacha_type: str,
    cost: int,
    session_id: str,
    producer: CasinoClustersKafkaProducer = Depends(get_kafka_producer)
):
    """가챠 오픈 액션 (통합 예시)"""
    try:
        # 1. 사용자 액션 기록
        await producer.send_user_action(
            user_id=user_id,
            action_type="GACHA_OPEN",
            action_data={
                "gacha_type": gacha_type,
                "cost": cost,
                "session_id": session_id
            }
        )
        
        # 2. 실시간 피드백 (도파민 트리거)
        await producer.send_real_time_feedback(
            user_id=user_id,
            feedback_type="DOPAMINE_TRIGGER",
            feedback_data={
                "message": "🎉 Lucky Box opened! Amazing rewards await!",
                "animation": "NEON_EXPLOSION",
                "sound": "victory_fanfare",
                "intensity": "high"
            }
        )
        
        # 3. 분석 이벤트
        await producer.send_analytics_event(
            event_type="MONETIZATION_ACTION",
            analytics_data={
                "user_id": user_id,
                "action": "gacha_open",
                "gacha_type": gacha_type,
                "cost": cost,
                "revenue_impact": cost
            }
        )
        
        return {
            "status": "success",
            "message": "가챠 오픈 액션 처리 완료",
            "user_id": user_id,
            "gacha_type": gacha_type,
            "cost": cost
        }
    except Exception as e:
        logger.error(f"가챠 오픈 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"가챠 오픈 실패: {str(e)}")

@router.post("/cyber-tokens/earn")
async def cyber_token_earn(
    user_id: str,
    amount: int,
    source: str,
    session_id: str,
    producer: CasinoClustersKafkaProducer = Depends(get_kafka_producer)
):
    """사이버 토큰 획득 (본사 연동)"""
    try:
        # 1. 사용자 액션 기록
        await producer.send_user_action(
            user_id=user_id,
            action_type="CYBER_TOKEN_EARN",
            action_data={
                "amount": amount,
                "source": source,
                "session_id": session_id
            }
        )
        
        # 2. 알림 전송
        await producer.send_notification(
            user_id=user_id,
            notification_type="CYBER_TOKEN_EARNED",
            message=f"🪙 You earned {amount} Cyber Tokens from {source}!",
            extra_data={
                "amount": amount,
                "source": source,
                "new_balance": "will_be_calculated"
            }
        )
        
        # 3. 분석 이벤트
        await producer.send_analytics_event(
            event_type="CYBER_TOKEN_TRANSACTION",
            analytics_data={
                "user_id": user_id,
                "transaction_type": "earn",
                "amount": amount,
                "source": source,
                "corporate_integration": True
            }
        )
        
        return {
            "status": "success",
            "message": "사이버 토큰 획득 처리 완료",
            "user_id": user_id,
            "amount": amount,
            "source": source
        }
    except Exception as e:
        logger.error(f"사이버 토큰 획득 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"토큰 획득 실패: {str(e)}")

# 헬스체크 및 상태 확인

@router.get("/health")
async def kafka_health_check():
    """Kafka 연결 상태 확인"""
    try:
        # Producer 연결 테스트
        producer = CasinoClustersKafkaProducer()
        
        # Topic Manager 연결 테스트
        topic_manager = KafkaTopicManager()
        topics = await topic_manager.list_topics()
        
        producer.close()
        
        return {
            "status": "healthy",
            "kafka_connection": "ok",
            "topics_available": len(topics),
            "configured_topics": len(KafkaConfig.TOPICS)
        }
    except Exception as e:
        logger.error(f"Kafka 헬스체크 실패: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/config")
async def get_kafka_config():
    """현재 Kafka 설정 조회"""
    return {
        "bootstrap_servers": KafkaConfig.BOOTSTRAP_SERVERS,
        "topics": KafkaConfig.TOPICS,
        "status": "configured"
    }
