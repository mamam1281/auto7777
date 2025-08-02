"""
🧠 Casino-Club F2P - Quiz Schemas
===============================
퀴즈 시스템 Pydantic 스키마 정의
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class QuizCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    category_type: str = "general"


class QuizCategoryResponse(QuizCategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    quiz_type: str = "general"
    difficulty: str = "medium"
    time_limit: int = 300
    max_attempts: int = 3
    reward_tokens: int = 100


class QuizResponse(QuizBase):
    id: int
    category_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizQuestionBase(BaseModel):
    text: str
    question_type: str = "multiple_choice"
    order: int = 0
    points: int = 10
    explanation: Optional[str] = None


class QuizQuestionResponse(QuizQuestionBase):
    id: int
    quiz_id: int
    answers: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


class QuizAttemptCreate(BaseModel):
    session_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class QuizAttemptResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    session_id: Optional[str] = None
    start_time: datetime
    submitted_at: Optional[datetime] = None
    completion_time: Optional[int] = None
    total_score: int = 0
    correct_answers: int = 0
    total_questions: int = 0
    risk_profile_result: Optional[str] = None
    personality_traits: Optional[Dict[str, Any]] = None
    status: str
    feedback: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class QuizAnswerSubmit(BaseModel):
    question_id: int
    answer_id: Optional[int] = None
    answer_text: Optional[str] = None
    time_taken: Optional[int] = None


class QuizLeaderboardResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: Optional[int] = None
    category_id: Optional[int] = None
    period_type: str
    best_score: int
    average_score: float
    total_attempts: int
    completion_rate: float
    rank_position: Optional[int] = None
    last_updated: datetime
    
    class Config:
        from_attributes = True


class QuizStatsResponse(BaseModel):
    total_attempts: int
    total_completed: int
    average_score: float
    best_score: int
    completion_rate: float
    favorite_categories: List[Dict[str, Any]]
    recent_performance: List[Dict[str, Any]]
    risk_profile_summary: Optional[Dict[str, Any]] = None
