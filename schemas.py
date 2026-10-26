from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class VariantItem(BaseModel):
    species: str
    confidence: float

class BirdInfoSchema(BaseModel):
    ukr_name: str
    scientific_name: str
    family: str
    habitat: str
    region: str
    diet: str
    size: str
    conservation_status: str
    interesting_facts: str

class ImageAnalysisResponse(BaseModel):
    success: bool
    record_id: Optional[int] = None
    file_name: str
    predicted_species: str
    confidence: float
    variants: List[VariantItem]
    bird_info: Optional[BirdInfoSchema] = None
    error: Optional[str] = None

class AudioAnalysisResponse(BaseModel):
    success: bool
    record_id: Optional[int] = None
    file_name: str
    predicted_species: str
    confidence: float
    is_reliable: bool
    status_description: str
    variants: List[VariantItem]
    bird_info: Optional[BirdInfoSchema] = None
    error: Optional[str] = None

class MultimodalAnalysisResponse(BaseModel):
    success: bool
    record_id: Optional[int] = None
    image_result: ImageAnalysisResponse
    audio_result: AudioAnalysisResponse
    verdict: str
    reliability_note: str
    is_match: bool
    match_level: str

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

class StatsSummarySchema(BaseModel):
    total_analyzed: int
    most_frequent_species: List[List[Any]]
    highest_confidence: Optional[HistoryRecordSchema] = None
    lowest_confidence: Optional[HistoryRecordSchema] = None
