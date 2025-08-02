"""
🤖 Casino-Club F2P - AI Recommendation API Router
===============================================
AI 기반 개인화 추천 시스템 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from ..database import get_db
from ..models.auth_models import User
from ..models.ai_models import (
    UserRecommendation, RecommendationInteraction, UserPreference,
    ModelPrediction, PersonalizationRule
)
from ..schemas.ai_schemas import (
    UserRecommendationResponse, UserRecommendationCreate,
    RecommendationInteractionCreate, RecommendationInteractionResponse,
    UserPreferenceResponse, UserPreferenceUpdate,
    PersonalizationRequest, PersonalizationResponse,
    ModelPredictionResponse
)
from ..services.auth_service import get_current_user
from ..services.ai_recommendation_service import AIRecommendationService
from ..utils.redis_client import get_redis

router = APIRouter(prefix="/api/ai", tags=["AI Recommendation"])

@router.get("/recommendations", response_model=List[UserRecommendationResponse])
async def get_user_recommendations(
    recommendation_type: Optional[str] = Query(None),
    status: Optional[str] = Query("pending"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 추천 목록 조회"""
    try:
        query = db.query(UserRecommendation).filter(
            UserRecommendation.user_id == current_user.id
        )
        
        if recommendation_type:
            query = query.filter(UserRecommendation.recommendation_type == recommendation_type)
        
        if status:
            query = query.filter(UserRecommendation.status == status)
        
        recommendations = query.order_by(
            UserRecommendation.priority_score.desc(),
            UserRecommendation.created_at.desc()
        ).limit(limit).all()
        
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/recommendations/generate", response_model=List[UserRecommendationResponse])
async def generate_recommendations(
    recommendation_type: Optional[str] = Query(None),
    max_recommendations: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """AI 추천 생성"""
    try:
        ai_service = AIRecommendationService(db, redis)
        recommendations = await ai_service.generate_recommendations(
            user_id=current_user.id,
            recommendation_type=recommendation_type,
            max_recommendations=max_recommendations
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")


@router.post("/recommendations/{recommendation_id}/interact", response_model=RecommendationInteractionResponse)
async def record_recommendation_interaction(
    recommendation_id: int,
    interaction_data: RecommendationInteractionCreate,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """추천 상호작용 기록"""
    try:
        ai_service = AIRecommendationService(db, redis)
        interaction = await ai_service.record_interaction(
            recommendation_id=recommendation_id,
            user_id=current_user.id,
            interaction_data=interaction_data
        )
        
        return interaction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record interaction: {str(e)}")


@router.get("/preferences", response_model=UserPreferenceResponse)
async def get_user_preferences(
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """사용자 선호도 조회"""
    try:
        ai_service = AIRecommendationService(db, redis)
        preferences = await ai_service.get_user_preferences(current_user.id)
        
        if not preferences:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preferences: {str(e)}")


@router.put("/preferences", response_model=UserPreferenceResponse)
async def update_user_preferences(
    preference_data: UserPreferenceUpdate,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """사용자 선호도 업데이트"""
    try:
        ai_service = AIRecommendationService(db, redis)
        preferences = await ai_service.update_user_preferences(
            user_id=current_user.id,
            preference_data=preference_data
        )
        
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")


@router.post("/personalize", response_model=PersonalizationResponse)
async def get_personalized_content(
    request: PersonalizationRequest,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """개인화 콘텐츠 요청"""
    try:
        ai_service = AIRecommendationService(db, redis)
        
        # 사용자 ID 설정
        request.user_id = current_user.id
        
        # 추천 생성
        recommendations = await ai_service.generate_recommendations(
            user_id=current_user.id,
            recommendation_type=request.content_type,
            max_recommendations=request.max_recommendations
        )
        
        # 개인화 응답 생성
        response = PersonalizationResponse(
            recommendations=recommendations,
            personalization_factors={
                "user_segment": "Medium",  # 실제 세그먼트 조회 필요
                "content_type": request.content_type,
                "context_data": request.context_data or {}
            },
            confidence_score=0.8,  # 실제 신뢰도 계산 필요
            algorithm_version="v1.0",
            generated_at=datetime.utcnow()
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get personalized content: {str(e)}")


@router.get("/predictions", response_model=List[ModelPredictionResponse])
async def get_user_predictions(
    prediction_type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 AI 예측 결과 조회"""
    try:
        query = db.query(ModelPrediction).filter(
            ModelPrediction.user_id == current_user.id
        )
        
        if prediction_type:
            query = query.filter(ModelPrediction.prediction_type == prediction_type)
        
        predictions = query.order_by(
            ModelPrediction.created_at.desc()
        ).limit(limit).all()
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get predictions: {str(e)}")


@router.get("/recommendations/stats", response_model=dict)
async def get_recommendation_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """추천 시스템 통계"""
    try:
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 전체 추천 수
        total_recommendations = db.query(UserRecommendation).filter(
            UserRecommendation.user_id == current_user.id,
            UserRecommendation.created_at >= start_date
        ).count()
        
        # 클릭된 추천 수
        clicked_recommendations = db.query(UserRecommendation).filter(
            UserRecommendation.user_id == current_user.id,
            UserRecommendation.status == "clicked",
            UserRecommendation.created_at >= start_date
        ).count()
        
        # 타입별 추천 수
        type_stats = db.query(
            UserRecommendation.recommendation_type,
            db.func.count(UserRecommendation.id).label('count')
        ).filter(
            UserRecommendation.user_id == current_user.id,
            UserRecommendation.created_at >= start_date
        ).group_by(UserRecommendation.recommendation_type).all()
        
        # 상호작용 수
        total_interactions = db.query(RecommendationInteraction).filter(
            RecommendationInteraction.user_id == current_user.id,
            RecommendationInteraction.created_at >= start_date
        ).count()
        
        click_through_rate = (clicked_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
        
        return {
            "period_days": days,
            "total_recommendations": total_recommendations,
            "clicked_recommendations": clicked_recommendations,
            "click_through_rate": round(click_through_rate, 2),
            "total_interactions": total_interactions,
            "recommendations_by_type": {row[0]: row[1] for row in type_stats},
            "engagement_score": round(click_through_rate * 0.7 + (total_interactions / max(total_recommendations, 1)) * 30, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation stats: {str(e)}")


@router.post("/feedback", response_model=dict)
async def submit_ai_feedback(
    recommendation_id: int,
    feedback: str = Query(..., regex="^(helpful|not_helpful|irrelevant)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 추천에 대한 피드백 제출"""
    try:
        # 추천 확인
        recommendation = db.query(UserRecommendation).filter(
            UserRecommendation.id == recommendation_id,
            UserRecommendation.user_id == current_user.id
        ).first()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # 상호작용 기록
        interaction = RecommendationInteraction(
            recommendation_id=recommendation_id,
            user_id=current_user.id,
            interaction_type="feedback",
            interaction_data={"feedback": feedback},
            result_data={"feedback_type": feedback}
        )
        
        db.add(interaction)
        db.commit()
        
        return {"message": "Feedback submitted successfully", "feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/learning-progress", response_model=dict)
async def get_learning_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 학습 진행 상황"""
    try:
        # 사용자 선호도 조회
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()
        
        if not preferences:
            return {
                "learning_progress": 0.0,
                "data_points": 0,
                "accuracy": 0.0,
                "last_update": None,
                "status": "no_data"
            }
        
        # 상호작용 데이터 수집
        total_interactions = db.query(RecommendationInteraction).filter(
            RecommendationInteraction.user_id == current_user.id
        ).count()
        
        # 학습 진행도 계산
        learning_progress = min(total_interactions / 50.0, 1.0)  # 50개 상호작용으로 완전 학습
        
        return {
            "learning_progress": round(learning_progress * 100, 1),
            "data_points": total_interactions,
            "accuracy": round(preferences.preference_accuracy * 100, 1) if preferences.preference_accuracy else 50.0,
            "last_update": preferences.last_model_update,
            "learning_rate": preferences.learning_rate,
            "status": "learning" if learning_progress < 1.0 else "trained"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning progress: {str(e)}")
