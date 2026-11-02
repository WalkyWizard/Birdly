from typing import List, Optional, Any
from pydantic import BaseModel

class HistoryRecordSchema(BaseModel):
    id: int
    analysis_type: str
    image_name: Optional[str] = None
    predicted_species: str
    confidence: float
    analysis_date: str
    description: Optional[str] = None
    scientific_name: Optional[str] = None
    family: Optional[str] = None
    habitat: Optional[str] = None
    region: Optional[str] = None
    diet: Optional[str] = None
    audio_name: Optional[str] = None
    audio_predicted_species: Optional[str] = None
    audio_confidence: Optional[float] = None
    top3_json: Optional[str] = None
    additional_info: Optional[str] = None

    class Config:
        from_attributes = True
