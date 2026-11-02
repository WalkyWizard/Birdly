from typing import Dict, Any
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from . import config
from .rabbit_client import publish_message, consume_messages, get_queue_info

app = FastAPI(title="Birdly API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-length"
}

async def forward_request(target_url: str, request: Request) -> Response:
    content = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() not in {"host", "content-length"}}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            content=content,
            headers=headers
        )
    resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in HOP_BY_HOP}
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=resp_headers,
        media_type=resp.headers.get("content-type")
    )

@app.api_route("/api/analyze/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_analyze(request: Request, path: str):
    return await forward_request(f"{config.ANALYSIS_SERVICE_URL}/analyze/{path}", request)

@app.api_route("/api/history", methods=["GET", "POST"])
async def route_history_root(request: Request):
    return await forward_request(f"{config.HISTORY_SERVICE_URL}/history", request)

@app.api_route("/api/history/{path:path}", methods=["GET", "POST", "DELETE"])
async def route_history(request: Request, path: str):
    return await forward_request(f"{config.HISTORY_SERVICE_URL}/history/{path}", request)

@app.api_route("/api/birds", methods=["GET"])
async def route_birds_root(request: Request):
    return await forward_request(f"{config.CATALOG_SERVICE_URL}/birds", request)

@app.api_route("/api/birds/{path:path}", methods=["GET", "POST"])
async def route_birds(request: Request, path: str):
    return await forward_request(f"{config.CATALOG_SERVICE_URL}/birds/{path}", request)

@app.api_route("/api/stats", methods=["GET"])
async def route_stats_root(request: Request):
    return await forward_request(f"{config.STATS_SERVICE_URL}/stats", request)

@app.api_route("/api/stats/{path:path}", methods=["GET"])
async def route_stats(request: Request, path: str):
    return await forward_request(f"{config.STATS_SERVICE_URL}/stats/{path}", request)

@app.post("/api/messages")
async def send_message(request: Request):
    payload = await request.json()
    ok = publish_message(payload)
    return {"success": ok, "queue": "birdly_notifications", "sent_message": payload}

@app.get("/api/messages")
async def get_messages(limit: int = 10):
    msgs = consume_messages("birdly_notifications", max_messages=limit)
    return {"queue": "birdly_notifications", "count": len(msgs), "messages": msgs}

@app.get("/api/messages/status")
async def get_rabbit_status():
    return get_queue_info("birdly_notifications")

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "Birdly Central API Gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=config.GATEWAY_HOST, port=config.GATEWAY_PORT, reload=False)
