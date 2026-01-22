from pydantic import BaseModel
from typing import Optional

class PredictionCreate(BaseModel):
    league: str
    home_team: str
    away_team: str
    match_datetime: str  # ISO format: "2026-01-20T20:00:00"
    prediction_type: str
    confidence: float
    reasoning: Optional[str] = None
