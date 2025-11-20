from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/{session_id}")
async def collaborate_ws(websocket: WebSocket, session_id: UUID) -> None:
    await websocket.accept()
    try:
        await websocket.send_json({"status": "connected", "session_id": str(session_id)})
        while True:
            message = await websocket.receive_json()
            await websocket.send_json({"echo": message, "session_id": str(session_id)})
    except WebSocketDisconnect:
        return
