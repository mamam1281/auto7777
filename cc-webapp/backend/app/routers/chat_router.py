"""
💬 Casino-Club F2P - Chat API Router
===================================
채팅 시스템 및 AI 어시스턴트 API
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta

from ..database import get_db
from ..models.auth_models import User
from ..models.chat_models import (
    ChatRoom, ChatParticipant, ChatMessage, MessageReaction,
    AIAssistant, AIConversation, AIMessage, EmotionProfile, ChatModeration
)
from ..schemas.chat_schemas import (
    ChatRoomCreate, ChatRoomResponse, ChatParticipantResponse,
    ChatMessageCreate, ChatMessageResponse, MessageReactionCreate,
    AIAssistantCreate, AIAssistantResponse, AIConversationCreate,
    AIConversationResponse, AIMessageCreate, AIMessageResponse,
    EmotionProfileUpdate, EmotionProfileResponse, ChatModerationAction
)
from ..dependencies import get_current_user
from ..services.chat_service import ChatService
from ..utils.redis import get_redis_manager
from ..utils.emotion_engine import EmotionEngine

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# WebSocket 연결 관리자
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            await websocket.send_text(message)
    
    async def broadcast_to_room(self, message: str, room_id: int):
        # 실제로는 room_id별 연결 관리가 필요하지만 여기서는 단순화
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# ========== 채팅방 관리 ==========

@router.post("/rooms", response_model=ChatRoomResponse)
async def create_chat_room(
    room_data: ChatRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """채팅방 생성"""
    try:
        chat_service = ChatService(db)
        room = await chat_service.create_room(current_user.id, room_data)
        return room
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")


@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_chat_rooms(
    room_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """채팅방 목록 조회"""
    try:
        query = db.query(ChatRoom).filter(ChatRoom.is_active == True)
        
        if room_type:
            query = query.filter(ChatRoom.room_type == room_type)
        
        rooms = query.offset(offset).limit(limit).all()
        
        # 참가자 수 추가
        for room in rooms:
            participant_count = db.query(ChatParticipant).filter(
                ChatParticipant.room_id == room.id,
                ChatParticipant.is_active == True
            ).count()
            room.participant_count = participant_count
        
        return rooms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rooms: {str(e)}")


@router.post("/rooms/{room_id}/join", response_model=ChatParticipantResponse)
async def join_chat_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """채팅방 참가"""
    try:
        chat_service = ChatService(db)
        participant = await chat_service.join_room(current_user.id, room_id)
        return participant
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join room: {str(e)}")


@router.post("/rooms/{room_id}/leave")
async def leave_chat_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """채팅방 나가기"""
    try:
        chat_service = ChatService(db)
        await chat_service.leave_room(current_user.id, room_id)
        return {"message": "Successfully left the room"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to leave room: {str(e)}")


# ========== 메시지 관리 ==========

@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_room_messages(
    room_id: int,
    limit: int = Query(50, ge=1, le=100),
    before_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """채팅방 메시지 조회"""
    try:
        # 참가자 확인
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_active == True
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not a participant of this room")
        
        query = db.query(ChatMessage).filter(
            ChatMessage.room_id == room_id,
            ChatMessage.is_deleted == False
        )
        
        if before_id:
            query = query.filter(ChatMessage.id < before_id)
        
        messages = query.order_by(ChatMessage.created_at.desc()).limit(limit).all()
        messages.reverse()  # 시간순 정렬
        
        # 발신자 닉네임 추가
        for message in messages:
            if message.sender_id:
                sender = db.query(User).filter(User.id == message.sender_id).first()
                message.sender_nickname = sender.nickname if sender else "Unknown"
        
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    room_id: int,
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    redis = Depends(get_redis_manager),
    current_user: User = Depends(get_current_user)
):
    """메시지 전송"""
    try:
        chat_service = ChatService(db, redis)
        emotion_engine = EmotionEngine(redis)
        
        # 메시지 생성
        message = await chat_service.send_message(
            current_user.id, room_id, message_data
        )
        
        # 감정 분석
        emotion_result = await emotion_engine.detect_emotion_from_text(message_data.content)
        message.emotion_detected = emotion_result["emotion"]
        message.sentiment_score = emotion_result["sentiment_score"]
        
        # 사용자 감정 프로필 업데이트
        await emotion_engine.update_user_mood(
            current_user.id,
            emotion_result["emotion"],
            confidence=emotion_result["confidence"]
        )
        
        db.commit()
        
        # WebSocket으로 실시간 전송
        message_dict = {
            "type": "new_message",
            "message": {
                "id": message.id,
                "content": message.content,
                "sender_id": message.sender_id,
                "sender_nickname": current_user.nickname,
                "emotion_detected": message.emotion_detected,
                "created_at": message.created_at.isoformat(),
                "room_id": room_id
            }
        }
        await manager.broadcast_to_room(json.dumps(message_dict), room_id)
        
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.post("/messages/{message_id}/reactions", response_model=dict)
async def add_message_reaction(
    message_id: int,
    reaction_data: MessageReactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """메시지 반응 추가"""
    try:
        # 기존 반응 확인
        existing_reaction = db.query(MessageReaction).filter(
            MessageReaction.message_id == message_id,
            MessageReaction.user_id == current_user.id,
            MessageReaction.reaction_value == reaction_data.reaction_value
        ).first()
        
        if existing_reaction:
            # 이미 같은 반응이 있으면 제거
            db.delete(existing_reaction)
            action = "removed"
        else:
            # 새 반응 추가
            reaction = MessageReaction(
                message_id=message_id,
                user_id=current_user.id,
                reaction_type=reaction_data.reaction_type,
                reaction_value=reaction_data.reaction_value
            )
            db.add(reaction)
            action = "added"
        
        db.commit()
        
        # 반응 수 업데이트
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if message:
            reactions = db.query(MessageReaction).filter(
                MessageReaction.message_id == message_id
            ).all()
            
            reaction_counts = {}
            for r in reactions:
                reaction_counts[r.reaction_value] = reaction_counts.get(r.reaction_value, 0) + 1
            
            message.reaction_counts = reaction_counts
            db.commit()
        
        return {"action": action, "reaction": reaction_data.reaction_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add reaction: {str(e)}")


# ========== AI 어시스턴트 ==========

@router.get("/assistants", response_model=List[AIAssistantResponse])
async def get_ai_assistants(
    assistant_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 어시스턴트 목록 조회"""
    try:
        query = db.query(AIAssistant).filter(AIAssistant.is_active == True)
        
        if assistant_type:
            query = query.filter(AIAssistant.assistant_type == assistant_type)
        
        assistants = query.all()
        return assistants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assistants: {str(e)}")


