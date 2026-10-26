from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException
import config

class AIClient:
    def __init__(self, base_url: str = config.AI_SERVER_URL):
        self.base_url = base_url.rstrip("/")

    async def predict_image(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        url = f"{self.base_url}/predict/image"
        files = {"file": (filename, file_bytes, "image/jpeg")}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, files=files)
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=f"Помилка AI сервера: {response.text}")
                return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Неможливо з'єднатися з AI сервером: {str(exc)}")

    async def predict_audio(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        url = f"{self.base_url}/predict/audio"
        files = {"file": (filename, file_bytes, "audio/wav")}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, files=files)
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=f"Помилка AI сервера: {response.text}")
                return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Неможливо з'єднатися з AI сервером: {str(exc)}")

    async def compare_modalities(
        self,
        image_species: str,
        audio_species: str,
        image_confidence: float,
        audio_confidence: float
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/compare/modalities"
        data = {
            "image_species": image_species,
            "audio_species": audio_species,
            "image_confidence": str(image_confidence),
            "audio_confidence": str(audio_confidence)
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, data=data)
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=f"Помилка AI сервера: {response.text}")
                return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Неможливо з'єднатися з AI сервером: {str(exc)}")

    async def get_bird_info(self, species_name: str) -> Dict[str, Any]:
        url = f"{self.base_url}/birds/{species_name}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                return {}
        except httpx.RequestError:
            return {}

    async def get_all_birds(self) -> Dict[str, Any]:
        url = f"{self.base_url}/birds"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                return {"families": [], "habitats": [], "diets": [], "species": []}
        except httpx.RequestError:
            return {"families": [], "habitats": [], "diets": [], "species": []}

ai_client = AIClient()
