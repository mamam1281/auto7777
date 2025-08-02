"""
💬 Casino-Club F2P - Chat API Router
===================================
실시간 채팅 및 AI 어시스턴트 시스템 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta

from ..database import get_db
from ..models.auth_models import User
from ..models.chat_models import (
    ChatRoom, ChatParticipant, ChatMessage, MessageReaction,
    AIAssistant, AIConversation, AIMessage, EmotionProfile
)
from ..schemas.chat_schemas import (
    ChatRoomResponse, ChatMessageResponse, ChatParticipantResponse,
    MessageCreate, RoomCreate, AIConversationResponse, EmotionProfileResponse
)
from ..services.auth_service import get_current_user
from ..services.chat_service import ChatService
from ..services.ai_chat_service import AIChatService
from ..utils.redis_client import get_redis
from ..utils.websocket_manager import WebSocketManager

router = APIRouter(prefix="/api/chat", tags=["Chat"])
websocket_manager = WebSocketManager()

@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_chat_rooms(
    room_type: Optional[str] = Query(None, regex="^(public|private|ai_assistant|support)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """채팅방 목록 조회"""
    try:
        query = db.query(ChatRoom).filter(ChatRoom.is_active == True)
        
        if room_type:
            query = query.filter(ChatRoom.room_type == room_type)
        
        # 사용자가 참여 중인 방만 조회 (private인 경우)
        if room_type == "private":
            query = query.join(ChatParticipant).filter(
                ChatParticipant.user_id == current_user.id,
                ChatParticipant.is_active == True
            )
        
        rooms = query.all()
        return rooms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rooms: {str(e)}")


@router.post("/rooms", response_model=ChatRoomResponse)
async def create_chat_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """채팅방 생성"""
    try:
        chat_service = ChatService(db)
        room = await chat_service.create_room(
            creator_id=current_user.id,
            room_data=room_data
        )
        return room
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")


@router.post("/rooms/{room_id}/join")
async def join_chat_room(
    room_id: int,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """채팅방 참여"""
    try:
        chat_service = ChatService(db)
        result = await chat_service.join_room(
            room_id=room_id,
            user_id=current_user.id
        )
        
        # Redis에 참가자 정보 업데이트
        await redis.sadd(f"room:{room_id}:participants", current_user.id)
        
        return {"success": True, "message": "Joined room successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join room: {str(e)}")


@router.post("/rooms/{room_id}/leave")
async def leave_chat_room(
    room_id: int,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """채팅방 나가기"""
    try:
        chat_service = ChatService(db)
        result = await chat_service.leave_room(
            room_id=room_id,
            user_id=current_user.id
        )
        
        # Redis에서 참가자 정보 제거
        await redis.srem(f"room:{room_id}:participants", current_user.id)
        
        return {"success": True, "message": "Left room successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to leave room: {str(e)}")


@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    room_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """채팅 메시지 조회"""
    try:
        # 사용자가 해당 방에 참여하고 있는지 확인
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_active == True
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not authorized to view this room")
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.room_id == room_id,
            ChatMessage.is_deleted == False
        ).order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit).all()
        
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    room_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """메시지 전송"""
    try:
        chat_service = ChatService(db)
        message = await chat_service.send_message(
            room_id=room_id,
            sender_id=current_user.id,
            message_data=message_data
        )
        
        # WebSocket으로 실시간 메시지 브로드캐스트
        await websocket_manager.broadcast_to_room(room_id, {
            "type": "new_message",
            "message": {
                "id": message.id,
                "content": message.content,
                "sender_id": message.sender_id,
                "created_at": message.created_at.isoformat(),
                "emotion_detected": message.emotion_detected
            }
        })
        
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.post("/messages/{message_id}/react")
async def react_to_message(
    message_id: int,
    reaction: str = Query(..., regex="^[👍👎❤️😊😢😠🎉]$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """메시지에 반응하기"""
    try:
        chat_service = ChatService(db)
        result = await chat_service.add_reaction(
            message_id=message_id,
            user_id=current_user.id,
            reaction_value=reaction
        )
        
        return {"success": True, "reaction_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add reaction: {str(e)}")


@router.websocket("/rooms/{room_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket 실시간 채팅"""
    await websocket_manager.connect(websocket, room_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 메시지를 방의 모든 참가자에게 브로드캐스트
            await websocket_manager.broadcast_to_room(room_id, {
                "type": "message",
                "data": message_data
            })
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, room_id)


