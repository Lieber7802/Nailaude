"""
WebSocket endpoint handlers
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ws.manager import manager

ws_router = APIRouter()


@ws_router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """Main WebSocket endpoint for real-time messaging."""
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # TODO: route message to appropriate handler based on message.type
            await manager.send_personal(websocket, {
                "type": "echo",
                "data": message,
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
