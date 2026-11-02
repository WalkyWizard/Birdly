from typing import Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import config
from .ai_client import ai_client

app = FastAPI(title="Birdly Catalog Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "Birdly Catalog Microservice"}

@app.get("/birds")
async def get_birds_metadata() -> Dict[str, Any]:
    return await ai_client.get_all_birds()

@app.get("/birds/info/{species_name}")
async def get_bird_details(species_name: str) -> Dict[str, Any]:
    return await ai_client.get_bird_info(species_name)

@app.get("/birds/compare/{species_a}/{species_b}")
async def compare_birds(species_a: str, species_b: str) -> Dict[str, Any]:
    info1 = await ai_client.get_bird_info(species_a)
    info2 = await ai_client.get_bird_info(species_b)

    fields = [
        ("Українська назва", "ukr_name"),
        ("Наукова назва", "scientific_name"),
        ("Родина", "family"),
        ("Середовище існування", "habitat"),
        ("Географічне поширення", "region"),
        ("Тип живлення", "diet"),
        ("Розміри", "size"),
        ("Природоохоронний статус", "conservation_status")
    ]

    rows = []
    for label, key in fields:
        v1 = info1.get(key, "Дані відсутні")
        v2 = info2.get(key, "Дані відсутні")
        rows.append({
            "parameter": label,
            "bird1_value": v1,
            "bird2_value": v2,
            "is_identical": v1 == v2
        })

    same_family = info1.get("family") == info2.get("family") and info1.get("family") != "Дані відсутні"

    return {
        "bird1_name": info1.get("ukr_name", species_a),
        "bird2_name": info2.get("ukr_name", species_b),
        "same_family": same_family,
        "comparison_rows": rows
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8030, reload=False)
