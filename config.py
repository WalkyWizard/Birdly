import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://127.0.0.1:8001")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'birdly_central.db'}")
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
