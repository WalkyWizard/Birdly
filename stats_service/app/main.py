import io
import csv
from collections import Counter
from typing import Dict, Any
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import config
from .database import get_db
from .models import AnalysisRecord
from .schemas import StatsSummarySchema, HistoryRecordSchema

app = FastAPI(title="Birdly Stats Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "Birdly Stats Microservice"}

@app.get("/stats", response_model=StatsSummarySchema)
def get_stats(db: Session = Depends(get_db)):
    records = db.query(AnalysisRecord).all()
    total = len(records)

    if total == 0:
        return StatsSummarySchema(
            total_analyzed=0,
            most_frequent_species=[]
        )

    species_counter = Counter([r.predicted_species for r in records if r.predicted_species])
    most_frequent = [[k, v] for k, v in species_counter.most_common(6)]

    sorted_by_conf = sorted(records, key=lambda x: x.confidence, reverse=True)
    highest = sorted_by_conf[0] if sorted_by_conf else None
    lowest = sorted_by_conf[-1] if sorted_by_conf else None

    return StatsSummarySchema(
        total_analyzed=total,
        most_frequent_species=most_frequent,
        highest_confidence=HistoryRecordSchema.from_orm(highest) if highest else None,
        lowest_confidence=HistoryRecordSchema.from_orm(lowest) if lowest else None
    )

@app.get("/stats/csv")
def download_csv(db: Session = Depends(get_db)):
    records = db.query(AnalysisRecord).order_by(AnalysisRecord.id.desc()).all()

    output = io.StringIO()
    fieldnames = [
        "image_name",
        "predicted_species",
        "confidence",
        "analysis_date",
        "description",
        "scientific_name",
        "family",
        "audio_name",
        "audio_predicted_species",
        "audio_confidence"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()

    for r in records:
        writer.writerow({
            "image_name": r.image_name or "",
            "predicted_species": r.predicted_species or "",
            "confidence": r.confidence,
            "analysis_date": r.analysis_date,
            "description": r.description or "",
            "scientific_name": r.scientific_name or "",
            "family": r.family or "",
            "audio_name": r.audio_name or "",
            "audio_predicted_species": r.audio_predicted_species or "",
            "audio_confidence": r.audio_confidence or 0.0
        })

    csv_data = "\ufeff" + output.getvalue()
    return Response(
        content=csv_data.encode("utf-8"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bird_analysis.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8040, reload=False)
