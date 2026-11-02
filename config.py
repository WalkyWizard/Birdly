import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

AI_VISION_URL = os.getenv("AI_VISION_URL", "http://127.0.0.1:8001")
AI_AUDIO_URL = os.getenv("AI_AUDIO_URL", "http://127.0.0.1:8002")
AI_INFO_URL = os.getenv("AI_INFO_URL", "http://127.0.0.1:8003")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'birdly_central.db'}")

GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8000"))

ANALYSIS_SERVICE_URL = os.getenv("ANALYSIS_SERVICE_URL", "http://127.0.0.1:8010")
ANALYSIS_SERVICE_PORT = int(os.getenv("ANALYSIS_SERVICE_PORT", "8010"))

HISTORY_SERVICE_URL = os.getenv("HISTORY_SERVICE_URL", "http://127.0.0.1:8020")
HISTORY_SERVICE_PORT = int(os.getenv("HISTORY_SERVICE_PORT", "8020"))

CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:8030")
CATALOG_SERVICE_PORT = int(os.getenv("CATALOG_SERVICE_PORT", "8030"))

STATS_SERVICE_URL = os.getenv("STATS_SERVICE_URL", "http://127.0.0.1:8040")
STATS_SERVICE_PORT = int(os.getenv("STATS_SERVICE_PORT", "8040"))

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
