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
