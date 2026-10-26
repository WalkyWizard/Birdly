from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config
from database import engine, Base
import models
from routers import analyze, history, birds, stats

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Birdly",
    description="Birdly API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(birds.router)
app.include_router(stats.router)

@app.get("/")
def root():
    return {
        "service": "Birdly Central Server",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.SERVER_HOST, port=config.SERVER_PORT, reload=False)
