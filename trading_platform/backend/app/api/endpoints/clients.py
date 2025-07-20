from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.client import Client as ClientModel
from app.schemas.client import Client, ClientCreate
from app.core.security import encrypt, decrypt
from app.services.mofsl_api_service import MofslApiService

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Client, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """
    Create a new client and store their encrypted credentials.
    """
    db_client = db.query(ClientModel).filter(ClientModel.client_id == client.client_id).first()
    if db_client:
        raise HTTPException(status_code=400, detail="Client ID already registered")

    encrypted_api_key = encrypt(client.api_key)
    encrypted_api_secret = encrypt(client.api_secret)

    new_client = ClientModel(
        client_id=client.client_id,
        name=client.name,
        api_key_encrypted=encrypted_api_key,
        api_secret_encrypted=encrypted_api_secret,
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

@router.get("/", response_model=List[Client])
def list_clients(db: Session = Depends(get_db)):
    """
    Retrieve a list of all clients.
    """
    return db.query(ClientModel).all()

@router.get("/{client_id}", response_model=Client)
def get_client_details(client_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve details for a single client by their UUID.
    """
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/{client_id}/portfolio")
def get_client_portfolio(client_id: UUID, db: Session = Depends(get_db)):
    """
    Fetch portfolio (positions and margin) for a specific client from MOFSL API.
    """
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    try:
        # This is a placeholder for fetching the real password and 2FA
        # In a real app, you'd have a secure way to get these, perhaps from a vault
        # or by prompting the user. For now, we assume they are available.
        decrypted_api_key = decrypt(client.api_key_encrypted)
        decrypted_api_secret = decrypt(client.api_secret_encrypted)
        
        # IMPORTANT: Hardcoding password and 2FA is insecure.
        # This is a placeholder for demonstration purposes.
        temp_password = "SOME_SECURE_PASSWORD"
        temp_2fa = "SOME_2FA_VALUE"

        mofsl_service = MofslApiService(
            api_key=decrypted_api_key,
            api_secret=decrypted_api_secret,
            client_id=client.client_id,
            password=temp_password,
            two_fa=temp_2fa,
        )

        positions = mofsl_service.get_positions()
        margin = mofsl_service.get_margin()

        return {"positions": positions, "margin_summary": margin}

    except HTTPException as e:
        # Re-raise HTTP exceptions from the service layer
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/{client_id}/active-trades", response_model=List[Dict[str, Any]])
async def get_client_active_trades(client_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a list of a single client's active trades (open positions).
    """
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    try:
        decrypted_api_key = decrypt(client.api_key_encrypted)
        decrypted_api_secret = decrypt(client.api_secret_encrypted)

        # IMPORTANT: Hardcoding password and 2FA is insecure.
        # This is a placeholder for demonstration purposes.
        temp_password = "SOME_SECURE_PASSWORD"
        temp_2fa = "SOME_2FA_VALUE"

        mofsl_service = MofslApiService(
            api_key=decrypted_api_key,
            api_secret=decrypted_api_secret,
            client_id=client.client_id,
            password=temp_password,
            two_fa=temp_2fa,
        )

        all_positions = mofsl_service.get_positions()
        
        active_trades = []
        if all_positions and isinstance(all_positions, dict) and "data" in all_positions:
            for position in all_positions["data"]:
                buy_quantity = position.get("buyquantity", 0)
                sell_quantity = position.get("sellquantity", 0)
                net_quantity = buy_quantity - sell_quantity

                if net_quantity != 0:
                    symbol = position.get("symbol")
                    ltp = position.get("LTP")
                    buy_amount = position.get("buyamount", 0)
                    sell_amount = position.get("sellamount", 0)

                    avg_price = 0.0
                    if net_quantity > 0 and buy_quantity > 0:
                        avg_price = buy_amount / buy_quantity
                    elif net_quantity < 0 and sell_quantity > 0:
                        avg_price = sell_amount / sell_quantity

                    active_trades.append({
                        "symbol": symbol,
                        "quantity": net_quantity,
                        "avg_price": round(avg_price, 2),
                        "ltp": ltp,
                    })
        return active_trades

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching active trades: {e}")
