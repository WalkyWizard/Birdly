import json
from typing import List, Optional, Dict, Any
from collections import Counter
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import config
from .database import get_db, engine, Base
from .models import AnalysisRecord
from .schemas import HistoryRecordSchema

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Birdly History Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "Birdly History Microservice"}

@app.get("/history", response_model=List[HistoryRecordSchema])
def get_history(
    search: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
    habitat: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(AnalysisRecord)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                AnalysisRecord.predicted_species.ilike(s),
                AnalysisRecord.scientific_name.ilike(s),
                AnalysisRecord.family.ilike(s),
                AnalysisRecord.habitat.ilike(s),
                AnalysisRecord.region.ilike(s),
                AnalysisRecord.description.ilike(s)
            )
        )

    if family and family != "Усі":
        query = query.filter(AnalysisRecord.family.ilike(f"%{family.strip()}%"))

    if habitat:
        query = query.filter(AnalysisRecord.habitat.ilike(f"%{habitat.strip()}%"))

    records = query.order_by(AnalysisRecord.id.desc()).limit(limit).all()
    return records

@app.post("/history")
def create_history_record(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    record = AnalysisRecord(
        analysis_type=payload.get("analysis_type", "image"),
        image_name=payload.get("image_name"),
        predicted_species=payload.get("predicted_species", ""),
        confidence=float(payload.get("confidence", 0.0)),
        analysis_date=payload.get("analysis_date", ""),
        description=payload.get("description"),
        scientific_name=payload.get("scientific_name"),
        family=payload.get("family"),
        habitat=payload.get("habitat"),
        region=payload.get("region"),
        diet=payload.get("diet"),
        size=payload.get("size"),
        conservation_status=payload.get("conservation_status"),
        interesting_facts=payload.get("interesting_facts"),
        audio_name=payload.get("audio_name"),
        audio_predicted_species=payload.get("audio_predicted_species"),
        audio_confidence=payload.get("audio_confidence"),
        top3_json=payload.get("top3_json"),
        additional_info=payload.get("additional_info")
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"success": True, "id": record.id}

@app.delete("/history/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Запис не знайдено")

    db.delete(record)
    db.commit()
    return {"success": True, "deleted_id": record_id}

@app.get("/history/stats")
def get_history_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    records = db.query(AnalysisRecord).all()
    total = len(records)
    if total == 0:
        return {
            "total_analyses": 0,
            "image_analyses": 0,
            "audio_analyses": 0,
            "multimodal_analyses": 0,
            "verified_count": 0,
            "most_frequent_species": "Немає даних",
            "most_common_family": "Немає даних",
            "average_confidence": 0.0,
            "species_distribution": {}
        }

    image_count = sum(1 for r in records if r.analysis_type == "image")
    audio_count = sum(1 for r in records if r.analysis_type == "audio")
    multi_count = sum(1 for r in records if r.analysis_type == "multimodal")
    verified = sum(1 for r in records if r.confidence >= 0.5)

    species_list = [r.predicted_species for r in records if r.predicted_species]
    families_list = [r.family for r in records if r.family]

    species_counter = Counter(species_list)
    family_counter = Counter(families_list)

    most_freq_species = species_counter.most_common(1)[0][0] if species_counter else "Немає даних"
    most_common_fam = family_counter.most_common(1)[0][0] if family_counter else "Немає даних"

    avg_conf = round(sum(r.confidence for r in records) / total, 4)

    return {
        "total_analyses": total,
        "image_analyses": image_count,
        "audio_analyses": audio_count,
        "multimodal_analyses": multi_count,
        "verified_count": verified,
        "most_frequent_species": most_freq_species,
        "most_common_family": most_common_fam,
        "average_confidence": avg_conf,
        "species_distribution": dict(species_counter.most_common(10))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8020, reload=False)
