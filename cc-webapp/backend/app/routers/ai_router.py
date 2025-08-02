"""
🤖 Casino-Club F2P - AI Recommendation API Router
===============================================
AI 기반 개인화 추천 시스템 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta

from ..database import get_db
from ..models.auth_models import User
from ..models.ai_models import (
    UserRecommendation, RecommendationTemplate, RecommendationInteraction,
    UserPreference, AIModel, ModelPrediction, ContentPersonalization
)
from ..schemas.ai_schemas import (
    RecommendationResponse, UserPreferenceResponse, RecommendationCreate,
    InteractionCreate, PreferenceUpdate, PersonalizationResponse
)
from ..services.auth_service import get_current_user
from ..services.ai_service import AIRecommendationService
from ..utils.redis_client import get_redis

router = APIRouter(prefix="/api/ai", tags=["AI Recommendation"])

@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_user_recommendations(
    recommendation_type: Optional[str] = Query(None, regex="^(game|reward|mission|content)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """사용자 맞춤 추천 목록 조회"""
    try:
        ai_service = AIRecommendationService(db, redis)
        recommendations = await ai_service.get_user_recommendations(
            user_id=current_user.id,
            recommendation_type=recommendation_type,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recommendations: {str(e)}")


@router.post("/recommendations/generate", response_model=List[RecommendationResponse])
async def generate_recommendations(
    force_refresh: bool = Query(False),
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """새로운 추천 생성"""
    try:
        ai_service = AIRecommendationService(db, redis)
        recommendations = await ai_service.generate_recommendations(
            user_id=current_user.id,
            force_refresh=force_refresh
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")


@router.post("/recommendations/{recommendation_id}/interact")
async def record_recommendation_interaction(
    recommendation_id: int,
    interaction_data: InteractionCreate,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """추천 상호작용 기록"""
    try:
        ai_service = AIRecommendationService(db, redis)
        result = await ai_service.record_interaction(
            recommendation_id=recommendation_id,
            user_id=current_user.id,
            interaction_data=interaction_data
        )
        return {"success": True, "interaction_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record interaction: {str(e)}")


@router.get("/preferences", response_model=UserPreferenceResponse)
async def get_user_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 선호도 프로필 조회"""
    try:
        preference = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()
        
        if not preference:
            # 기본 선호도 생성
            preference = UserPreference(
                user_id=current_user.id,
                preferred_games={},
                preferred_reward_types={},
                active_hours={},
                content_categories={}
            )
            db.add(preference)
            db.commit()
            db.refresh(preference)
        
        return preference
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch preferences: {str(e)}")


@router.put("/preferences", response_model=UserPreferenceResponse)
async def update_user_preferences(
    preference_data: PreferenceUpdate,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """사용자 선호도 업데이트"""
    try:
        ai_service = AIRecommendationService(db, redis)
        preference = await ai_service.update_user_preferences(
            user_id=current_user.id,
            preference_data=preference_data
        )
        return preference
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")


@router.get("/personalization", response_model=PersonalizationResponse)
async def get_personalization_data(
    content_type: str = Query(..., regex="^(game|ui|message|reward)$"),
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """개인화 데이터 조회"""
    try:
        ai_service = AIRecommendationService(db, redis)
        personalization = await ai_service.get_personalization_data(
            user_id=current_user.id,
            content_type=content_type
        )
        return personalization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch personalization: {str(e)}")


@router.get("/insights", response_model=Dict[str, Any])
async def get_user_insights(
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """사용자 행동 인사이트"""
    try:
        ai_service = AIRecommendationService(db, redis)
        insights = await ai_service.get_user_insights(current_user.id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch insights: {str(e)}")


@router.get("/predictions/churn", response_model=Dict[str, Any])
async def get_churn_prediction(
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """이탈 예측"""
    try:
        ai_service = AIRecommendationService(db, redis)
        prediction = await ai_service.predict_churn(current_user.id)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict churn: {str(e)}")


@router.get("/predictions/ltv", response_model=Dict[str, Any])
async def get_ltv_prediction(
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """LTV 예측"""
    try:
        ai_service = AIRecommendationService(db, redis)
        prediction = await ai_service.predict_ltv(current_user.id)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict LTV: {str(e)}")


@router.get("/recommendations/performance", response_model=Dict[str, Any])
async def get_recommendation_performance(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """추천 성능 분석"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 추천별 상호작용 통계
        interactions = db.query(RecommendationInteraction).join(
            UserRecommendation
        ).filter(
            UserRecommendation.user_id == current_user.id,
            RecommendationInteraction.created_at >= start_date
        ).all()
        
        # 성능 메트릭 계산
        total_recommendations = len(set(i.recommendation_id for i in interactions))
        total_interactions = len(interactions)
        
        interaction_types = {}
        for interaction in interactions:
            interaction_type = interaction.interaction_type
            interaction_types[interaction_type] = interaction_types.get(interaction_type, 0) + 1
        
        click_rate = interaction_types.get('click', 0) / total_recommendations if total_recommendations > 0 else 0
        completion_rate = interaction_types.get('complete', 0) / total_recommendations if total_recommendations > 0 else 0
        
        return {
            "period_days": days,
            "total_recommendations": total_recommendations,
            "total_interactions": total_interactions,
            "interaction_breakdown": interaction_types,
            "click_rate": click_rate,
            "completion_rate": completion_rate,
            "engagement_score": (click_rate + completion_rate) / 2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance: {str(e)}")


@router.post("/feedback")
async def submit_ai_feedback(
    feedback_data: Dict[str, Any],
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """AI 추천에 대한 피드백 제출"""
    try:
        ai_service = AIRecommendationService(db, redis)
        result = await ai_service.process_feedback(
            user_id=current_user.id,
            feedback_data=feedback_data
        )
        return {"success": True, "message": "Feedback processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")


@router.get("/models/status", response_model=List[Dict[str, Any]])
async def get_ai_models_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI 모델 상태 조회"""
    try:
        models = db.query(AIModel).filter(
            AIModel.is_production == True,
            AIModel.status == "active"
        ).all()
        
        model_status = []
        for model in models:
            status_info = {
                "name": model.name,
                "version": model.version,
                "type": model.model_type,
                "accuracy": model.accuracy,
                "last_trained": model.trained_at,
                "status": model.status
            }
            model_status.append(status_info)
        
        return model_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch model status: {str(e)}")


@router.get("/segments/recommendation", response_model=Dict[str, Any])
async def get_segment_based_recommendations(
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    """세그먼트 기반 추천"""
    try:
        ai_service = AIRecommendationService(db, redis)
        recommendations = await ai_service.get_segment_recommendations(current_user.id)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch segment recommendations: {str(e)}")
