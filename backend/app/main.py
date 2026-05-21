"""
AgentHub Backend - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.ws.handlers import ws_router

app = FastAPI(
    title="AgentHub API",
    description="IM-style Multi-Agent Collaboration Workstation",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API routes
app.include_router(api_router, prefix="/api/v1")

# Mount WebSocket routes
app.include_router(ws_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "agenthub-backend"}
