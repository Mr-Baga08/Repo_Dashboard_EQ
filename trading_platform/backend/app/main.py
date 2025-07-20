import threading
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import clients as client_router
from app.api.endpoints import orders as order_router
from app.api.endpoints import websockets as websocket_router
from app.api.endpoints import tokens as token_router
from app.services.live_mofsl_handler import LiveMofslHandler
from app.core.config import settings
from app.core.security import decrypt
from app.db.session import SessionLocal
from app.models.client import Client as ClientModel
from app.services.mofsl_api_service import BASE_URL # Import BASE_URL

app = FastAPI(
    title="Multi-Client Trading Platform API",
    version="1.0.0",
    description="API for managing trading clients, executing orders, and viewing portfolios via the MOFSL OpenAPI.",
    contact={
        "name": "Your Name",
        "email": "your.email@example.com",
    },
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Routers
app.include_router(client_router.router, prefix="/api/v1/clients", tags=["Clients"])
app.include_router(order_router.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(websocket_router.router, prefix="/ws", tags=["WebSockets"])
app.include_router(token_router.router, prefix="/api/v1/tokens", tags=["Tokens"])

@app.on_event("startup")
async def startup_event():
    print("Application startup: Initializing MOFSL Live Data Handler...")
    db = SessionLocal()
    try:
        # Fetch a primary client to use its credentials for the MOFSL live feed
        # In a real application, you might have a dedicated admin client or a more robust way to manage these credentials.
        primary_client = db.query(ClientModel).first() # Gets the first client in the DB

        if primary_client:
            decrypted_api_key = decrypt(primary_client.api_key_encrypted)
            decrypted_api_secret = decrypt(primary_client.api_secret_encrypted)

            # IMPORTANT: Hardcoding password and 2FA is insecure.
            # This is a placeholder for demonstration purposes.
            temp_password = "SOME_SECURE_PASSWORD"
            temp_2fa = "SOME_2FA_VALUE"

            mofsl_live_handler = LiveMofslHandler(
                api_key=decrypted_api_key,
                base_url=BASE_URL,
                client_code=primary_client.client_id,
                source_id="WEB", # Or a more appropriate source ID
                browser_name="FastAPI_Backend",
                browser_version="1.0"
            )

            # Start the MOFSL WebSocket connection in a background thread
            # The Broadcast_connect method is blocking, so it must run in a separate thread.
            threading.Thread(target=mofsl_live_handler.Broadcast_connect, daemon=True).start()
            print("MOFSL Live Data Handler started in background thread.")

            # Register for some example scrips (token codes) to receive live data
            # Replace with actual scrip codes you want to monitor
            # Example: NSE, CASH, ScripCode (e.g., 1660 for RELIANCE)
            # You might want to fetch these dynamically or from configuration
            # Give a small delay to allow the connection to establish
            await asyncio.sleep(5) 
            mofsl_live_handler.Register("NSE", "CASH", 1660) # Example scrip for RELIANCE
            mofsl_live_handler.Register("NSE", "CASH", 22) # Example scrip for another token
            print("Registered for example scrips.")
        else:
            print("No primary client found in database. MOFSL Live Data Handler not started.")
    except Exception as e:
        print(f"Error during MOFSL Live Data Handler startup: {e}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "healthy"}
