from typing import Dict, Any
from fastapi import APIRouter
from services.ai_client import ai_client

router = APIRouter(prefix="/api/birds", tags=["Birds"])

@router.get("")
async def get_birds_metadata() -> Dict[str, Any]:
    return await ai_client.get_all_birds()

@router.get("/info/{species_name}")
async def get_bird_details(species_name: str) -> Dict[str, Any]:
    return await ai_client.get_bird_info(species_name)

@router.get("/compare/{species_a}/{species_b}")
async def compare_birds_endpoint(species_a: str, species_b: str) -> Dict[str, Any]:
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
