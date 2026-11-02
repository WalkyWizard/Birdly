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
