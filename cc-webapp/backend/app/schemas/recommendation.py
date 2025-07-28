from pydantic import BaseModel
from typing import List, Optional, Dict

class FinalRecommendation(BaseModel):
    game_id: int
    game_name: str
    confidence: float
    reasons: List[str]
    rewards: Optional[Dict] = None
