from typing import Dict, Any
import httpx
from . import config

class AIClient:
    def __init__(self, info_url: str = config.AI_INFO_URL):
        self.info_url = info_url.rstrip("/")

    async def get_bird_info(self, species_name: str) -> Dict[str, Any]:
        url = f"{self.info_url}/birds/{species_name}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                return {}
        except httpx.RequestError:
            return {}

    async def get_all_birds(self) -> Dict[str, Any]:
        url = f"{self.info_url}/birds"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                return {"families": [], "habitats": [], "diets": [], "species": []}
        except httpx.RequestError:
            return {"families": [], "habitats": [], "diets": [], "species": []}

ai_client = AIClient()
