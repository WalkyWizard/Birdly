from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    analysis_type = Column(String(50), nullable=False)
    image_name = Column(String(255), nullable=True)
    predicted_species = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    analysis_date = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    scientific_name = Column(String(255), nullable=True)
    family = Column(String(255), nullable=True)
    habitat = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)
    diet = Column(String(255), nullable=True)
    size = Column(String(255), nullable=True)
    conservation_status = Column(String(255), nullable=True)
    interesting_facts = Column(Text, nullable=True)
    audio_name = Column(String(255), nullable=True)
    audio_predicted_species = Column(String(255), nullable=True)
    audio_confidence = Column(Float, nullable=True)
    top3_json = Column(Text, nullable=True)
    additional_info = Column(Text, nullable=True)
