"""
🤖 Casino-Club F2P - AI Schemas
==============================
AI 추천 시스템 Pydantic 스키마 정의
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class RecommendationTemplateBase(BaseModel):
    name: str
    template_type: str
    target_segment: Optional[str] = None
    trigger_conditions: Dict[str, Any] = {}
    content_template: Dict[str, Any] = {}
    priority: int = 1


class RecommendationCreate(BaseModel):
    template_id: Optional[int] = None
    recommendation_type: str
    title: str
    description: Optional[str] = None
    content_data: Dict[str, Any] = {}
    priority_score: float = 0.5


class RecommendationResponse(BaseModel):
    id: int
    user_id: int
    template_id: Optional[int] = None
    recommendation_type: str
    title: str
    description: Optional[str] = None
    content_data: Dict[str, Any]
    priority_score: float
    confidence_score: float
    personalization_factors: Optional[Dict[str, Any]] = None
    status: str
    shown_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    source: str
    algorithm_version: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    interaction_type: str = Field(..., description="view, click, dismiss, complete")
    interaction_data: Optional[Dict[str, Any]] = None
    duration: Optional[int] = None
    result_data: Optional[Dict[str, Any]] = None


class UserPreferenceBase(BaseModel):
    preferred_games: Dict[str, Any] = {}
    game_difficulty_preference: str = "medium"
    risk_tolerance: float = 0.5
    preferred_reward_types: Dict[str, Any] = {}
    spending_pattern: Dict[str, Any] = {}
    active_hours: Dict[str, Any] = {}
    session_duration_preference: Optional[int] = None
    content_categories: Dict[str, Any] = {}
    interaction_style: Optional[str] = None


class PreferenceUpdate(UserPreferenceBase):
    pass


class UserPreferenceResponse(UserPreferenceBase):
    id: int
    user_id: int
    learning_rate: float
    last_model_update: Optional[datetime] = None
    preference_accuracy: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PersonalizationResponse(BaseModel):
    content_type: str
    personalization_data: Dict[str, Any]
    effectiveness_score: float
    last_applied: Optional[datetime] = None
    recommendations: List[Dict[str, Any]] = []


class AIModelBase(BaseModel):
    name: str
    model_type: str
    version: str
    description: Optional[str] = None
    algorithm: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None


class AIModelResponse(AIModelBase):
    id: int
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    status: str
    is_production: bool
    trained_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    prediction_type: str
    input_features: Dict[str, Any]


class PredictionResponse(BaseModel):
    id: int
    model_id: int
    user_id: int
    prediction_type: str
    input_features: Dict[str, Any]
    prediction_result: Dict[str, Any]
    confidence_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PersonalizationRuleBase(BaseModel):
    name: str
    rule_type: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int = 1


class PersonalizationRuleResponse(PersonalizationRuleBase):
    id: int
    is_active: bool
    execution_count: int
    success_rate: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
