import os

AI_INFO_URL = os.getenv("AI_INFO_URL", "http://127.0.0.1:8003")

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
