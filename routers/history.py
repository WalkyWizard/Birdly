from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import AnalysisRecord
from schemas import HistoryRecordSchema

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("", response_model=List[HistoryRecordSchema])
def get_history(
    search: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
    habitat: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(AnalysisRecord)

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                AnalysisRecord.predicted_species.ilike(pattern),
                AnalysisRecord.description.ilike(pattern),
                AnalysisRecord.scientific_name.ilike(pattern),
                AnalysisRecord.audio_predicted_species.ilike(pattern)
            )
        )

    if family and family != "Усі":
        query = query.filter(AnalysisRecord.family == family)

    if habitat:
        query = query.filter(AnalysisRecord.habitat.ilike(f"%{habitat.strip()}%"))

    records = query.order_by(AnalysisRecord.id.desc()).limit(limit).all()
    return records

@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Запис не знайдено.")

    db.delete(record)
    db.commit()
    return {"success": True, "deleted_id": record_id}
