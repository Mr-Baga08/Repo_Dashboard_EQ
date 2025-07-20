import json
import asyncio
import threading
from MOFSLOPENAPI import MOFSLOPENAPI
from app.websockets.connection_manager import connection_manager

class LiveMofslHandler(MOFSLOPENAPI):
    def __init__(self, api_key, base_url, client_code, source_id, browser_name, browser_version):
        super().__init__(api_key, base_url, client_code, source_id, browser_name, browser_version)

    def _Broadcast_on_message(self, ws, message_type, message):
        # The 'message' parameter is already a dictionary containing live data.
        # Convert it to a JSON string and broadcast to all connected frontend clients.
        try:
            json_message = json.dumps({"type": message_type, "data": message})
            # Use asyncio.run_coroutine_threadsafe to run the async broadcast in the main event loop
            asyncio.run_coroutine_threadsafe(connection_manager.broadcast(json_message), asyncio.get_event_loop())
        except Exception as e:
            print(f"Error broadcasting message: {e}")

# This will be instantiated in main.py
