from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import clients as client_router
from app.api.endpoints import orders as order_router
from app.api.endpoints import websockets as websocket_router

# from app.api.v1.routers import token_router

app = FastAPI(title="Trading Platform API")

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


# Placeholder for future routers
# app.include_router(token_router, prefix="/api/v1/tokens", tags=["tokens"])

@app.get("/")
def read_root():
    return {"status": "healthy"}
