import json
from datetime import datetime
from typing import Dict, Any
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from . import config
from .ai_client import ai_client
from .rabbit_client import publish_notification
from .schemas import (
    ImageAnalysisResponse,
    AudioAnalysisResponse,
    MultimodalAnalysisResponse,
    VariantItem
)

app = FastAPI(title="Birdly Analysis Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def save_history_record(payload: Dict[str, Any]) -> int:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{config.HISTORY_SERVICE_URL}/history", json=payload)
            if resp.status_code == 200:
                return resp.json().get("id", 0)
    except httpx.RequestError:
        pass
    return 0

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "Birdly Analysis Microservice"}

@app.post("/analyze/image", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
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

    record_payload = {
        "analysis_type": "image",
        "image_name": file.filename,
        "predicted_species": species,
        "confidence": conf,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": desc,
        "scientific_name": info.get("scientific_name"),
        "family": info.get("family"),
        "habitat": info.get("habitat"),
        "region": info.get("region"),
        "diet": info.get("diet"),
        "size": info.get("size"),
        "conservation_status": info.get("conservation_status"),
        "interesting_facts": info.get("interesting_facts"),
        "audio_name": None,
        "audio_predicted_species": None,
        "audio_confidence": None,
        "top3_json": json.dumps(variants),
        "additional_info": None
    }

    record_id = await save_history_record(record_payload)

    publish_notification({
        "event": "analysis_completed",
        "analysis_type": "image",
        "file_name": file.filename,
        "predicted_species": species,
        "confidence": conf,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return ImageAnalysisResponse(
        success=True,
        record_id=record_id,
        file_name=file.filename,
        predicted_species=species,
        confidence=conf,
        variants=[VariantItem(species=v["species"], confidence=v["confidence"]) for v in variants],
        bird_info=info
    )

@app.post("/analyze/audio", response_model=AudioAnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):
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

    desc = f"{info.get('ukr_name', species)} ({info.get('scientific_name', '')}) [Аудіоаналіз]"

    record_payload = {
        "analysis_type": "audio",
        "image_name": None,
        "predicted_species": species,
        "confidence": conf,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": desc,
        "scientific_name": info.get("scientific_name"),
        "family": info.get("family"),
        "habitat": info.get("habitat"),
        "region": info.get("region"),
        "diet": info.get("diet"),
        "size": info.get("size"),
        "conservation_status": info.get("conservation_status"),
        "interesting_facts": info.get("interesting_facts"),
        "audio_name": file.filename,
        "audio_predicted_species": species,
        "audio_confidence": conf,
        "top3_json": json.dumps(variants),
        "additional_info": ai_res.get("status_description")
    }

    record_id = await save_history_record(record_payload)

    publish_notification({
        "event": "analysis_completed",
        "analysis_type": "audio",
        "file_name": file.filename,
        "predicted_species": species,
        "confidence": conf,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return AudioAnalysisResponse(
        success=True,
        record_id=record_id,
        file_name=file.filename,
        predicted_species=species,
        confidence=conf,
        is_reliable=ai_res.get("is_reliable", True),
        status_description=ai_res.get("status_description", ""),
        variants=[VariantItem(species=v["species"], confidence=v["confidence"]) for v in variants],
        bird_info=info
    )

@app.post("/analyze/multimodal", response_model=MultimodalAnalysisResponse)
async def analyze_multimodal(
    image_file: UploadFile = File(...),
    audio_file: UploadFile = File(...)
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
    add_info = f"{comp['verdict']} {comp['reliability_note']}"

    record_payload = {
        "analysis_type": "multimodal",
        "image_name": image_file.filename,
        "predicted_species": img_res["predicted_species"],
        "confidence": img_res["confidence"],
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": desc,
        "scientific_name": info.get("scientific_name"),
        "family": info.get("family"),
        "habitat": info.get("habitat"),
        "region": info.get("region"),
        "diet": info.get("diet"),
        "size": info.get("size"),
        "conservation_status": info.get("conservation_status"),
        "interesting_facts": info.get("interesting_facts"),
        "audio_name": audio_file.filename,
        "audio_predicted_species": aud_res["predicted_species"],
        "audio_confidence": aud_res["confidence"],
        "top3_json": json.dumps(img_res.get("variants", [])),
        "additional_info": add_info
    }

    record_id = await save_history_record(record_payload)

    publish_notification({
        "event": "analysis_completed",
        "analysis_type": "multimodal",
        "image_file": image_file.filename,
        "audio_file": audio_file.filename,
        "predicted_species": img_res["predicted_species"],
        "confidence": img_res["confidence"],
        "is_match": comp["is_match"],
        "verdict": comp["verdict"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return MultimodalAnalysisResponse(
        success=True,
        record_id=record_id,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8010, reload=False)
