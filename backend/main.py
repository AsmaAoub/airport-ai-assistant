from fastapi import FastAPI

from app.api_gateway.routes import router as api_router
from app.api_gateway.websocket import router as websocket_router


app = FastAPI(
    title="Airport AI Assistant",
    description="Backend API for the multilingual airport conversational assistant",
    version="0.1.0",
)


app.include_router(api_router)
app.include_router(websocket_router)