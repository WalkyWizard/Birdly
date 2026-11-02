import os

GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8000"))

ANALYSIS_SERVICE_URL = os.getenv("ANALYSIS_SERVICE_URL", "http://127.0.0.1:8010")
HISTORY_SERVICE_URL = os.getenv("HISTORY_SERVICE_URL", "http://127.0.0.1:8020")
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:8030")
STATS_SERVICE_URL = os.getenv("STATS_SERVICE_URL", "http://127.0.0.1:8040")

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