# AI 어시스턴트 관련 엔드포인트

@router.get("/ai/assistants", response_model=List[Dict[str, Any]])
async def get_ai_assistants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 어시스턴트 목록 조회"""
    try:
        assistants = db.query(AIAssistant).filter(
            AIAssistant.is_active == True
        ).all()
        
        return [
            {
                "id": assistant.id,
                "name": assistant.name,
                "assistant_type": assistant.assistant_type,
                "personality": assistant.personality,
                "default_mood": assistant.default_mood
            }
            for assistant in assistants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assistants: {str(e)}")


@router.post("/ai/conversations", response_model=AIConversationResponse)
async def start_ai_conversation(
    assistant_id: int,
    conversation_type: str = Query("general", regex="^(general|support|guidance)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 대화 시작"""
    try:
        ai_chat_service = AIChatService(db)
        conversation = await ai_chat_service.start_conversation(
            user_id=current_user.id,
            assistant_id=assistant_id,
            conversation_type=conversation_type
        )
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")


@router.post("/ai/conversations/{conversation_id}/message")
async def send_ai_message(
    conversation_id: int,
    message: str,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """AI에게 메시지 전송"""
    try:
        ai_chat_service = AIChatService(db)
        response = await ai_chat_service.send_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            message=message
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send AI message: {str(e)}")


@router.get("/ai/conversations/{conversation_id}/messages")
async def get_ai_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 대화 기록 조회"""
    try:
        messages = db.query(AIMessage).filter(
            AIMessage.conversation_id == conversation_id
        ).order_by(AIMessage.created_at.asc()).limit(limit).all()
        
        return [
            {
                "id": msg.id,
                "content": msg.content,
                "sender_type": msg.sender_type,
                "detected_emotion": msg.detected_emotion,
                "response_mood": msg.response_mood,
                "created_at": msg.created_at,
                "confidence_score": msg.confidence_score
            }
            for msg in messages
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch AI messages: {str(e)}")


@router.get("/emotion/profile", response_model=EmotionProfileResponse)
async def get_emotion_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """감정 프로필 조회"""
    try:
        profile = db.query(EmotionProfile).filter(
            EmotionProfile.user_id == current_user.id
        ).first()
        
        if not profile:
            # 기본 감정 프로필 생성
            profile = EmotionProfile(
                user_id=current_user.id,
                current_mood="neutral",
                emotion_history={},
                dominant_emotions={}
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emotion profile: {str(e)}")


@router.post("/emotion/update")
async def update_emotion_state(
    emotion: str = Query(..., regex="^(joy|sad|angry|surprise|fear|disgust|neutral|excited|calm)$"),
    intensity: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """감정 상태 업데이트"""
    try:
        # 감정 프로필 업데이트
        profile = db.query(EmotionProfile).filter(
            EmotionProfile.user_id == current_user.id
        ).first()
        
        if profile:
            profile.current_mood = emotion
            profile.mood_intensity = intensity
            
            # 감정 히스토리 업데이트
            history = profile.emotion_history or {}
            current_time = datetime.utcnow().isoformat()
            history[current_time] = {"emotion": emotion, "intensity": intensity}
            
            # 최근 100개 기록만 유지
            if len(history) > 100:
                sorted_times = sorted(history.keys())
                for old_time in sorted_times[:-100]:
                    del history[old_time]
            
            profile.emotion_history = history
            profile.last_updated = datetime.utcnow()
            
            db.commit()
        
        # Redis에 실시간 감정 상태 캐싱
        await redis.hset(
            f"user:{current_user.id}:emotion",
            mapping={
                "mood": emotion,
                "intensity": str(intensity),
                "updated_at": datetime.utcnow().isoformat()
            }
        )
        
        return {"success": True, "emotion": emotion, "intensity": intensity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update emotion: {str(e)}")


@router.get("/moderation/history")
async def get_moderation_history(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """모더레이션 기록 조회"""
    try:
        from ..models.chat_models import ChatModeration
        
        history = db.query(ChatModeration).filter(
            ChatModeration.user_id == current_user.id
        ).order_by(ChatModeration.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": record.id,
                "action_type": record.action_type,
                "reason": record.reason,
                "severity_level": record.severity_level,
                "auto_moderation": record.auto_moderation,
                "created_at": record.created_at,
                "expires_at": record.expires_at
            }
            for record in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch moderation history: {str(e)}")
