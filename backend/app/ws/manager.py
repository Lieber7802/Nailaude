"""
WebSocket Connection Manager
"""
from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections per conversation."""

    def __init__(self):
        # conversation_id -> list of active connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.active_connections:
            if websocket in self.active_connections[conversation_id]:
                self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def broadcast(self, conversation_id: str, message: dict):
        """Send message to all connections in a conversation."""
        connections = self.active_connections.get(conversation_id, [])
        for connection in connections:
            await connection.send_json(message)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection."""
        await websocket.send_json(message)


manager = ConnectionManager()
