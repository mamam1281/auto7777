"""
💬 Casino-Club F2P - Chat Schemas
===============================
채팅 시스템 Pydantic 스키마 정의
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatRoomBase(BaseModel):
    name: str
    room_type: str = "public"
    description: Optional[str] = None
    max_participants: int = 100
    allow_anonymous: bool = False
    auto_moderation: bool = True
    ai_assistant_enabled: bool = True


class RoomCreate(ChatRoomBase):
    pass


class ChatRoomResponse(ChatRoomBase):
    id: int
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    participant_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class ChatParticipantResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    role: str
    is_active: bool
    is_muted: bool
    joined_at: datetime
    last_seen: Optional[datetime] = None
    message_count: int
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: str = "text"
    formatted_content: Optional[Dict[str, Any]] = None
    reply_to_id: Optional[int] = None
    thread_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: int
    room_id: int
    sender_id: Optional[int] = None
    message_type: str
    content: str
    formatted_content: Optional[Dict[str, Any]] = None
    emotion_detected: Optional[str] = None
    sentiment_score: Optional[float] = None
    ai_generated: bool
    ai_model_version: Optional[str] = None
    reply_to_id: Optional[int] = None
    thread_id: Optional[str] = None
    is_edited: bool
    is_deleted: bool
    reaction_counts: Optional[Dict[str, int]] = None
    read_by: Optional[List[int]] = None
    created_at: datetime
    edited_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MessageReactionCreate(BaseModel):
    reaction_type: str = "emoji"
    reaction_value: str = Field(..., min_length=1, max_length=10)


class AIAssistantBase(BaseModel):
    name: str
    assistant_type: str = "general"
    personality: Optional[Dict[str, Any]] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    prompt_template: Optional[str] = None
    response_style: Optional[Dict[str, Any]] = None
    default_mood: str = "neutral"
    mood_adaptation: bool = True
    emotion_responsiveness: float = 0.7


class AIAssistantResponse(AIAssistantBase):
    id: int
    can_access_user_data: bool
    can_make_recommendations: bool
    can_provide_rewards: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIConversationCreate(BaseModel):
    assistant_id: int
    conversation_type: str = "general"
    context_data: Optional[Dict[str, Any]] = None


class AIConversationResponse(BaseModel):
    id: int
    user_id: int
    assistant_id: int
    conversation_type: str
    context_data: Optional[Dict[str, Any]] = None
    status: str
    current_mood: str
    user_satisfaction: Optional[float] = None
    message_count: int
    duration_minutes: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    last_activity: datetime
    
    class Config:
        from_attributes = True


class AIMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = "text"


class AIMessageResponse(BaseModel):
    id: int
    conversation_id: int
    message_type: str
    content: str
    sender_type: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None
    detected_emotion: Optional[str] = None
    response_mood: Optional[str] = None
    personalization_applied: Optional[Dict[str, Any]] = None
    user_feedback: Optional[str] = None
    follow_up_needed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmotionProfileBase(BaseModel):
    current_mood: str = "neutral"
    mood_intensity: float = 0.5
    emotion_history: Optional[Dict[str, Any]] = None
    dominant_emotions: Optional[Dict[str, Any]] = None
    emotion_triggers: Optional[Dict[str, Any]] = None
    response_patterns: Optional[Dict[str, Any]] = None
    preferred_mood_responses: Optional[Dict[str, Any]] = None
    sensitivity_level: float = 0.5


class EmotionProfileResponse(EmotionProfileBase):
    id: int
    user_id: int
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatModerationCreate(BaseModel):
    message_id: Optional[int] = None
    user_id: int
    action_type: str = Field(..., regex="^(warning|mute|ban|delete)$")
    reason: Optional[str] = None
    severity_level: int = Field(1, ge=1, le=5)
    action_taken: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class ChatModerationResponse(BaseModel):
    id: int
    message_id: Optional[int] = None
    user_id: int
    moderator_id: Optional[int] = None
    action_type: str
    reason: Optional[str] = None
    auto_moderation: bool
    severity_level: int
    action_taken: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    room_id: Optional[int] = None
    user_id: Optional[int] = None
    timestamp: Optional[datetime] = None
