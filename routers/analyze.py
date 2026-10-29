import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import AnalysisRecord
from schemas import ImageAnalysisResponse, AudioAnalysisResponse, MultimodalAnalysisResponse
from services.ai_client import ai_client

router = APIRouter(prefix="/api/analyze", tags=["Analyze"])

@router.post("/image", response_model=ImageAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не вказано")

    file_bytes = await file.read()
    ai_res = await ai_client.predict_image(file_bytes, file.filename)

    if not ai_res.get("success"):
        raise HTTPException(status_code=400, detail=ai_res.get("error", "Помилка аналізу зображення"))

    species = ai_res["predicted_species"]
    conf = ai_res["confidence"]
    info = ai_res.get("bird_info", {})
    variants = ai_res.get("variants", [])

    desc = f"{info.get('ukr_name', species)} ({info.get('scientific_name', '')})"
    add_info = f"Середовище: {info.get('habitat', 'Невідомо')}. Охоронний статус: {info.get('conservation_status', 'Невідомо')}."

    record = AnalysisRecord(
        analysis_type="image",
        image_name=file.filename,
        predicted_species=species,
        confidence=conf,
        analysis_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description=desc,
        scientific_name=info.get("scientific_name"),
        family=info.get("family"),
        habitat=info.get("habitat"),
        region=info.get("region"),
        diet=info.get("diet"),
        size=info.get("size"),
        conservation_status=info.get("conservation_status"),
        interesting_facts=info.get("interesting_facts"),
        top3_json=json.dumps(variants),
        additional_info=add_info
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ImageAnalysisResponse(
        success=True,
        record_id=record.id,
        file_name=file.filename,
        predicted_species=species,
        confidence=conf,
        variants=variants,
        bird_info=info
    )

@router.post("/audio", response_model=AudioAnalysisResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не вказано")

    file_bytes = await file.read()
    ai_res = await ai_client.predict_audio(file_bytes, file.filename)

    if not ai_res.get("success"):
        raise HTTPException(status_code=400, detail=ai_res.get("error", "Помилка аналізу аудіо"))

    species = ai_res["predicted_species"]
    conf = ai_res["confidence"]
    info = ai_res.get("bird_info", {})
    variants = ai_res.get("variants", [])

    desc = f"{info.get('ukr_name', species)} ({ai_res['status_description']})"

    record = AnalysisRecord(
        analysis_type="audio",
        audio_name=file.filename,
        predicted_species=species,
        confidence=conf,
        analysis_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description=desc,
        scientific_name=info.get("scientific_name"),
        family=info.get("family"),
        habitat=info.get("habitat"),
        region=info.get("region"),
        diet=info.get("diet"),
        size=info.get("size"),
        conservation_status=info.get("conservation_status"),
        interesting_facts=info.get("interesting_facts"),
        audio_predicted_species=species,
        audio_confidence=conf,
        top3_json=json.dumps(variants),
        additional_info=ai_res["status_description"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return AudioAnalysisResponse(
        success=True,
        record_id=record.id,
        file_name=file.filename,
        predicted_species=species,
        confidence=conf,
        is_reliable=ai_res["is_reliable"],
        status_description=ai_res["status_description"],
        variants=variants,
        bird_info=info
    )

@router.post("/multimodal", response_model=MultimodalAnalysisResponse)
async def analyze_multimodal(
    image_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    img_bytes = await image_file.read()
    aud_bytes = await audio_file.read()

    img_res = await ai_client.predict_image(img_bytes, image_file.filename)
    aud_res = await ai_client.predict_audio(aud_bytes, audio_file.filename)

    if not img_res.get("success") or not aud_res.get("success"):
        raise HTTPException(status_code=400, detail="Помилка мультимодальної обробки")

    comp = await ai_client.compare_modalities(
        img_res["predicted_species"],
        aud_res["predicted_species"],
        img_res["confidence"],
        aud_res["confidence"]
    )

    info = img_res.get("bird_info", {})
    desc = f"{info.get('ukr_name', img_res['predicted_species'])} (Мультимодальне зіставлення)"
    add_info = f"{comp['verdict']}. {comp['reliability_note']}"

    record = AnalysisRecord(
        analysis_type="multimodal",
        image_name=image_file.filename,
        predicted_species=img_res["predicted_species"],
        confidence=img_res["confidence"],
        analysis_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description=desc,
        scientific_name=info.get("scientific_name"),
        family=info.get("family"),
        habitat=info.get("habitat"),
        region=info.get("region"),
        diet=info.get("diet"),
        size=info.get("size"),
        conservation_status=info.get("conservation_status"),
        interesting_facts=info.get("interesting_facts"),
        audio_name=audio_file.filename,
        audio_predicted_species=aud_res["predicted_species"],
        audio_confidence=aud_res["confidence"],
        top3_json=json.dumps(img_res.get("variants", [])),
        additional_info=add_info
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return MultimodalAnalysisResponse(
        success=True,
        record_id=record.id,
        image_result=ImageAnalysisResponse(
            success=True,
            file_name=image_file.filename,
            predicted_species=img_res["predicted_species"],
            confidence=img_res["confidence"],
            variants=img_res.get("variants", []),
            bird_info=info
        ),
        audio_result=AudioAnalysisResponse(
            success=True,
            file_name=audio_file.filename,
            predicted_species=aud_res["predicted_species"],
            confidence=aud_res["confidence"],
            is_reliable=aud_res["is_reliable"],
            status_description=aud_res["status_description"],
            variants=aud_res.get("variants", []),
            bird_info=aud_res.get("bird_info")
        ),
        verdict=comp["verdict"],
        reliability_note=comp["reliability_note"],
        is_match=comp["is_match"],
        match_level=comp["match_level"]
    )
