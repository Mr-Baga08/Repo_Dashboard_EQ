import asyncio
import random
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/pl")
async def websocket_pl_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint to stream simulated real-time Profit/Loss data.
    """
    await websocket.accept()
    try:
        while True:
            # In a real app, this data would come from a Redis stream or a broker's feed.
            # Here, we simulate it for demonstration.
            mock_data = {
                "clientId": f"user_{random.randint(1, 10)}",
                "pnl": round(random.uniform(-500, 500), 2)
            }
            await websocket.send_json(mock_data)
            await asyncio.sleep(2)  # Simulate a 2-second interval for updates
    except WebSocketDisconnect:
        print("Client disconnected from P/L WebSocket.")
    except Exception as e:
        print(f"An error occurred in the P/L WebSocket: {e}")
