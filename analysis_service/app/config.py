import os

AI_VISION_URL = os.getenv("AI_VISION_URL", "http://127.0.0.1:8001")
AI_AUDIO_URL = os.getenv("AI_AUDIO_URL", "http://127.0.0.1:8002")
AI_INFO_URL = os.getenv("AI_INFO_URL", "http://127.0.0.1:8003")

HISTORY_SERVICE_URL = os.getenv("HISTORY_SERVICE_URL", "http://127.0.0.1:8020")

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
