from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(
    prefix="/api/v1",
    tags=["WebSocket"],
)


@router.websocket("/audio")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_bytes()

            # Pour l'instant, on ne traite pas encore l'audio.
            # Cette partie sera connectée à l'Orchestrator plus tard.

            await websocket.send_json({
                "status": "received",
                "bytes": len(data),
            })

    except WebSocketDisconnect:
        print("WebSocket disconnected")