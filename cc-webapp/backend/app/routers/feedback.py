from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from ..emotion_models import EmotionResult, SupportedEmotion, SupportedLanguage
from ..schemas import FeedbackResponse
from ..services.emotion_feedback_service import EmotionFeedbackService 
from ..routers.auth import get_user_from_token as get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["Feedback"])

class EmotionFeedbackRequest(BaseModel):
    emotion_result_data: Dict[str, Any] = Field(..., description="EmotionResult as dict.")
    user_segment: Optional[str] = "GENERAL"
    mission_type: Optional[str] = "GENERAL"
    context_text: Optional[str] = None

def get_emotion_feedback_service():
    try: return EmotionFeedbackService()
    except Exception as e: logger.error(f"Failed to init EmotionFeedbackService: {e}", exc_info=True); return None

@router.post("/emotion_based", response_model=Optional[FeedbackResponse], summary="Get Personalized Emotion-Based Feedback")
async def get_emotion_based_feedback_endpoint(
    request_data: EmotionFeedbackRequest = Body(...),
    feedback_service: Optional[EmotionFeedbackService] = Depends(get_emotion_feedback_service)
):
    logger.info(f"Received feedback request for user_segment: {request_data.user_segment}")
    if not feedback_service:
        raise HTTPException(status_code=503, detail="Feedback service unavailable.")

    try:
        # Convert relevant fields in emotion_result_data to enums before passing to EmotionResult
        raw_emotion_data = request_data.emotion_result_data.copy() # Work on a copy
        if 'language' in raw_emotion_data and isinstance(raw_emotion_data['language'], str):
            raw_emotion_data['language'] = SupportedLanguage[raw_emotion_data['language'].upper()]
        if 'emotion' in raw_emotion_data and isinstance(raw_emotion_data['emotion'], str):
            raw_emotion_data['emotion'] = SupportedEmotion[raw_emotion_data['emotion'].upper()]

        parsed_emotion_result = EmotionResult(**raw_emotion_data)
    except (KeyError, ValueError, TypeError) as e: # Catch specific errors
        logger.error(f"Error parsing emotion_result_data: {e}, input: {request_data.emotion_result_data}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid emotion_result_data: {e}")

    try:
        feedback = feedback_service.get_emotion_feedback(
            emotion_result=parsed_emotion_result, user_segment=request_data.user_segment,
            mission_type=request_data.mission_type, context_text=request_data.context_text
        )
    except Exception as e:
        logger.exception("Error generating emotion feedback in router.")
        raise HTTPException(status_code=500, detail="Failed to generate feedback.")

    if not feedback: logger.warning("No feedback generated for context.")
    return feedback

@router.post("/generate")
async def generate_feedback(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    service: EmotionFeedbackService = Depends(get_emotion_feedback_service)
):
    """
    사용자 감정에 기반한 피드백 생성
    
    Args:
        request: 피드백 요청 데이터
            - user_id: 사용자 ID
            - emotion: 감정 상태
            - segment: 사용자 세그먼트
            - context: 추가 컨텍스트 정보
    
    Returns:
        피드백 응답 객체
    """
    try:
        user_id = request.get("user_id")
        emotion = request.get("emotion")
        segment = request.get("segment", "Medium")
        context = request.get("context", {})
        
        # 필수 필드 검증
        if not user_id or not emotion:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # 현재 사용자 권한 확인
        if user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this resource")
        
        # 피드백 생성
        feedback = service.generate_feedback(emotion, segment, context)
        
        return {
            "success": True,
            "data": feedback
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate feedback: {str(e)}"
        }