@router.post("/conversations", response_model=AIConversationResponse)
async def start_ai_conversation(
    conversation_data: AIConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 대화 시작"""
    try:
        chat_service = ChatService(db)
        conversation = await chat_service.start_ai_conversation(
            current_user.id, conversation_data
        )
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")


@router.post("/conversations/{conversation_id}/messages", response_model=AIMessageResponse)
async def send_ai_message(
    conversation_id: int,
    message_data: AIMessageCreate,
    db: Session = Depends(get_db),
    redis = Depends(get_redis_manager),
    current_user: User = Depends(get_current_user)
):
    """AI와 메시지 주고받기"""
    try:
        chat_service = ChatService(db, redis)
        
        # 사용자 메시지 저장
        user_message = await chat_service.add_ai_message(
            conversation_id, current_user.id, message_data
        )
        
        # AI 응답 생성
        ai_response = await chat_service.generate_ai_response(
            conversation_id, current_user.id, message_data.content
        )
        
        return ai_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send AI message: {str(e)}")


@router.get("/conversations/{conversation_id}/messages", response_model=List[AIMessageResponse])
async def get_ai_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 대화 메시지 조회"""
    try:
        # 권한 확인
        conversation = db.query(AIConversation).filter(
            AIConversation.id == conversation_id,
            AIConversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = db.query(AIMessage).filter(
            AIMessage.conversation_id == conversation_id
        ).order_by(AIMessage.created_at.desc()).limit(limit).all()
        
        messages.reverse()  # 시간순 정렬
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI messages: {str(e)}")


# ========== 감정 프로필 ==========

@router.get("/emotion-profile", response_model=EmotionProfileResponse)
async def get_emotion_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 감정 프로필 조회"""
    try:
        profile = db.query(EmotionProfile).filter(
            EmotionProfile.user_id == current_user.id
        ).first()
        
        if not profile:
            # 프로필이 없으면 기본값으로 생성
            profile = EmotionProfile(user_id=current_user.id)
            db.add(profile)
            db.commit()
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get emotion profile: {str(e)}")


@router.put("/emotion-profile", response_model=EmotionProfileResponse)
async def update_emotion_profile(
    profile_data: EmotionProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 감정 프로필 업데이트"""
    try:
        profile = db.query(EmotionProfile).filter(
            EmotionProfile.user_id == current_user.id
        ).first()
        
        if not profile:
            profile = EmotionProfile(user_id=current_user.id)
            db.add(profile)
        
        # 필드 업데이트
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(profile, field) and value is not None:
                setattr(profile, field, value)
        
        profile.last_updated = datetime.utcnow()
        db.commit()
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update emotion profile: {str(e)}")


# ========== WebSocket 연결 ==========

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket 채팅 연결"""
    try:
        # 참가자 확인
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == user_id,
            ChatParticipant.is_active == True
        ).first()
        
        if not participant:
            await websocket.close(code=4003, reason="Not authorized")
            return
        
        await manager.connect(websocket, user_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # 메시지 타입에 따른 처리
                if message_data.get("type") == "message":
                    # 실시간 메시지 브로드캐스트는 send_message에서 처리
                    pass
                elif message_data.get("type") == "typing":
                    # 타이핑 상태 브로드캐스트
                    typing_data = {
                        "type": "typing",
                        "user_id": user_id,
                        "is_typing": message_data.get("is_typing", False)
                    }
                    await manager.broadcast_to_room(json.dumps(typing_data), room_id)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
            
    except Exception as e:
        await websocket.close(code=4000, reason=f"Error: {str(e)}")
