from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from ..utils.sentiment_analyzer import SentimentAnalyzer

router = APIRouter(prefix="/ai", tags=["ai"])

class AnalyzeRequest(BaseModel):
    """감정 분석 ?�청 모델"""
    user_id: int
    text: str = Field(..., description="분석???�스??)
    context: Dict[str, Any] = Field(default_factory=dict, description="추�? 컨텍?�트")

@router.post("/analyze")
async def analyze_emotion(request: AnalyzeRequest):
    """고급 감정 분석 ?�드?�인??""
    try:
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze(request.text)
        
        return {
            "success": True,
            "data": {
                "emotion": result.emotion,
                "score": result.score,
                "confidence": result.confidence,
                "language": result.language,
                "context_aware": bool(request.context)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
