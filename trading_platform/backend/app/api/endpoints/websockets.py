from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.connection_manager import connection_manager

router = APIRouter()

@router.websocket("/ws/pl")
async def websocket_pl_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time P/L data. Manages client connections.
    """
    await connection_manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive. Frontend sends no messages to this endpoint.
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("Client disconnected from P/L WebSocket.")
    except Exception as e:
        print(f"An error occurred in the P/L WebSocket: {e}")
    finally:
        connection_manager.disconnect(websocket)
